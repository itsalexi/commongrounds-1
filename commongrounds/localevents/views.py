from django.shortcuts import render
from .models import Event

# Create your views here.


def event_list(request):
    events = Event.objects.all()

    ctx = {
        'events': events
    }

    return render(request, './events/event_list.html', ctx)


def event_detail(request, pk):
    event = Event.objects.get(pk=pk)
    ctx = {
        'event': event
    }

    return render(request, './events/event_detail.html', ctx)
