from django.shortcuts import render
from localevents.models import Event
from bookclub.models import Book
from commissions.models import Commission


def landing(request):
    ctx = {
        'upcoming_events': Event.objects.order_by('start_time')[:3],
        'current_book': Book.objects.first(),
        'gigs': Commission.objects.order_by('-created_on')[:4],
    }
    return render(request, 'landing.html', ctx)
