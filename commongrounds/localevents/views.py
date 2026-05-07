from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from accounts.decorators import role_required
from .forms import EventForm, EventSignupForm
from .models import Event, EventSignup


def event_list(request):
    events = (
        Event.objects.select_related('category')
        .prefetch_related('organizer', 'signups')
        .order_by('start_time')
    )
    created_events = Event.objects.none()
    signed_up_events = Event.objects.none()
    all_events = events
    profile = None

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Exception:
            profile = None

        if profile:
            created_events = events.filter(organizer=profile)
            signed_up_events = (
                events.filter(signups__user_registrant=profile)
                .exclude(organizer=profile)
                .distinct()
            )
            all_events = (
                events.exclude(pk__in=created_events.values('pk'))
                .exclude(pk__in=signed_up_events.values('pk'))
            )

    ctx = {
        'created_events': created_events,
        'signed_up_events': signed_up_events,
        'all_events': all_events,
        'can_create_event': (
            profile is not None
            and profile.role == 'Event Organizer'
        ),
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


class BaseSignupView(View):

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        return render(request, 'events/event_signup.html', {
            'event': event,
            'form': EventSignupForm(),
        })

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])

        if not self.check_capacity(event):
            return redirect(self.get_redirect_url(event))

        if not self.check_ownership(event, request.user):
            return redirect(self.get_redirect_url(event))

        self.create_signup(event, request.user)
        return redirect(self.get_redirect_url(event))

    def check_capacity(self, event):
        raise NotImplementedError

    def check_ownership(self, event, user):
        raise NotImplementedError

    def create_signup(self, event, user):
        raise NotImplementedError

    def get_redirect_url(self, event):
        raise NotImplementedError


class EventSignupView(BaseSignupView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            event = get_object_or_404(Event, pk=kwargs['pk'])
            form = EventSignupForm(request.POST)
            if not form.is_valid():
                return render(request, 'events/event_signup.html', {
                    'event': event,
                    'form': form,
                })
        return super().post(request, *args, **kwargs)

    def check_capacity(self, event):
        return event.signups.count() < event.event_capacity

    def check_ownership(self, event, user):
        if not user.is_authenticated:
            return True
        return not event.organizer.filter(pk=user.profile.pk).exists()

    def create_signup(self, event, user):
        if user.is_authenticated:
            EventSignup.objects.get_or_create(event=event, user_registrant=user.profile)
        else:
            form = EventSignupForm(self.request.POST)
            if form.is_valid():
                EventSignup.objects.create(
                    event=event,
                    new_registrant=form.cleaned_data['name'],
                )

    def get_redirect_url(self, event):
        return reverse('localevents:event_detail', args=[event.pk])
