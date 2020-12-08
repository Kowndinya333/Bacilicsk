
from django.shortcuts import render 
import subprocess
import os
from django.core.files import File
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    return render(request, "coding/index.html", {
        "code":"Your code here"
    })

def savecode(request):
    codetext=request.POST["codetext"]
    filepath=request.POST["filepath"]
    fhand=open(filepath, "w+")
    fhand.write(codetext)
    fhand.close()
    return render(request, "coding/index.html", {
        "path":filepath, "code":codetext
    })

def runcode(request):
    filepath=request.POST["filepath"]
    input_data=request.POST["input_data"]
    inputs=bytes(input_data, "UTF-8")
    code_text=""
    fhand=open(filepath)
    for line in fhand:
        code_text+=line
    if filepath[-1]=='p':
        p1="files/"+request.user.username+"/templates/template."
        string=p1+"cpp"
        string2=p1+"exe"
        fhand=open(p1+"cpp", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run(["g++", string, "-o", string2], capture_output=True, text=True, shell=False)
        if k1.stderr:
            return render(request, 'coding/index.html', {
                "code":code_text, "path":filepath, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run(string2, input=inputs, capture_output=True, shell=False)
            return render(request, "coding/index.html", {
                "code":code_text, "path":filepath, "stdout":k2.stdout.decode('UTF-8')
            })
    elif filepath[-1]=='y':
        p1="files/"+request.user.username+"/templates/template."
        stringtolist=["python3",p1+"py"]
        fhand=open(p1+"py", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        inpfile=open(p1+"txt",'w+')
        myinpfile=File(inpfile)
        myinpfile.write(input_data)
        myinpfile.close()
        inpfile.close()
        inpfile = open(p1+"txt")
        inpfile.seek(0)
        k1=subprocess.run(["cat",p1+"txt"], universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        k2=subprocess.run(stringtolist, input = k1.stdout, universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        inpfile.close()
        if k2.stderr:
            return render(request, 'coding/index.html', {
                "code":code_text, "path":filepath, "compiler_error":k2.stderr
            })
        else:
            # k2=subprocess.run('files/template.exe', capture_output=True, shell=False)
            return render(request, "coding/index.html", {
                "code":code_text, "path":filepath, "stdout":k2.stdout
            })
    elif filepath[-1]=='a':
        i=len(filepath)-1
        while filepath[i]!='/':
            i-=1
        c_n=filepath[i+1:-5]
        p1="./files/"+request.user.username+"/templates/template."

        # print("./files/" + request.user.username +"/templates/"+c_n+".java")
        fhand = open("./files/" + request.user.username +"/templates/"+c_n+".java",'w')
        fhand.close()
        fhand = open("./files/" + request.user.username +"/templates/"+c_n+".java",'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        inpfile=open(p1+"txt",'w+')
        myinpfile=File(inpfile)
        myinpfile.write(input_data)
        myinpfile.close()
        inpfile.close()
        inpfile = open(p1+"txt")
        inpfile.seek(0)
        k1 = subprocess.run(["javac","./files/" + request.user.username +"/templates/"+c_n+".java"],capture_output=True, shell=False)
        if k1.stderr:
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            return render(request, 'coding/index.html', {
                "code":code_text, "path":filepath, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run(["java","-cp","./files/" + request.user.username +"/templates/",c_n],stdin = inpfile,text = True, capture_output=True, shell=False)
            inpfile.close()
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".class")
            return render(request, "coding/index.html", {
                "code":code_text, "path":filepath, "stdout":k2.stdout
            })
