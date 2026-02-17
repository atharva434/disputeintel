from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm

def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('customer_dashboard')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})
