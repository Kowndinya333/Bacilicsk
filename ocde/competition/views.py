from datetime import date
from django.http.response import HttpResponseRedirect
from .models import Questionnaire, Solution
from django.shortcuts import render
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import os
import subprocess
from django.core.files import File
# Create your views here.

def index(request):
    all_questions=Questionnaire.objects.all()
    return render(request, "competition/index.html",{
        "questions":all_questions
    })

def openquestion(request, string):
    question = Questionnaire.objects.get(identifier=string)
    numdays=question.time_limit
    deadline=question.pub_date + datetime.timedelta(days=numdays)
    solution=Solution.objects.all().filter(question=question, solver=request.user)
    if len(solution)==0:
        code_to_show="Your code here"
    else:
        solution=Solution.objects.get(question=question, solver=request.user)
        code_to_show=solution.code

    return render(request, 'competition/openquestion.html', {
        "question":question, "deadline":deadline, "code_display":code_to_show
    })

def saveattempt(request, string):
    try:
        question=Questionnaire.objects.get(identifier=string)
        solution=Solution.objects.all().filter(question=question, solver=request.user)
        code=request.POST['codetext']
        language=request.POST['lang']
        if len(solution)==0:
            sol=Solution(question=question, code=code, lang=language, solver=request.user)
            sol.save()
        else:
            solution=Solution.objects.get(question=question, solver=request.user)
            new_code=request.POST["codetext"]
            solution.code=new_code
            solution.save()
        path="../"+string
        return HttpResponseRedirect(path)
    except:
        question=Questionnaire.objects.get(identifier=string)
        numdays=question.time_limit
        deadline=question.pub_date + datetime.timedelta(days=numdays)
        code_to_show=request.POST['codetext']
        lang_message="Please select a language"
        return render(request, 'competition/openquestion.html', {
            "question":question, "deadline":deadline, "code_display":code_to_show, "lang_message":lang_message
        })

def runcode(request, string):
    question=Questionnaire.objects.get(identifier=string)
    numdays=question.time_limit
    deadline=question.pub_date + datetime.timedelta(days=numdays)
    solution=Solution.objects.get(solver=request.user, question=question)
    code_text=solution.code
    lang=solution.lang
    input_data=request.POST["input_data"]
    inputs=bytes(input_data, "UTF-8")
    if lang=='C':
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
            return render(request, 'competition/openquestion.html', {
                "code_display":code_text, "name":question.identifier, "compiler_error":k1.stderr, "question":question, "deadline":deadline
            })
        else:
            k2=subprocess.run(string2, input=inputs, capture_output=True, shell=False)
            return render(request, "competition/openquestion.html", {
                "code_display":code_text, "name":question.identifier, "stdout":k2.stdout.decode('UTF-8'), "question":question, "deadline":deadline
            })
    elif lang=='P':
        pass
    elif lang=='J':
        pass