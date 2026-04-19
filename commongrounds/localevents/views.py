from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import role_required
from .forms import EventForm, EventSignupForm
from .models import Event, EventSignup


def event_list(request):
    ctx = {'all_events': Event.objects.all()}

    if request.user.is_authenticated:
        profile = request.user.profile
        created = Event.objects.filter(organizer=profile)
        signed_up = Event.objects.filter(signups__user_registrant=profile)
        ctx = {
            'created_events': created,
            'signed_up_events': signed_up,
            'all_events': Event.objects.exclude(pk__in=(created | signed_up)),
        }

    return render(request, 'events/event_list.html', ctx)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    signup_count = event.signups.count()
    is_full = signup_count >= event.event_capacity
    is_organizer = (
        request.user.is_authenticated
        and event.organizer.filter(pk=request.user.profile.pk).exists()
    )
    already_signed_up = (
        request.user.is_authenticated
        and EventSignup.objects.filter(event=event, user_registrant=request.user.profile).exists()
    )

    ctx = {
        'event': event,
        'is_full': is_full,
        'is_organizer': is_organizer,
        'already_signed_up': already_signed_up,
        'signup_count': signup_count,
    }
    return render(request, 'events/event_detail.html', ctx)


@role_required('Event Organizer')
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            form.save_m2m()
            event.organizer.set([request.user.profile])
            return redirect('localevents:event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'events/event_create.html', {'form': form})


@role_required('Event Organizer')
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated = form.save(commit=False)
            signup_count = updated.signups.count()
            if signup_count >= updated.event_capacity:
                updated.status = Event.Status.FULL
            else:
                updated.status = Event.Status.AVAILABLE
            updated.save()
            form.save_m2m()
            return redirect('localevents:event_detail', pk=updated.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_update.html', {'form': form, 'event': event})


def event_signup(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user.is_authenticated:
        profile = request.user.profile
        if not EventSignup.objects.filter(event=event, user_registrant=profile).exists():
            EventSignup.objects.create(event=event, user_registrant=profile)
        return redirect('localevents:event_detail', pk=pk)

    if request.method == 'POST':
        form = EventSignupForm(request.POST)
        if form.is_valid():
            EventSignup.objects.create(
                event=event,
                new_registrant=form.cleaned_data['name'],
            )
            return redirect('localevents:event_detail', pk=pk)
    else:
        form = EventSignupForm()

    return render(request, 'events/event_signup.html', {'event': event, 'form': form})
