from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm, StudentLoginForm, UserProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Murakaza neza, {user.display_name}! Konti yanyu yafunguwe neza. (Welcome! Your account was created successfully.)"
            )
            return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, "Hari amakosa yabayeho. Reba amakuru winjije. (Please check the form for errors.)")
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:student_dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Murakaza neza, {user.display_name}!")
            next_url = request.GET.get('next', 'dashboard:student_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Izina cyangwa ijambo ry'ibanga ntabwo bihuye. (Invalid username or password.)")
    else:
        form = StudentLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Muvuye muri sisitemu neza. (You have been logged out safely.)")
    return redirect('core:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Umwirondoro wanyu wavuguruwe neza! (Profile updated successfully!)")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})

