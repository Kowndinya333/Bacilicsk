
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
        p1="files/"+request.user.first_name+"/templates/template."
        string="g++ "+p1+"cpp"+" -o "+p1+".exe"
        string2=p1+".exe"
        fhand=open(p1+"cpp", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run(string, capture_output=True, text=True, shell=False)
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
                "code":code_text, "path":filepath, "compiler_error":k1.stderr
            })
        else:
            # k2=subprocess.run('files/template.exe', capture_output=True, shell=False)
            return render(request, "codes/showcode.html", {
                "code":code_text, "path":filepath, "stdout":k1.stdout.decode('UTF-8')
            })
    elif filepath[-1]=='a':
        pass