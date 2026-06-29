from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseForbidden


from .models import CustomUser, UserProfile


def login(request):
    if request.user.is_authenticated:
        return redirect('redirect_to_own_profile')
    if(request.method == 'POST'):
        data = request.POST
        form = AuthenticationForm(request, data=data)
        if form.is_valid():
            # Retrieve the authenticated user object from the form
            user = form.get_user()
            auth_login(request, user)

            return redirect(f"/profile/{user.pk}", pk=user.pk)
    else:
        # If it is a get request
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].help_text = (
            "<span class='text-green-500'>• Your custom header text:</span><br> "
            "<span class='text-green-500'>• Must be 8 characters long.</span><br>"
        )
        # Injects Tailwind classes automatically into your form elements
        tailwind_classes = (
            "w-full px-4 py-3 rounded-xl border border-gray-300 bg-white "
            "text-sm transition-all focus:outline-none focus:border-indigo-500 "
            "focus:ring-4 focus:ring-indigo-500/15"
        )
        for field in self.fields.values():
            field.widget.attrs.update({'class': tailwind_classes})

def register(request):
    if request.user.is_authenticated:
        return redirect('redirect_to_own_profile')
    if request.method == 'POST':
        # Use our newly defined custom form to catch the data
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            # Redirecting using the URL pattern name 'profile'
            return redirect('profile', pk=user.pk)
    else:
        # Handles the initial GET request cleanly
        form = CustomUserCreationForm()

        # This sits completely outside the if/else blocks.
        # It renders the blank GET form AND keeps validation errors visible on bad POSTs.
    return render(request, 'users/register.html', {'form': form})

def redirect_to_own_profile(request):
    """Intercepts static requests and forwards users to their personal dynamic ID url"""
    return redirect('profile', pk=request.user.pk)
@login_required
def profile(request, pk):
    # 1. Fetch the user matching the ID in the URL
    target_user = get_object_or_404(CustomUser, pk=pk)

    # 2. Grab their corresponding profile/bio information
    profile_data, created = UserProfile.objects.get_or_create(user=target_user)

    # 3. CRITICAL: Package your data as top-level keys
    context = {
        'target_user': target_user,
        'profile': profile_data,
        'is_own_profile': (request.user == target_user)
    }

    # 4. CRITICAL: Pass the context directly! Do NOT wrap it in another dictionary like {'context': context}
    return render(request, 'users/profile.html', context)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This keeps the styling clean but locks the input field completely
        self.fields['email'].widget.attrs['readonly'] = True
        # Optional: Add Tailwind classes to make it visually clear it's locked
        self.fields['email'].widget.attrs['class'] = 'bg-gray-100 cursor-not-allowed text-gray-500'

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_bio', 'profile_photo_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': "w-full px-4 py-3 rounded-xl border border-gray-300 bg-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/15"})

@ login_required
def edit_profile(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)

    # Security Check: Prevent users from editing profiles that aren't theirs
    if request.user != target_user:
        return HttpResponseForbidden("You are not authorized to edit this profile.")

    profile_instance, created = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        print(request.user)
        # Bind incoming data to the existing database instances
        user_form = UserUpdateForm(request.POST, instance=target_user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', pk=target_user.pk)
    else:
        # Pre-populate forms with existing database data
        user_form = UserUpdateForm(instance=target_user)
        profile_form = ProfileUpdateForm(instance=profile_instance)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'target_user': target_user
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def logout(request):
    # This completely flushes the user's browser session data
    auth_logout(request)

    # Send them back to the login page (or homepage '/') after logging out
    return redirect('login')
