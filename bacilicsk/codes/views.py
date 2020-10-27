from django.contrib.auth.models import User
from django.http import request
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from .models import Code
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "codes/index.html")
    else:
        return HttpResponseRedirect(reverse("users:index"))

def save_code(request):
    if request.user.is_authenticated:
        language=request.POST['lang']
        code_text=request.POST['codetext']
        fname=request.POST['saveas']
        code=Code(lang=language, code=code_text, coder=request.user, name=fname)
        code.save()
        return HttpResponseRedirect(reverse("users:index"))
    else:
        return HttpResponseRedirect(reverse("users:index"))

def view_codes(request):
    codes=Code.objects.all().filter(coder=request.user)
    return render(request, "codes/allcodes.html",{
        "codes":codes
    })

def show_file(request, file):
    code=Code.objects.get(coder=request.user, name=file)
    return render(request, "codes/showcode.html",{
        "code": code.code,
        "name": code.name
    })

def delete_file(request, file):
    Code.objects.get(coder=request.user, name=file).delete()
    codes=Code.objects.all().filter(coder=request.user)
    return render(request, "codes/allcodes.html",{
        "codes":codes
    })
