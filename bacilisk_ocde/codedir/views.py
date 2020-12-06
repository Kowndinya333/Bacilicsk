
from users.models import MyUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from pathlib import Path
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import os
import subprocess
from django.urls.base import reverse
import shutil
from django.urls.conf import path
# Create your views here.
def index(request):
    myuser=MyUser.objects.get(relatedUser=request.user)
    if myuser.Paid_User=='N':
        return render(request, "codedir/unsubscribed.html")
    else:
        string=str(request.path)
        path='.'+string+request.user.first_name
        listofDirs=os.listdir(path)
        dirs=list()
        files=list()
        for f in listofDirs:
            s=path+'/'+f
            print(path)
            if os.path.isfile(s):
                files.append(f)
            if os.path.isdir(s) and f!='templates':
                if  f!="validation":
                    dirs.append(f)
        return render(request, 'codedir/index.html', {
            "path":path, "dirs":dirs, "files":files
        })

def parsepath(request):
    givenpath=request.POST['path']
    if os.path.isfile(givenpath):
        code_text=""
        fhand=open(givenpath)
        for line in fhand:
            code_text+=line
        return render(request, "coding/index.html",{
            "path":givenpath, "code":code_text
        })
    else:
        listofDirs=os.listdir(givenpath)
        dirs=list()
        files=list()
        for f in listofDirs:
            s=givenpath+'/'+f
            if os.path.isfile(s):
                files.append(f)
            if os.path.isdir(s):
                dirs.append(f)
        return render(request, 'codedir/index.html', {
            "path":givenpath, "dirs":dirs, "files":files
        })

def newfolder(request):
    path=request.POST["presentpath"]
    newstr=path[2:]
    folder_name=request.POST['newfoldername']
    string=newstr+'/'+folder_name
    os.mkdir(string)
    return HttpResponseRedirect(reverse('codedir:index'))

def newfile(request):
    path=request.POST["presentpath"]
    newstr=path[2:]
    file_name=request.POST['newfilename']
    string=newstr+'/'+file_name
    open(string, "w+")
    return HttpResponseRedirect(reverse("codedir:index"))

def deletefolder(request):
    path=request.POST["path"]
    shutil.rmtree(path)
    return HttpResponseRedirect(reverse("codedir:index"))

def deletefile(request):
    path=request.POST["path"]
    os.remove(path)
    return HttpResponseRedirect(reverse("codedir:index"))