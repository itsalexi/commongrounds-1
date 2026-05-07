from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileUpdateForm, RegistrationForm
from .models import Profile


def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        Profile.objects.create(
            user=user,
            display_name=user.username,
            email=user.email,
            role=form.cleaned_data['role'],
        )
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_update(request, username):
    if request.user.username != username:
        raise PermissionDenied

    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('accounts:profile_update', username=username)
    return render(request, 'accounts/profile_update.html', {'form': form})
