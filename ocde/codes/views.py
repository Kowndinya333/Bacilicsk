from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from .models import Code
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files import File
import subprocess
import os
from users.models import MyUser
# Create your views here.

def subcription_status(request):
    myuser=MyUser.objects.get(relatedUser=request.user)
    if myuser.Paid_User=='Y':
        return True
    elif myuser.Paid_User=='N':
        return False

def showcodes(request):
    if subcription_status(request)==True:
        submessage="You have premimum access. You can always head towards My Folders section to store unlimited amount of files"
    else:
        submessage=""
    codes=Code.objects.all().filter(coder=request.user)
    return render(request, 'codes/showcodes.html', {
        "codes":codes, "submessage":submessage
    })

def practice(request):
    if subcription_status(request)==True:
        submessage="You have premimum access. You can always head towards My Folders section to store unlimited amount of files"
    else:
        submessage=""
    return render(request, 'codes/practice.html', {
        "code_display":"Your code here", "submessage":submessage
    })

def savecode(request):
    if request.user.is_authenticated:
        try:
            language=request.POST['lang']
            code_text=request.POST['codetext']
            fname=request.POST['saveas']
            if fname=="":
                return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please suggest a name to save the file"
            })
            #checking maximum capacity which is 10
            codes=Code.objects.all().filter(coder=request.user)
            if len(codes)==10:
                return render(request, 'codes/practice.html', {
                    "code_display":request.POST['codetext'], "err":"You have reached the maximum limit. Please subscribe to premium plan for more storage", "saveas":request.POST['saveas']
                })
            code=Code(lang=language, code=code_text, coder=request.user, name=fname)
            code.save()
            string='../showcode/'+fname
            return HttpResponseRedirect(string)
        except:
            return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please select a programming language", "saveas":request.POST['saveas']
            })
    else:
        return HttpResponseRedirect(reverse("users:index"))

def showcode(request, file):
    if subcription_status(request)==True:
        submessage="You have premimum access. You can always head towards My Folders section to store unlimited amount of files"
    else:
        submessage=""
    code=Code.objects.get(coder=request.user, name=file)
    return render(request, "codes/showcode.html", {
        "code":code.code,
        "name":code.name, "submessage":submessage
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
    input_data=request.POST["input_data"]
    inputs=bytes(input_data, "UTF-8")
    if lang=='C':
        p1="files/"+request.user.first_name+"/templates/template."
        stringtolist=["g++",p1+"cpp","-o",p1+"exe"]
        string2=[p1+"exe"]
        fhand=open(p1+"cpp", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run(stringtolist, capture_output=True, text=True, shell=False)
        if k1.stderr:
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run(string2, input=inputs, capture_output=True, shell=False)
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout.decode('UTF-8')
            })
    elif lang=='P':
        p1="files/"+request.user.first_name+"/templates/template."
        stringtolist=["python3",p1+"py"]
        fhand=open(p1+"py", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run(stringtolist , input = input_data,universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if k1.stderr:
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            # k2=subprocess.run('files/template.exe', capture_output=True, shell=False)
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k1.stdout
            })
    elif lang=='J':
        c_n = code.name
        if c_n.endswith(".java"):
            c_n = c_n[:-5]
        fhand = open('files/' + request.user.firstname +'/templates/'+c_n+'.java','w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1 = subprocess.run(['javac','./files/'+request.user.firstname+'/templates/'+c_n+'.java'],universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if k1.stderr:
            os.remove('./files/'+request.user.firstname+'/templates/'+c_n+'.java')
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run(['java','-cp','./files',c_n],universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.remove('./files/'+request.user.firstname+'/templates/'+c_n+'.java')
            os.remove('./files/'+request.user.firstname+'/templates/'+c_n+'.class')
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout
            })