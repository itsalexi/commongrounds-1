import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import Profile
from bookclub.models import Book, Bookmark, Borrow
from commissions.models import Commission, Job
from commissions.services import CommissionService
from diyprojects.models import Favorite, Project
from localevents.models import Event, EventSignup
from merchstore.models import Product, Transaction


OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
MAX_TOOL_STEPS = 3
MAX_RESULTS = 5
PRODUCT_AVAILABILITY_TERMS = {'available', 'buy', 'buyable', 'sale', 'sell', 'selling'}
PRODUCT_QUERY_FILLER_TERMS = PRODUCT_AVAILABILITY_TERMS | {
    'for',
    'item',
    'items',
    'merch',
    'product',
    'products',
    'shop',
    'show',
    'store',
}

SYSTEM_PROMPT = (
    'You are Groundie, the helpful Common Grounds assistant. Be warm, direct, '
    'and personal without being wordy. Use database tools before answering '
    'questions about site records, the user cart, or user actions. Pick the '
    'most relevant tool or call multiple tools when the question spans apps. '
    'Pass a short content search query; pass an empty string only when the user '
    'asks to list a whole section. For products "for sale", search for '
    '"available". For cart questions, use view_cart. You may use write tools '
    'only when the user explicitly asks to take that action. Write tools are '
    'limited to normal user actions like cart, bookmark, borrow, favorite, '
    'event signup, and job application. When adding a product to cart, prefer '
    'the product name from the user wording unless a product id is certain. '
    'When asked what you can do, mention that you can search Common Grounds, '
    'check the cart, and take those allowed user actions. Answer only from '
    'tool results.'
)


def ask_agentic_chatbot(question, site_url, user, history=None):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        *chat_history(history),
        {'role': 'user', 'content': question},
    ]
    tool_events = []

    for _ in range(MAX_TOOL_STEPS):
        message = call_openrouter(messages, site_url)
        tool_calls = message.get('tool_calls') or []
        messages.append(assistant_message(message, tool_calls))

        if not tool_calls:
            return (message.get('content') or '').strip(), tool_events

        for tool_call in tool_calls:
            tool_message, event = run_tool_call(tool_call, user)
            messages.append(tool_message)
            tool_events.append(event)

    raise ChatbotError('The chatbot needed too many lookup steps.')


def stream_agentic_chatbot(question, site_url, user, history=None):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        *chat_history(history),
        {'role': 'user', 'content': question},
    ]

    yield {'type': 'status', 'message': 'Thinking'}

    for _ in range(MAX_TOOL_STEPS):
        message = call_openrouter(messages, site_url)
        tool_calls = message.get('tool_calls') or []
        messages.append(assistant_message(message, tool_calls))

        if not tool_calls:
            yield {
                'type': 'answer',
                'message': (message.get('content') or '').strip(),
            }
            return

        for tool_call in tool_calls:
            yield tool_started_event(tool_call)
            tool_message, event = run_tool_call(tool_call, user)
            messages.append(tool_message)
            yield {'type': 'tool_done', 'event': event}

        yield {'type': 'status', 'message': 'Reading results'}

    raise ChatbotError('The chatbot needed too many lookup steps.')


def chat_history(history):
    messages = []
    for message in history or []:
        role = message.get('role')
        content = str(message.get('content') or '').strip()
        if role in ('user', 'assistant') and content:
            messages.append({'role': role, 'content': content})
    return messages[-10:]


def call_openrouter(messages, site_url):
    if not settings.OPENROUTER_API_KEY:
        raise ChatbotError('OPENROUTER_API_KEY is not configured.')

    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps({
            'model': settings.OPENROUTER_MODEL,
            'messages': messages,
            'tools': database_tools(),
            'tool_choice': 'auto',
            'parallel_tool_calls': True,
            'temperature': 0.2,
            'max_tokens': 500,
        }).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': site_url,
            'X-OpenRouter-Title': 'Groundie',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['choices'][0]['message']
    except urllib.error.HTTPError as exc:
        raise ChatbotError(f'OpenRouter request failed with status {exc.code}.')
    except urllib.error.URLError:
        raise ChatbotError('OpenRouter could not be reached. Try again later.')
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        raise ChatbotError('OpenRouter did not return a usable answer.')


def database_tools():
    return [
        tool_schema(name, config['tool_description'])
        for name, config in TOOL_CONFIGS.items()
    ] + [
        action_tool_schema(name, config)
        for name, config in ACTION_TOOL_CONFIGS.items()
    ]


def tool_schema(name, description):
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': description,
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Short content search query. Use empty string to list records.',
                    },
                },
                'required': ['query'],
            },
        },
    }


def action_tool_schema(name, config):
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': config['tool_description'],
            'parameters': config['parameters'],
        },
    }


def assistant_message(message, tool_calls):
    result = {'role': 'assistant', 'content': message.get('content')}
    if tool_calls:
        result['tool_calls'] = tool_calls
    return result


def run_tool_call(tool_call, user):
    function = tool_call.get('function', {})
    tool_name = function.get('name')
    args = parse_json(function.get('arguments'))
    query = args.get('query', '')

    if tool_name in TOOL_CONFIGS:
        results = search_records(TOOL_CONFIGS[tool_name], query)
        content = {'results': results}
        event = {
            'label': TOOL_CONFIGS[tool_name]['label'],
            'query': query or 'List records',
            'result_count': len(results),
            'status': 'completed',
        }
    elif tool_name in ACTION_TOOL_CONFIGS:
        content = run_write_action(tool_name, args, user)
        event = {
            'label': ACTION_TOOL_CONFIGS[tool_name]['label'],
            'query': content.get('message', 'Action completed'),
            'result_count': 0,
            'status': 'completed' if content.get('ok') else 'failed',
            'message': content.get('message', ''),
        }
    else:
        content = {'ok': False, 'message': 'Unknown tool.'}
        event = {
            'label': 'Unknown tool',
            'query': query,
            'result_count': 0,
            'status': 'failed',
            'message': 'Unknown tool.',
        }

    return {
        'role': 'tool',
        'tool_call_id': tool_call.get('id'),
        'content': json.dumps(content),
    }, event


def tool_started_event(tool_call):
    function = tool_call.get('function', {})
    tool_name = function.get('name')
    query = parse_json(function.get('arguments')).get('query', '')
    config = TOOL_CONFIGS.get(tool_name) or ACTION_TOOL_CONFIGS.get(tool_name, {})
    label = config.get('start_label') or config.get('label', 'Using tool').replace('Searched', 'Searching')

    return {
        'type': 'tool_start',
        'event': {
            'label': label,
            'query': query or config.get('start_message', 'Working'),
            'status': 'running',
        },
    }


def parse_json(value):
    try:
        return json.loads(value or '{}')
    except json.JSONDecodeError:
        return {}


def search_records(config, query):
    queryset = config['queryset']()
    terms = search_terms(query)

    if config.get('available_products') and is_product_availability_query(terms):
        queryset = queryset.filter(
            stock__gt=0,
            status__in=[Product.Status.AVAILABLE, Product.Status.ON_SALE],
        )
        terms = [term for term in terms if term not in PRODUCT_QUERY_FILLER_TERMS]

    if terms:
        filtered = apply_text_search(queryset, terms, config['search_fields'])
        queryset = filtered if filtered.exists() else queryset

    if config.get('order_by'):
        queryset = queryset.order_by(*config['order_by'])

    return [
        serialize_record(record, config)
        for record in queryset.distinct()[:MAX_RESULTS]
    ]


def run_write_action(tool_name, args, user):
    try:
        return ACTION_TOOL_CONFIGS[tool_name]['handler'](args, user)
    except (Product.DoesNotExist, Book.DoesNotExist, Project.DoesNotExist,
            Event.DoesNotExist, Job.DoesNotExist):
        return {'ok': False, 'message': 'I could not find that record.'}
    except (TypeError, ValueError) as exc:
        return {'ok': False, 'message': str(exc)}


def add_product_to_cart(args, user):
    profile = require_profile(user)
    product = resolve_product(args)
    amount = max(1, int(args.get('amount') or 1))

    if product.owner_id == profile.id:
        return {'ok': False, 'message': 'You cannot add your own product to your cart.'}
    if product.stock < amount:
        return {'ok': False, 'message': f'Only {product.stock} item(s) are in stock.'}

    transaction = Transaction.objects.create(
        buyer=profile,
        product=product,
        amount=amount,
        status=Transaction.Status.ON_CART,
    )
    return {
        'ok': True,
        'message': f'Added {amount} x {product.name} to your cart.',
        'transaction_id': transaction.pk,
        'url': '/merchstore/cart',
    }


def view_cart(args, user):
    profile = require_profile(user)
    transactions = Transaction.objects.select_related(
        'product',
        'product__owner',
    ).filter(
        buyer=profile,
        status=Transaction.Status.ON_CART,
    ).order_by('product__owner__display_name', 'product__name', '-created_on')

    items = []
    total = 0
    for transaction in transactions:
        product = transaction.product
        if not product:
            continue
        line_total = product.price * transaction.amount
        total += line_total
        items.append({
            'transaction_id': transaction.pk,
            'product_id': product.pk,
            'product': product.name,
            'seller': product.owner.display_name if product.owner else 'Unknown seller',
            'amount': transaction.amount,
            'unit_price': str(product.price),
            'line_total': str(line_total),
            'url': product.get_absolute_url(),
        })

    if not items:
        return {
            'ok': True,
            'message': 'Your cart is empty.',
            'items': [],
            'total': '0.00',
            'url': '/merchstore/cart',
        }

    return {
        'ok': True,
        'message': f'Your cart has {len(items)} item type(s), totaling {total:.2f}.',
        'items': items,
        'total': str(total),
        'url': '/merchstore/cart',
    }


def resolve_product(args):
    product_name = (args.get('product_name') or args.get('query') or '').strip()
    product_id = args.get('product_id')
    if product_id not in (None, '') and not product_name:
        return Product.objects.get(pk=int(product_id))

    if not product_name:
        raise ValueError('Which product should I add?')

    exact_match = Product.objects.filter(name__iexact=product_name).first()
    if exact_match:
        return exact_match

    contains_matches = Product.objects.filter(name__icontains=product_name)
    count = contains_matches.count()
    if count == 1:
        return contains_matches.first()
    if count > 1:
        options = ', '.join(contains_matches.values_list('name', flat=True)[:3])
        raise ValueError(f'I found multiple matching products: {options}. Which one?')

    term_matches = Product.objects.all()
    for term in search_terms(product_name):
        term_matches = term_matches.filter(name__icontains=term)

    count = term_matches.count()
    if count == 1:
        return term_matches.first()
    if count > 1:
        options = ', '.join(term_matches.values_list('name', flat=True)[:3])
        raise ValueError(f'I found multiple matching products: {options}. Which one?')

    raise Product.DoesNotExist


def bookmark_book(args, user):
    profile = require_profile(user)
    book = Book.objects.get(pk=int(args.get('book_id')))
    _, created = Bookmark.objects.get_or_create(
        profile=profile,
        book=book,
        defaults={'date_bookmarked': timezone.localdate()},
    )
    action = 'Bookmarked' if created else 'Already bookmarked'
    return {
        'ok': True,
        'message': f'{action}: {book.title}.',
        'url': book.get_absolute_url(),
    }


def borrow_book(args, user):
    book = Book.objects.get(pk=int(args.get('book_id')))
    if not book.available_to_borrow:
        return {'ok': False, 'message': f'{book.title} is not available to borrow.'}

    profile = profile_for(user)
    name = (args.get('name') or '').strip()
    borrowed_on = parse_date(args.get('date_borrowed')) or timezone.localdate()
    due_on = borrowed_on + timedelta(days=14)

    if profile:
        borrower_name = profile.display_name
    elif name:
        borrower_name = name
    else:
        return {'ok': False, 'message': 'A name is required to borrow while logged out.'}

    Borrow.objects.create(
        book=book,
        borrower=profile,
        name=borrower_name,
        date_borrowed=borrowed_on,
        date_to_return=due_on,
    )
    book.available_to_borrow = False
    book.save(update_fields=['available_to_borrow', 'updated_on'])
    return {
        'ok': True,
        'message': f'Borrowed {book.title}. Return date is {due_on:%b %d, %Y}.',
        'url': book.get_absolute_url(),
    }


def favorite_project(args, user):
    profile = require_profile(user)
    project = Project.objects.get(pk=int(args.get('project_id')))
    status = args.get('project_status') or Favorite.Status.BACKLOG
    valid_statuses = {choice[0] for choice in Favorite.Status.choices}
    if status not in valid_statuses:
        status = Favorite.Status.BACKLOG

    favorite, created = Favorite.objects.get_or_create(
        project=project,
        profile=profile,
        defaults={'project_status': status},
    )
    if not created:
        favorite.project_status = status
        favorite.save(update_fields=['project_status'])
    return {
        'ok': True,
        'message': f'Saved {project.title} as {favorite.project_status}.',
        'url': project.get_absolute_url(),
    }


def sign_up_for_event(args, user):
    event = Event.objects.get(pk=int(args.get('event_id')))
    if event.signups.count() >= event.event_capacity:
        return {'ok': False, 'message': f'{event.title} is already full.'}

    profile = profile_for(user)
    if profile and event.organizer.filter(pk=profile.pk).exists():
        return {'ok': False, 'message': 'You cannot sign up for your own event.'}

    if profile:
        _, created = EventSignup.objects.get_or_create(
            event=event,
            user_registrant=profile,
        )
        message = 'Signed up' if created else 'You are already signed up'
    else:
        name = (args.get('name') or '').strip()
        if not name:
            return {'ok': False, 'message': 'A name is required to sign up while logged out.'}
        EventSignup.objects.create(event=event, new_registrant=name)
        message = 'Signed up'

    return {
        'ok': True,
        'message': f'{message}: {event.title}.',
        'url': event.get_absolute_url(),
    }


def apply_to_job(args, user):
    profile = require_profile(user)
    job = Job.objects.select_related('commission').get(pk=int(args.get('job_id')))
    CommissionService.apply_to_job(applicant=profile, job=job)
    return {
        'ok': True,
        'message': f'Applied to {job.role} for {job.commission.title}.',
        'url': job.commission.get_absolute_url(),
    }


def require_profile(user):
    profile = profile_for(user)
    if not profile:
        raise ValueError('You need to be logged in for that action.')
    return profile


def profile_for(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def apply_text_search(queryset, terms, fields):
    query = Q()
    for term in terms:
        for field in fields:
            query |= Q(**{f'{field}__icontains': term})
    return queryset.filter(query)


def search_terms(query):
    return [
        ''.join(char for char in word if char.isalnum())
        for word in query.lower().replace('/', ' ').replace('-', ' ').split()
        if ''.join(char for char in word if char.isalnum())
    ][:8]


def is_product_availability_query(terms):
    return bool(PRODUCT_AVAILABILITY_TERMS & set(terms))


def serialize_record(record, config):
    return {
        'id': record.pk,
        'section': config['section'],
        'title': value_for(record, config['title']),
        'meta': '; '.join(
            str(value_for(record, field))
            for field in config['meta']
            if value_for(record, field) not in ('', None)
        ),
        'description': truncate(value_for(record, config['description_field'])),
        'url': record.get_absolute_url(),
    }


def value_for(record, path):
    value = record
    for part in path.split('__'):
        value = getattr(value, part, '')
        if value is None:
            return ''
    return value


def truncate(value, length=180):
    text = ' '.join(str(value or '').split())
    if len(text) <= length:
        return text
    return f'{text[:length].rstrip()}...'


TOOL_CONFIGS = {
    'search_shop': {
        'label': 'Searched shop',
        'tool_description': 'Search merch store products. Use query "available" when the user asks for products for sale.',
        'section': 'Shop',
        'queryset': lambda: Product.objects.select_related('product_type'),
        'search_fields': ('name', 'description', 'status', 'product_type__name'),
        'title': 'name',
        'meta': ('product_type__name', 'status', 'price', 'stock'),
        'description_field': 'description',
        'available_products': True,
    },
    'search_events': {
        'label': 'Searched events',
        'tool_description': 'Search local events.',
        'section': 'Events',
        'queryset': lambda: Event.objects.select_related('category').annotate(
            signup_count=Count('signups')
        ),
        'search_fields': ('title', 'description', 'location', 'status', 'category__name'),
        'title': 'title',
        'meta': ('category__name', 'status', 'location', 'start_time', 'signup_count'),
        'description_field': 'description',
        'order_by': ('start_time',),
    },
    'search_books': {
        'label': 'Searched book club',
        'tool_description': 'Search book club books.',
        'section': 'Book Club',
        'queryset': lambda: Book.objects.select_related('genre'),
        'search_fields': ('title', 'author', 'synopsis', 'genre__name'),
        'title': 'title',
        'meta': ('genre__name', 'author', 'publication_year', 'available_to_borrow'),
        'description_field': 'synopsis',
    },
    'search_projects': {
        'label': 'Searched DIY projects',
        'tool_description': 'Search DIY projects.',
        'section': 'DIY Projects',
        'queryset': lambda: Project.objects.select_related('category'),
        'search_fields': ('title', 'description', 'materials', 'steps', 'category__name'),
        'title': 'title',
        'meta': ('category__name',),
        'description_field': 'description',
    },
    'search_gigs': {
        'label': 'Searched gigs',
        'tool_description': 'Search commission gigs.',
        'section': 'Gigs',
        'queryset': lambda: Commission.objects.select_related('commission_type'),
        'search_fields': ('title', 'description', 'status', 'commission_type__name'),
        'title': 'title',
        'meta': ('commission_type__name', 'status', 'num_of_people_required'),
        'description_field': 'description',
    },
}


ACTION_TOOL_CONFIGS = {
    'add_product_to_cart': {
        'label': 'Added to cart',
        'start_label': 'Adding to cart',
        'start_message': 'Adding product to cart',
        'tool_description': 'Add a merch store product to the current user cart. Prefer product_name from the user request; use product_id only when certain.',
        'handler': add_product_to_cart,
        'parameters': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'product_name': {'type': 'string'},
                'amount': {'type': 'integer', 'default': 1},
            },
        },
    },
    'view_cart': {
        'label': 'Checked cart',
        'start_label': 'Checking cart',
        'start_message': 'Checking your cart',
        'tool_description': 'View the current logged-in user cart contents.',
        'handler': view_cart,
        'parameters': {
            'type': 'object',
            'properties': {},
        },
    },
    'bookmark_book': {
        'label': 'Bookmarked book',
        'start_label': 'Bookmarking book',
        'start_message': 'Bookmarking book',
        'tool_description': 'Bookmark a book for the current logged-in user.',
        'handler': bookmark_book,
        'parameters': {
            'type': 'object',
            'properties': {
                'book_id': {'type': 'integer'},
            },
            'required': ['book_id'],
        },
    },
    'borrow_book': {
        'label': 'Borrowed book',
        'start_label': 'Borrowing book',
        'start_message': 'Borrowing book',
        'tool_description': 'Borrow an available book. Logged-out users must provide a name.',
        'handler': borrow_book,
        'parameters': {
            'type': 'object',
            'properties': {
                'book_id': {'type': 'integer'},
                'date_borrowed': {
                    'type': 'string',
                    'description': 'Optional YYYY-MM-DD borrow date.',
                },
                'name': {
                    'type': 'string',
                    'description': 'Required only when the user is logged out.',
                },
            },
            'required': ['book_id'],
        },
    },
    'favorite_project': {
        'label': 'Saved project',
        'start_label': 'Saving project',
        'start_message': 'Saving project',
        'tool_description': 'Favorite a DIY project for the current logged-in user.',
        'handler': favorite_project,
        'parameters': {
            'type': 'object',
            'properties': {
                'project_id': {'type': 'integer'},
                'project_status': {
                    'type': 'string',
                    'enum': ['Backlog', 'To-Do', 'Done'],
                    'default': 'Backlog',
                },
            },
            'required': ['project_id'],
        },
    },
    'sign_up_for_event': {
        'label': 'Signed up for event',
        'start_label': 'Signing up for event',
        'start_message': 'Signing up for event',
        'tool_description': 'Sign up for a local event if capacity allows.',
        'handler': sign_up_for_event,
        'parameters': {
            'type': 'object',
            'properties': {
                'event_id': {'type': 'integer'},
                'name': {
                    'type': 'string',
                    'description': 'Required only when the user is logged out.',
                },
            },
            'required': ['event_id'],
        },
    },
    'apply_to_job': {
        'label': 'Applied to job',
        'start_label': 'Applying to job',
        'start_message': 'Applying to job',
        'tool_description': 'Apply the current logged-in user to a commission job.',
        'handler': apply_to_job,
        'parameters': {
            'type': 'object',
            'properties': {
                'job_id': {'type': 'integer'},
            },
            'required': ['job_id'],
        },
    },
}


class ChatbotError(Exception):
    pass
