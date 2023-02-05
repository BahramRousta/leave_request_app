from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from .forms import LoginForm


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {"form": form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
    return redirect('accounts:login')
