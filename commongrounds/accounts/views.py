from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileUpdateForm
from .models import Profile


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        Profile.objects.create(user=user, display_name=user.username, email='')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_update(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('accounts:profile_update', username=username)
    return render(request, 'accounts/profile_update.html', {'form': form})
