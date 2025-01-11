from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib import auth
# Create your views here.
def home(request):
    return render(request, 'page/home.html')
def register(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['pw1']
        password2 = request.POST['pw2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email is already taken')
                    redirect('register')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, 'User created')
                    return redirect('home')
        else:
            messages.info(request, 'Password not matching')
            return redirect('register')
    return render(request, 'page/register.html')
def login(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['name']
        password = request.POST['pw']
        user = User.objects.filter(username=username)
        if user.exists():
            if user[0].check_password(password):
                auth.login(request, user[0])
                messages.success(request, 'Login successful')
                return redirect('home')
            else:
                messages.info(request, 'Password is incorrect')
                return redirect('login')
        else:
            messages.info(request, 'Username is incorrect')
            return redirect('login')
    return render(request, 'page/login.html')
@login_required(login_url='login')
def logout(request):  
    auth.logout(request)
    messages.success(request, 'Logout successful')
    return redirect('home')
@login_required(login_url='login')
def identify(request):
    return render(request, 'page/identify.html')
@login_required(login_url='login')
def tracker(request):
    return render(request, 'page/tracker.html')
def research(request):
    return render(request, 'page/research.html')
@login_required(login_url='login')
def history(request):
    return render(request, 'page/history.html')