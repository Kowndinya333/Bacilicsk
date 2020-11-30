from datetime import date
from django.http.response import HttpResponseRedirect
from .models import Questionnaire, Solution
from django.shortcuts import render
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
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