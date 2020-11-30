from os import name
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from .models import Code
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files import File
import subprocess
# Create your views here.
def showcodes(request):
    codes=Code.objects.all().filter(coder=request.user)
    return render(request, 'codes/showcodes.html', {
        "codes":codes
    })

def practice(request):
    return render(request, 'codes/practice.html', {
        "code_display":"Your code here"
    })

def savecode(request):
    if request.user.is_authenticated:
        language=request.POST['lang']
        code_text=request.POST['codetext']
        fname=request.POST['saveas']
        code=Code(lang=language, code=code_text, coder=request.user, name=fname)
        code.save()
        string='../showcode/'+fname
        return HttpResponseRedirect(string)
    else:
        return HttpResponseRedirect(reverse("users:index"))

def showcode(request, file):
    code=Code.objects.get(coder=request.user, name=file)
    return render(request, "codes/showcode.html", {
        "code":code.code,
        "name":code.name
    })

def deletecode(request, file):
    code=Code.objects.get(coder=request.user, name=file).delete()
    return HttpResponseRedirect(reverse("codes:showcodes"))

def updatecode(request, file):
    new_code=request.POST['codetext']
    code=Code.objects.get(coder=request.user, name=file)
    code.code=new_code
    code.save()
    string='../showcode/'+file
    return HttpResponseRedirect(string)

def runcode(request, file):
    code=Code.objects.get(coder=request.user, name=file)
    code_text=code.code
    lang=code.lang
    if lang=='C':
        fhand=open('files/template.cpp', 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run('g++ files/template.cpp -o files/template.exe', capture_output=True, text=True, shell=False)
        if k1.stderr:
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run('files/template.exe', capture_output=True, shell=False)
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout.decode('UTF-8')
            })
    elif lang=='P':
        pass
    elif lang=='J':
        pass