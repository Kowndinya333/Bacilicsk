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
    """Check whether user is subscribed to code directory or not
    
    Uses the present request and finds if the respective user is subscribed or not.

    Args:
        request: the present request at any point
    
    Returns:
        A Boolean value. Returns true if the current user sending the request is subscribed to code directory
    """
    myuser=MyUser.objects.get(relatedUser=request.user)
    if myuser.Paid_User=='Y':
        return True
    elif myuser.Paid_User=='N':
        return False

def index(request):
    """Main webpage rendering

    The first function that is called when someone initiates the website.

    Args:
        request: takes in GET request as an argument
    
    Returns:
        If the current user who opened that website already has a session with the user already logged in, then 
        renders the main dashboard of website whose code resides in users/index.html.
        Else if the current user is not logged in, then we call login_view method.
    """
    if request.user.is_authenticated:
        return render(request, 'users/index.html')
    else:
        return HttpResponseRedirect(reverse('users:login'))

def login_view(request):
    """Manages GET/POST requests related to login

    A GET request to this method is made when redirected by index function.
    A POST request to this method is made when some user presses login button from the users/login.html page.
    Checks for errors in login info given by the user. If there is error, redirects again to login page, along with
    displaying the message "Invalid Credentials". If the login details are valid, then the user is logged in and the homepage is rendered.

    Args:
        A GET/POST request
    
    Returns:
        Returns either a Http Redirect to the login page or a rendering of the main homepage of the website.
    """
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
    """Logout function

    Manages logout request. Logs out the user and returns the login page again
    
    Args:
        A GET request for logout_view
    Returns:
        The login page
    
    """
    logout(request)
    return render(request, "users/login.html")

def signup_view(request):
    """Manages signup requests(GET/POST)

    Based on whether the request type is GET or POST, different pages are rendered.
    If the request is GET type, then signup html page given by users/signup.html is rendered
    Else if the request is POST type, there is some error checking in the details provided by user for registration
    and if there are no errors then user is registered in the users database. Then the user is redirected to login page to further use the
    services provided by the website.The method is also responsible for creating a separate folder for the user in a directory named files which will 
    later be used to serve the user many features. The method also adds an entry in the myUser table defined in users/models.py, with a default value for 
    the subscription_status to be of Basic. The ;method also creates two files in the directory created above in the name of the user with names being,
    template.cpp and template.py

    Args:
        A GET/POST request

    Returns:
        Based on the request type and error checking, either login page is rendered, or signup page is rendered.
    """
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
    """Called when GET request to view profile is made.

    Calls subscription_status function to know if the user is signed up for Basic plan or Premium plan.

    Args:
        A GET request, requesting profile of user
    Returns:
        A html page(users/profile.html), that displays the basic details of the user along with which type of subscription he/she has.
    """
    if subcription_status(request)==True:
        subscribed_status="Premium Plan"
    else:
        subscribed_status="Basic Plan"
    return render(request, 'users/profile.html', {
        "subscribed_status":subscribed_status
    })

def subscribe(request):
    """Subscirbe requests is handled

    This function is called when the user presses the button for payment to upgrade to premium plan.

    Args:
        A GET request to the function
    Returns:
        The method opens the myuser table to change the entry corresponding user's paid status to yes, i.e., subsribed to premium plan.
    """
    myuser=MyUser.objects.get(relatedUser=request.user)
    myuser.Paid_User='Y'
    myuser.save()
    return HttpResponseRedirect(reverse('codedir:index'))
