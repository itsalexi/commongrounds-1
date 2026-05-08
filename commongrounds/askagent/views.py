import json

from django.http import HttpResponseForbidden
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse

from .agent import ChatbotError, ask_agentic_chatbot, stream_agentic_chatbot


def ask(request):
    question = ''
    answer = ''
    error = ''
    tool_events = []

    if request.method == 'POST':
        if not request.user.is_authenticated:
            error = 'Log in first to chat with Groundie.'
            return render(request, 'askagent/ask.html', {
                'question': question,
                'answer': answer,
                'error': error,
                'tool_events': tool_events,
            }, status=403)

        question = request.POST.get('question', '').strip()
        if question:
            try:
                answer, tool_events = ask_agentic_chatbot(
                    question,
                    request.build_absolute_uri('/'),
                    request.user,
                )
            except ChatbotError as exc:
                error = str(exc)
        else:
            error = 'Ask a question so Groundie has something to look up.'

    return render(request, 'askagent/ask.html', {
        'question': question,
        'answer': answer,
        'error': error,
        'tool_events': tool_events,
    })


def stream(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            return HttpResponseForbidden(json.dumps({
                'type': 'auth_required',
                'message': 'Log in first to chat with Groundie.',
                'login_url': reverse('login'),
            }), content_type='application/json')

    payload = stream_payload(request)
    question = payload.get('question', '').strip()
    history = payload.get('history', [])

    def events():
        if not request.user.is_authenticated:
            yield sse_message({
                'type': 'auth_required',
                'message': 'Log in first to chat with Groundie.',
                'login_url': reverse('login'),
            })
            return

        if not question:
            yield sse_message({
                'type': 'error',
                'message': 'Ask a question so Groundie has something to look up.',
            })
            return

        try:
            for event in stream_agentic_chatbot(
                question,
                request.build_absolute_uri('/'),
                request.user,
                history=history,
            ):
                yield sse_message(event)
        except ChatbotError as exc:
            yield sse_message({'type': 'error', 'message': str(exc)})

    response = StreamingHttpResponse(events(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def stream_payload(request):
    if request.method == 'POST':
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return {}
    return {
        'question': request.GET.get('question', ''),
        'history': [],
    }


def sse_message(payload):
    return f'data: {json.dumps(payload)}\n\n'
