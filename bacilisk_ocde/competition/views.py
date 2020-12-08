
from datetime import date
from django.http.response import HttpResponseRedirect
from .models import CorrectSolution, Questionnaire, Solution
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
        path="./../open/"+string
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
        p1="files/"+request.user.username+"/template/template."
        string=p1+"cpp"
        string2=p1+"exe"
        fhand=open(p1+"cpp", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        k1=subprocess.run(["g++", string, "-o", string2], capture_output=True, text=True, shell=False)
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
        p1="files/"+request.user.username+"/template/template."
        stringtolist=["python3", p1+"py"]
        fhand=open(p1+"py", "w+")
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        inpfile=open(p1+"txt", "w+")
        myinpfile=File(inpfile)
        myinpfile.write(input_data)
        myinpfile.close()
        inpfile=open(p1+"txt")
        inpfile.seek(0)
        k1=subprocess.run(["cat", p1+"txt"], universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        k2=subprocess.run(stringtolist, input = k1.stdout, universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        inpfile.close()
        if k2.stderr:
            return render(request, 'competition/openquestion.html', {
                "code_display":code_text, "name":question.identifier, "compile_error":k2.stderr, "question":question, "deadline":deadline
            })
        else:
            return render(request, "competition/openquestion.html", {
                "code_display":code_text, "name":question.identifier, "stout":k2.stout, "question":question, "deadline":deadline
            })
    elif lang=='J':
        p1="./files/"+request.user.username+"/templates/template."
        c_n=question.identifier
        fhand=open("./files/"+request.user.username+"/templates/"+c_n+".java", 'w+')
        fhand.close()
        fhand=open("./files/"+request.user.username+"/templates/"+c_n+".java", 'w+')
        myFile=File(fhand)
        myFile.write(code_text)
        myFile.close()
        fhand.close()
        inpfile=open(p1+"txt", 'w+')
        myinpfile=File(inpfile)
        myinpfile.write(input_data)
        myinpfile.close()
        inpfile.close()
        inpfile=open(p1+"txt")
        inpfile.seek(0)
        k1 = subprocess.run(["javac","./files/" + request.user.username +"/templates/"+c_n+".java"],capture_output=True, shell=False)
        if k1.stderr:
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            return render(request, 'coding/index.html', {
                "code_display":code_text, "name":question.identifier, "compiler_error":k1.stderr, "question":question, "deadline":deadline
            })
        else:
            k2=subprocess.run(["java","-cp","./files/" + request.user.username +"/templates/",c_n],stdin = inpfile,text = True, capture_output=True, shell=False)
            inpfile.close()
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".java")
            os.remove("./files/" + request.user.username +"/templates/"+c_n+".class")
            return render(request, "coding/index.html", {
                "code_display":code_text, "name":question.identifier, "stdout":k2.stdout, "question":question, "deadline":deadline
            })

def validate(request, string):
    if request.method=="GET":
        return render(request, "competition/validate.html", {
            "q_identifier":string
        })
    elif request.method=="POST":
        identifier=request.POST["q_identifier"]
        question=Questionnaire.objects.get(identifier=identifier)
        solutions=Solution.objects.all().filter(question=question)
        correct_solution=CorrectSolution.objects.get(question=question)
        inputs=list()
        inputs.append(correct_solution.input1)
        inputs.append(correct_solution.input2)
        inputs.append(correct_solution.input3)
        outputs=list()
        outputs.append(correct_solution.output1)
        outputs.append(correct_solution.output2)
        outputs.append(correct_solution.output3)
        for solution in solutions:
            code_text=solution.code
            lang=solution.lang
            if lang=="C":
                path='files/validation/template.'
                s1=path+"cpp"
                s2=path+"exe"
                fhand=open(s1, "w+")
                myFile=File(fhand)
                myFile.write(code_text)
                myFile.close()
                fhand.close()
                solution.is_Correct='Y'
                solution.save()
                for i in range(3):
                    input_data=bytes(inputs[i], "UTF-8")
                    k1=subprocess.run(["g++", s1, "-o", "s2"], capture_output=True, text=True, shell=False)
                    if k1.stderr:
                        solution.is_Correct='N'
                        solution.save()
                        break
                    else:
                        k2=subprocess.run(s2, input=input_data, capture_output=True, shell=False)
                        stdout=k2.stdout.decode("UTF-8")
                        if outputs[i]!=stdout:
                            solution.is_Correct='N'
                            solution.save()
                            break
            elif lang=="P":
                path='files/validation/template.'
                s1=path+"py"
                stringtolist=["python3", path+"py"]
                fhand=open(s1, "w+")
                myFile=File(fhand)
                myFile.write(code_text)
                myFile.close()
                fhand.close()
                solution.is_Correct='Y'
                solution.save()
                for i in range(3):
                    input_data=bytes(inputs[i], "UTF-8")
                    inpfile=open(path+"txt", 'w+')
                    myinpfile=File(inpfile)
                    myinpfile.write(input_data)
                    myinpfile.close()
                    inpfile.close()
                    inpfile=open(path+"txt")
                    inpfile.seek(0)
                    k1=subprocess.run(["cat", path+"txt"], universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    k2=subprocess.run(stringtolist, input = k1.stdout, universal_newlines=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    inpfile.close()
                    if k2.stderr:
                        solution.is_Correct='N'
                        solution.save()
                    else:
                        if outputs[i]!=k2.stdout:
                            solution.is_Correct='N'
                            solution.save()
                            break
            elif lang=="J":
                path='files/validation/template.'
                c_n=identifier
                fhand=open("./files/"+"validation/"+c_n+".java", 'w+')
                myFile=File(fhand)
                myFile.write(code_text)
                myFile.close()
                fhand.close()
                solution.is_Correct='Y'
                solution.save()
                for i in range(3):
                    input_data=bytes(inputs[i], "UTF-8")
                    inpfile=open(path+"txt", 'w+')
                    myinpfile=File(inpfile)
                    myinpfile.write(input_data)
                    myinpfile.close()
                    inpfile.close()
                    inpfile=open(path+"txt")
                    inpfile.seek(0)
                    k1 = subprocess.run(["javac","./files/" + "validation/" + c_n+".java"],capture_output=True, shell=False)
                    if k1.stderr:
                        solution.is_Correct='N'
                        solution.save()
                    else:
                        if outputs[i]!=k1.stdout:
                            solution.is_Correct='N'
                            solution.save()
                            break
        return render(request, "users/index.html")

def results(request):
    questions=Questionnaire.objects.all()
    status=list()
    for question in questions:
        try:
            solution=Solution.objects.get(question=question, solver=request.user)
            if solution.is_Correct=='Y':
                status.append("Passed")
            elif solution.isCorrect=='N':
                status.append("Failed")
            else:
                status.append("Yet to be graded")
        except:
            status.append('Not attempted')
            continue

    users=User.objects.all()
    ranks=dict()
    for user in users:
        ranks[user.username]=0
    for question in questions:
        solutions=Solution.objects.all().filter(question=question)
        for solution in solutions:
            user=solution.solver
            if solution.is_Correct=='Y':
                ranks[user.username]+=1
    ranks_new=dict()
    for i in sorted(ranks, key=ranks.get, reverse=True):
        ranks_new[i]=ranks[i]
    print(ranks_new)
    return render(request, "competition/results.html", {
        "questions":questions, "status":status, "leaderboard":ranks_new
    })
    
            