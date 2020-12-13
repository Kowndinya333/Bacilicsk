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

def showcodes(request):
    """To display all the saved codes from the database corresponding to the user requesting it.

    If the user is subscribed to the premium plan, then the user is reminded of it with the string stored in the variable submessage, statnding for
    subscription_message.
    The method then retrieves all the entries in the Code table that have the current user as the coder and a list of Code objects is generated.

    Args:
        A GET request requesting the codes written by the current user.
    Returns:
        Renders the HTML page, codes/showcodes.html with the list of all codes that the user has stored in the database.
    """
    if subcription_status(request)==True:
        submessage="You have premimum access. You can always head towards My Folders section to store unlimited amount of files"
    else:
        submessage=""
    codes=Code.objects.all().filter(coder=request.user)
    return render(request, 'codes/showcodes.html', {
        "codes":codes, "submessage":submessage
    })

def practice(request):
    """To process the GET request on pressing the Practice link from the left navigation bar of the homepage.

    It renders codes/practice.html containing a html form for the user to code, save and practice.

    Args:
        A GET request requested from the left navigation bar.
    Returns:
        It renders codes/practice.html that has a form for user to enter code and run in three programming languages-C++, Java, Python

    """
    if subcription_status(request)==True:
        submessage="You have premimum access. You can always head towards My Folders section to store unlimited amount of files"
    else:
        submessage=""
    return render(request, 'codes/practice.html', {
        "code_display":"Your code here", "submessage":submessage
    })

def savecode(request):
    """Process the request from the "Save" link from the codes/practice.html

    Takes in the inputs from the form. Uses a try-except block to check the validity of the form data and renders the codes/practice.html with 
    the supporting error message, if any error in the form data is found. If everything is fine, then the form data is stored into the Code table 
    with the coder being the current user.

    Args:
        A GET request from the practice page.
    Returns:
        Returns the codes/practice.html if with an error, if the form data is wrong and with just the saved code, if the form data is succesfully stored into the database.    
    """
    if request.user.is_authenticated:
        try:
            language=request.POST['lang']
            code_text=request.POST['codetext']
            fname=request.POST['saveas']
            if fname=="":
                return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please suggest a name to save the file"
            })
            if language=='C':
                if fname[-4:] == ".cpp" :
                    pass
                else :
                    return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please check the file name"
            })
            elif language=='P':
                if fname[-3:] == ".py" :
                    pass
                else :
                    return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please check the file name"
            })
            elif language=='J':
                if fname[-5:] == ".java" :
                    pass
                else :
                    return render(request, 'codes/practice.html', {
                "code_display":request.POST['codetext'], "err":"Please check the file name"
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
    """Processing GET request from the code file links from the codes/showcodes.html

    Reminds the user if already in Premium plan and displays message if desired to use code directory structure

    Args:
        GET request, along with the file name that wants to be retrieved
    Returns:
        Returns a html page, 'codes/showcode.html', along with any message that is passed
    """
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
    """Processes Delete code file request

    The method retrieves the Code object from the Code database that corresponds to the file name passed as an 
    argument and then deletes the file. Finally the user is redirected to codes/showcodes.html

    Args:
        GET request and a file name which has to be removed from the database.
    Returns:
        A HttpResponseRedirect to the codes/showcodes.html page with the updated list after deleting this file.
    """
    code=Code.objects.get(coder=request.user, name=file).delete()
    return HttpResponseRedirect(reverse("codes:showcodes"))

def updatecode(request, file):
    """Processes update request to the code of an already existing code object in Code table

    This is triggered when the user changes the code from the codes/showcode.html page and presses save.
    The updated code is obtained from the form that exists in the codes/showcode.html page. The code object corresponding to the 
    user and the file name given as arguments. THe code is then updated and saved. Finally user is redirected to the page showing the updated code.

    Args:
        GET request and file name of the file being modified.
    Returns:
        HttpResponseRedirect to the codes/showcode/file which displays the updated code.
    """
    new_code=request.POST['codetext']
    code=Code.objects.get(coder=request.user, name=file)
    code.code=new_code
    code.save()
    string='../showcode/'+file
    return HttpResponseRedirect(string)

def runcode(request, file):
    """Compilation and execution of the code

    The method is triggered when the user presses run on the showcodes.html page.It takes as argument, the file name. Hence, 
    retrieves the code object from the Code table corresponding to the file name and the current user. It then checks the language of the file.
    According to the language of the code file, it runs the corresponding code. It uses subprocess module to compile and execute the code.

    Args:
        A POST request and file name
    Returns:
        It renders back the codes/showcode/file but this time with compile error, if there is one or stdout of the process, if there is one.
    """
    code=Code.objects.get(coder=request.user, name=file)
    code_text=code.code
    lang=code.lang
    input_data=request.POST["input_data"]
    # print(input_data)
    # input_dataforpy= input_data.splitlines()
    # for a in input_dataforpy:
    #     a = a.strip("\r")
    # print(input_dataforpy)
    inputs=bytes(input_data, "UTF-8")
    commandline_args=request.POST["commandline_args"]
    cl_args=str(commandline_args)
    if lang=='C':
        p1="./files/"+request.user.username+"/templates/template."
        stringtolist=["g++",p1+"cpp","-o",p1+"exe"]
        string2=[p1+"exe"]
        for i in cl_args.split(" "):
            if i!="":
                string2.append(i)
        fhand=open(p1+"cpp", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        inpfile=open(p1+"txt",'w')
        myinpfile=File(inpfile)
        myinpfile.write(input_data)
        myinpfile.close()
        inpfile.close()
        inpfile = open(p1+"txt")
        inpfile.seek(0)
        k1=subprocess.run(stringtolist,  universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if k1.stderr:
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            k2=subprocess.run(string2, stdin = inpfile,  universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            inpfile.close()
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout
            })
    elif lang=='P':
        p1="./files/"+request.user.username+"/templates/template."
        stringtolist=["python3",p1+"py"]
        for i in cl_args.split(" "):
            if i!="":
                stringtolist.append(i)
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
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k2.stderr
            })
        else:
            # k2=subprocess.run('files/template.exe', capture_output=True, shell=False)
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout
            })
    elif lang=='J':
        p1="./files/"+request.user.username+"/templates/template."
        c_n = code.name
        if c_n.endswith(".java"):
            c_n = c_n[:-5]

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
        k1 = subprocess.run(["javac","./files/" + request.user.username +"/templates/"+c_n+".java"],universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if k1.stderr:
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            return render(request, 'codes/showcode.html', {
                "code":code.code, "name":code.name, "compiler_error":k1.stderr
            })
        else:
            list_string=["java","-cp","./files/"+request.user.username+"/templates/",c_n]
            for i in cl_args.split(" "):
                if i!="":
                    list_string.append(i)
            k2=subprocess.run(list_string,stdin = inpfile,universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            inpfile.close()
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".class")
            return render(request, "codes/showcode.html", {
                "code":code.code, "name":code.name, "stdout":k2.stdout
            })
