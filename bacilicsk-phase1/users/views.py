from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "users/index.html")
    else:
        return HttpResponseRedirect(reverse('users:login'))

def login_view(request):
    if request.method!="POST":
        return render(request, "users/login.html")
    else:
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("users:index"))
        else:
            return render(request, "users/login.html", {
                "message":"Invalid Credentials"
            })

def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {
        "message":"Logged out successfully"
    })

def signup_view(request):
    if request.method=="GET":
        return render(request, "users/signup.html")
    else:
        username=request.POST['username']
        password=request.POST['password']
        email=request.POST['email']
        firstname=request.POST['first_name']
        lastname=request.POST['last_name']
        user=User.objects.create_user(username, email, password)
        user.last_name=lastname
        user.first_name=firstname
        user.save()
        return HttpResponseRedirect(reverse("users:login"))