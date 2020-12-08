from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls.base import reverse, set_urlconf
import subprocess
import os
from pathlib import Path
from .models import MyUser
from django.db import IntegrityError
# Create your views here.

def subcription_status(request):
    myuser=MyUser.objects.get(relatedUser=request.user)
    if myuser.Paid_User=='Y':
        return True
    elif myuser.Paid_User=='N':
        return False
def index(request):
    if request.user.is_authenticated:
        return render(request, 'users/index.html')
    else:
        return HttpResponseRedirect(reverse('users:login'))

def login_view(request):
    if request.method=='GET':
        return render(request, 'users/login.html')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        if email.strip()=="":
            return render(request, 'users/login.html', {
                "message":"Please enter a valid email address"
            })
        if password.strip()=="":
            return render(request, 'users/login.html', {
                "message":"Please enter your password"
            })
        try:
            user_1=User.objects.get(email=email)
        except:
            return render(request, 'users/login.html', {
                "message":"Invalid Credentials"
            })
        user_1=User.objects.get(email=email)
        user=authenticate(request, username=user_1.username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('users:index'))
        else:
            return render(request, 'users/login.html', {
                "message":"Invalid Credentials"
            })

def logout_view(request):
    logout(request)
    return render(request, "users/login.html")

def signup_view(request):
    if request.method=='GET':
        return render(request, 'users/signup.html')
    else:

        password=request.POST['password']
        password1=request.POST['confpassword']
        email=request.POST['email']
        username=request.POST['username']
        name=request.POST['name']
        username=username.strip()
        #username=request.POST['username']
        #if username.strip()=="":
        #    return render(request, 'users/signup.html', {
        #        "message":"Please enter Username"
        #    })
        if username.strip()=="":
            return render(request, 'users/signup.html', {
                "message":"Please enter username"
            })
        if username.count(" "):
            return render(request, 'users/signup.html', {
                "message":"Please don't use spaces in username"
            })
        if name.strip()=="":
            return render(request, 'users/signup.html', {
                "message":"Please enter your Name"
            })
        if password=="":
            return render(request, 'users/signup.html', {
                "message":"Please set your password"
            })
        if password1 == password :
            pass
        else:
            return render(request, 'users/signup.html', {
                "message":"Password not matching"
            })
        #user=User.objects.create_user(username, email, password)
        try:
            user=User.objects.create_user(username, email, password)
        except IntegrityError as e: 
            return render(request, 'users/signup.html', {
                "message":"Username already exists, try a different one"
            })
        #user.username=username
        user.last_name=name
        user.username=username
        myuser=MyUser(Paid_User='N', relatedUser=user)
        myuser.save()
        p1=Path("files/"+username)
        p2=Path("files/"+username+"/templates")
        os.mkdir(p1)
        os.mkdir(p2)
        open("files/"+username+"/templates/"+"template.cpp", "w+")
        open("files/"+username+"/templates/"+"template.py", "w+")
        open("files/"+username+"/templates/"+"template.java", "w+")
        return HttpResponseRedirect(reverse("users:login"))

def profile(request):
    if subcription_status(request)==True:
        subscribed_status="Premium Plan"
    else:
        subscribed_status="Basic Plan"
    return render(request, 'users/profile.html', {
        "subscribed_status":subscribed_status
    })

def subscribe(request):
    myuser=MyUser.objects.get(relatedUser=request.user)
    myuser.Paid_User='Y'
    myuser.save()
    return HttpResponseRedirect(reverse('codedir:index'))
