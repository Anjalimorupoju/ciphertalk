from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm
from .models import UserProfile



def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the user in after registration
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('chat:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Register - CipherTalk'
    }
    return render(request, 'users/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Update online status
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.online_status = True
            profile.save()
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_url = request.GET.get('next', 'chat:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Login - CipherTalk'
    }
    return render(request, 'users/login.html', context)


@login_required
def logout_view(request):
    # Update online status before logout
    try:
        profile = request.user.profile
        profile.online_status = False
        profile.save()
    except UserProfile.DoesNotExist:
        pass
    
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    
    context = {
        'user': user,
        'profile': profile,
        'title': f'Profile - {user.username}'
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Edit Profile - CipherTalk'
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def security_settings_view(request):
    context = {
        'title': 'Security Settings - CipherTalk'
    }
    return render(request, 'users/security.html', context)