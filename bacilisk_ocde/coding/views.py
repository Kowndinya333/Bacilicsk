
from django.shortcuts import render 
import subprocess
import os
from django.core.files import File
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    """Processes GET request on pressing a link of a file from the code directory structure

    Returns the Html page coding/index.html

    Args:
        A GET request from the index of the codedir app
    Returns:
        Renders a html page coding/index.html
    """
    return render(request, "coding/index.html", {
        "code":"Your code here"
    })

def savecode(request):
    """Processes the POST request from the index of the coding app.(The file which is open right now from the codedir app)

    The method extracts codetext, and filepath from the POST request and then writes it to the file located in the filepath.
    And the user is taken to the coding/index.html page but this time with altered data, with code being the codetext that was just saved in the 
    given filepath.

    Args:
        POST Request from the index of the coding app.
    Returns:
        Returns rendering the html page - coding/index.html along with passing the necessary data
    """
    codetext=request.POST["codetext"]
    filepath=request.POST["filepath"]
    fhand=open(filepath, "w+")
    fhand.write(codetext)
    fhand.close()
    return render(request, "coding/index.html", {
        "path":filepath, "code":codetext
    })

def runcode(request):
    """Processes the POST request from pressing the run button on coding/index.html

    The method extracts codetext, and filepath from the POST request. It also extracts the inputs from the POST request. 
    After that, based on the extension of the file, the programming language is decided..Now, in the same way as for the codes app, the code
    is executed using the subprocess module. In case of java, little more work is done as the file name and the class name should be the same.
    The user is taken back to where he started but this time with an additional text which may be either stderr, if there is a compile error. 
    If there is any stdout, then it is rendered in the same html page.

    Args:
        The POST request from the coding/index.html
    Reuturns:
        The same html page from where we ran the program, is rendered, but now with an additional information
    """
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
