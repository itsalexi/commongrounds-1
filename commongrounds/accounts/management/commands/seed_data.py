from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from bookclub.models import Book, BookReview, Genre
from commissions.models import Commission, CommissionType, Job
from diyprojects.models import Project, ProjectCategory
from localevents.models import Event, EventType
from merchstore.models import Product, ProductType


class Command(BaseCommand):
    help = 'Seed Common Grounds with starter community data.'

    def handle(self, *args, **options):
        profiles = self.seed_profiles()
        self.seed_bookclub(profiles['book'])
        self.seed_events(profiles['event'])
        self.seed_products(profiles['seller'])
        self.seed_projects(profiles['project'])
        self.seed_commissions(profiles['commission'])
        self.stdout.write(self.style.SUCCESS('Seed data ready.'))

    def seed_profiles(self):
        people = {
            'seller': {
                'username': 'market_maya',
                'display_name': 'Maya Santos',
                'email': 'maya@example.com',
                'role': Profile.Role.MARKET_SELLER,
            },
            'event': {
                'username': 'events_eli',
                'display_name': 'Eli Navarro',
                'email': 'eli@example.com',
                'role': Profile.Role.EVENT_ORGANIZER,
            },
            'book': {
                'username': 'books_bea',
                'display_name': 'Bea Cruz',
                'email': 'bea@example.com',
                'role': Profile.Role.BOOK_CONTRIBUTOR,
            },
            'project': {
                'username': 'maker_mina',
                'display_name': 'Mina Reyes',
                'email': 'mina@example.com',
                'role': Profile.Role.PROJECT_CREATOR,
            },
            'commission': {
                'username': 'commissions_carlo',
                'display_name': 'Carlo Lim',
                'email': 'carlo@example.com',
                'role': Profile.Role.COMMISSION_MAKER,
            },
        }

        profiles = {}
        for key, data in people.items():
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email']},
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
            elif user.email != data['email']:
                user.email = data['email']
                user.save(update_fields=['email'])

            profile, _ = Profile.objects.update_or_create(
                user=user,
                defaults={
                    'display_name': data['display_name'],
                    'email': data['email'],
                    'role': data['role'],
                },
            )
            profiles[key] = profile
        return profiles

    def seed_bookclub(self, contributor):
        genres = {
            'Community Fiction': 'Stories about neighborhoods, found family, and everyday resilience.',
            'Practical Guides': 'Useful books for building skills, organizing, and caring for shared spaces.',
            'Food Writing': 'Essays and cookbooks centered on culture, memory, and meals.',
            'Speculative Futures': 'Hopeful fiction about better systems and future communities.',
        }
        genre_objects = {
            name: Genre.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )[0]
            for name, description in genres.items()
        }

        books = [
            ('Braiding Sweetgrass', 'Robin Wall Kimmerer', 2013, 'Practical Guides', 'A thoughtful blend of ecology, Indigenous knowledge, and care for the land.'),
            ('The Long Table', 'Harper Reyes', 2024, 'Community Fiction', 'Neighbors turn a neglected storefront into a shared supper club.'),
            ('Salt, Smoke, and Sundays', 'Mina Villanueva', 2022, 'Food Writing', 'A warm collection of recipes and essays from intergenerational kitchens.'),
            ('Pocket Neighborhoods', 'Ross Chapin', 2011, 'Practical Guides', 'Design ideas for smaller, more connected places to live.'),
            ('The City We Grow', 'Lena Park', 2025, 'Speculative Futures', 'A near-future story about mutual aid, gardens, and civic imagination.'),
        ]
        book_objects = []
        for title, author, year, genre, synopsis in books:
            book, _ = Book.objects.update_or_create(
                title=title,
                defaults={
                    'author': author,
                    'publication_year': year,
                    'synopsis': synopsis,
                    'available_to_borrow': True,
                    'genre': genre_objects[genre],
                    'contributor': contributor,
                },
            )
            book_objects.append(book)

        for book in book_objects[:3]:
            BookReview.objects.update_or_create(
                book=book,
                title=f'Why we picked {book.title}',
                defaults={
                    'user_reviewer': contributor,
                    'comment': 'A strong fit for Common Grounds readers and conversation circles.',
                },
            )

    def seed_events(self, organizer):
        event_types = {
            'Workshop': 'Hands-on sessions for learning practical community skills.',
            'Meetup': 'Low-pressure gatherings for neighbors and collaborators.',
            'Market Day': 'Local selling, swapping, tasting, and discovering.',
        }
        type_objects = {
            name: EventType.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )[0]
            for name, description in event_types.items()
        }

        now = timezone.now()
        events = [
            ('Saturday Skill Swap', 'Workshop', 'Bring one useful skill, learn two more, and meet neighbors building local projects.', 'Common Grounds Workshop Room', 5, 10, 30),
            ('Makers Morning Market', 'Market Day', 'A compact market for handmade goods, pantry staples, books, and project supplies.', 'Courtyard Pop-up Area', 9, 9, 45),
            ('Book Club: Hopeful Futures', 'Meetup', 'A guided discussion on practical optimism in fiction and community planning.', 'Reading Nook', 14, 18, 24),
            ('Repair Cafe Night', 'Workshop', 'Bring small household items and learn basic repair with volunteer fixers.', 'Tool Library Corner', 21, 17, 20),
        ]
        for title, type_name, description, location, days, hour, capacity in events:
            start = (now + timezone.timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0)
            event, _ = Event.objects.update_or_create(
                title=title,
                defaults={
                    'category': type_objects[type_name],
                    'description': description,
                    'location': location,
                    'start_time': start,
                    'end_time': start + timezone.timedelta(hours=2),
                    'event_capacity': capacity,
                    'status': Event.Status.AVAILABLE,
                },
            )
            event.organizer.set([organizer])

    def seed_products(self, owner):
        product_types = {
            'Pantry': 'Small-batch food, drinks, and shelf-stable staples.',
            'Home Goods': 'Useful handmade goods for home and shared spaces.',
            'Workshop Supplies': 'Materials for DIY projects and classes.',
        }
        type_objects = {
            name: ProductType.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )[0]
            for name, description in product_types.items()
        }

        products = [
            ('House Blend Coffee Beans', 'Pantry', 'Medium roast beans from a neighborhood micro-roaster.', '18.00', 24, Product.Status.AVAILABLE),
            ('Citrus Herb Marmalade', 'Pantry', 'Small-batch marmalade with calamansi, orange peel, and thyme.', '9.50', 18, Product.Status.ON_SALE),
            ('Linen Produce Bag Set', 'Home Goods', 'Reusable drawstring bags for market runs and pantry storage.', '14.00', 30, Product.Status.AVAILABLE),
            ('Beeswax Wrap Trio', 'Home Goods', 'Reusable wraps for bowls, snacks, and leftovers.', '12.00', 16, Product.Status.AVAILABLE),
            ('Beginner Planter Kit', 'Workshop Supplies', 'Clay pot, soil mix, seeds, and a simple care card.', '16.75', 0, Product.Status.OUT_OF_STOCK),
        ]
        for name, type_name, description, price, stock, status in products:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    'product_type': type_objects[type_name],
                    'owner': owner,
                    'description': description,
                    'price': Decimal(price),
                    'stock': stock,
                    'status': status,
                },
            )

    def seed_projects(self, creator):
        categories = {
            'Garden': 'Growing food and greenery in small shared spaces.',
            'Repair': 'Simple fixes that extend the life of everyday items.',
            'Home': 'Low-cost upgrades for comfort, storage, and reuse.',
        }
        category_objects = {
            name: ProjectCategory.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )[0]
            for name, description in categories.items()
        }

        projects = [
            ('Balcony Herb Rail', 'Garden', 'Build a narrow herb shelf for a balcony rail or sunny window.', 'Cedar strip, brackets, small pots, soil, herb seedlings', 'Measure rail width. Attach brackets. Set pots in place. Water lightly and label each herb.'),
            ('Patch a Canvas Tote', 'Repair', 'Turn a worn tote into a stronger everyday bag.', 'Fabric patch, needle, thread, pins, scissors', 'Trim loose threads. Pin the patch. Sew around the edge twice. Reinforce handles if needed.'),
            ('Jar Pantry Labels', 'Home', 'Make clean reusable labels for bulk pantry jars.', 'Jars, masking tape or label paper, marker, cloth', 'Clean jars. Cut labels evenly. Write item and date. Place labels where they are easy to scan.'),
            ('Starter Compost Bucket', 'Garden', 'Set up a simple kitchen scrap bucket for compost drop-offs.', 'Lidded bucket, charcoal filter, sticker label, small scoop', 'Wash the bucket. Add filter. Label clearly. Empty at a community compost point twice a week.'),
        ]
        for title, category, description, materials, steps in projects:
            Project.objects.update_or_create(
                title=title,
                defaults={
                    'category': category_objects[category],
                    'creator': creator,
                    'description': description,
                    'materials': materials,
                    'steps': steps,
                },
            )

    def seed_commissions(self, maker):
        commission_types = {
            'Community Help': 'Short-term requests for neighbor support.',
            'Creative Work': 'Design, writing, photo, and craft commissions.',
            'Event Support': 'Roles needed for local events and gatherings.',
        }
        type_objects = {
            name: CommissionType.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )[0]
            for name, description in commission_types.items()
        }

        commissions = [
            ('Market Day Setup Crew', 'Event Support', 'Help arrange tables, signage, and vendor check-in before the monthly market.', 6, [('Table setup', 3), ('Vendor check-in', 2), ('Signage runner', 1)]),
            ('Community Zine Cover', 'Creative Work', 'Create an inviting cover for the next Common Grounds mini-zine.', 1, [('Illustrator', 1)]),
            ('Workshop Photo Volunteer', 'Event Support', 'Document the next repair cafe with candid photos for the community board.', 2, [('Photographer', 1), ('Photo assistant', 1)]),
            ('Pantry Shelf Build', 'Community Help', 'Assemble simple shelving for the shared pantry corner.', 4, [('Builder', 2), ('Painter', 2)]),
        ]
        for title, type_name, description, people_required, jobs in commissions:
            commission, _ = Commission.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'commission_type': type_objects[type_name],
                    'maker': maker,
                    'num_of_people_required': people_required,
                    'status': Commission.Status.OPEN,
                },
            )
            for role, manpower in jobs:
                Job.objects.update_or_create(
                    commission=commission,
                    role=role,
                    defaults={
                        'manpower_required': manpower,
                        'status': Job.Status.OPEN,
                    },
                )
