from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls.base import reverse, set_urlconf
import subprocess
import os
from pathlib import Path
from .models import MyUser
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
        email=request.POST['email']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        user=User.objects.create_user(firstname, email, password)
        user.last_name=lastname
        user.first_name=firstname
        user.save()
        myuser=MyUser(Paid_User='N', relatedUser=user)
        myuser.save()
        p1=Path("files/"+firstname)
        p2=Path("files/"+firstname+"/templates")
        os.mkdir(p1)
        os.mkdir(p2)
        open("files/"+firstname+"/templates/"+"template.cpp", "w+")
        open("files/"+firstname+"/templates/"+"template.py", "w+")
        open("files/"+firstname+"/templates/"+"template.java", "w+")
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
    return render(request, 'codedir/index.html')