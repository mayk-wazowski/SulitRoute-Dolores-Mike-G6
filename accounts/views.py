from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import Profile


def get_profile(user):
    """Return the user's profile, creating one if missing (e.g. superuser)."""
    default_role = 'admin' if user.is_superuser else 'shopper'
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': default_role})
    return profile


def role_required(role):
    """Only allow users with the given role to open a page."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if get_profile(request.user).role != role:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role='shopper')
            login(request, user)
            messages.success(request, 'Account created. Welcome to SulitRoute!')
            return redirect('accounts:dashboard')
        messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    if get_profile(request.user).role == 'admin':
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:shopper_dashboard')


@role_required('shopper')
def shopper_dashboard(request):
    return render(request, 'accounts/shopper_dashboard.html')


@role_required('admin')
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')


@login_required
def profile(request):
    """Users can only see and edit their own profile."""
    prof = get_profile(request.user)
    return render(request, 'accounts/profile.html', {'prof': prof})


@login_required
def profile_edit(request):
    prof = get_profile(request.user)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=prof)
    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('accounts:profile')
        messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })