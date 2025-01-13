from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import HttpResponse, FileResponse, Http404, StreamingHttpResponse
from .models import Bee
from asgiref.sync import async_to_sync
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), 'processor'))))
from processor.main import *
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
    if request.method == 'POST':
        print(request.FILES.get('file'))
        user = request.user
        video = request.FILES.get('file')
        new_bee = Bee.objects.create(user=user, video=video)
        
        messages.success(request,"Result")
   

        # Take last Bee saved
        new_bee.save()
        video_name = new_bee.video.name.split('/')[1].split('.')[0]
        print(video_name)
        process(video_name + '.mp4')
        new_video_path = 'return_videos/' + video_name + '_p_output.mp4'
        print(new_video_path)
        new_bee.return_video = new_video_path
        new_bee.save()
        return redirect('/result/' + str(new_bee.pk))
    return render(request, 'page/identify.html')
@login_required(login_url='login')
def tracker(request):
    return render(request, 'page/tracker.html')
def research(request):
    return render(request, 'page/research.html')
@login_required(login_url='login')
def history(request):
    user = User.objects.get(username=request.user)
    history = Bee.objects.filter(user=user)
    for i in history:
        i.video = i.video.name.split('/')[1]
        i.return_video = i.return_video.name.split('/')[1]
    context = {
        'history': history
    }
    return render(request, 'page/history.html', context)
@login_required(login_url='login')
def profile(request):
    user = User.objects.get(username=request.user)
    history = Bee.objects.filter(user=user)
    return render(request, 'page/profile.html', {'history': history, 'user': user})
@login_required(login_url='login')
def result(request,pk):
    bee = Bee.objects.get(pk=pk)
    video_name = bee.video.name.split('/')[1]
    return_video_name = bee.return_video.name.split('/')[1]
    context = {
        'bee': bee,
        'video_name': video_name,
        'return_video_name': return_video_name
    }
    return render(request, 'page/result.html', context)
def stream_video(request, folder,name):
    path = f'{folder}/{name}'
    try:
        def file_chunk_generator(file_path, chunk_size=8192):
            with open(file_path, 'rb') as file:
                while chunk := file.read(chunk_size):
                    yield chunk
        
        return StreamingHttpResponse(
        file_chunk_generator(f'media/{path}'),
        content_type='video/mp4'
    )
    except FileNotFoundError:
        raise Http404()
    