
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
    """Processes the GET request that is obtained from pressing the Competition link on the left nav-bar of the main page.

    All the questions from the Questionnaire table are extracted, and then it is rendered in competition/index.html but only if the quesiton is active as 
    decided by the developers.
    Args:
        A GET request when pressed the Competition button
    Returns:
        Returns by rendering the competition/index.html where all active questions are listed.
    """
    all_questions=Questionnaire.objects.all()
    return render(request, "competition/index.html",{
        "questions":all_questions
    })

def openquestion(request, string):
    """Processes the GET request obtained by pressing the link of question from the competition/index.html.

    The question with the given string as identifier is extracted from the Questionnaire table. If there is already a solution submitted by the user, 
    then the competition/open/string is rendered with the code that the user has submitted earlier.
    If not submitted user sees an empty field for him to type in his solution.

    Args:
        The GET request, and a string which is the identifier to the question
    Returns:
        Returns by rendering the competition/open/string with appropriate content,
    """
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
    """Processes the POST request from the competition/openquestion.html on pressing save.

    We first find out whether the user has submitted any solution to the question in the past. If submitted, then we just modify the solution in the database. 
    If not, then we create a new solution and save it in the database.

    Args:
        A POST request and a string which is the identifier of the question.
    Returns:
        Based on the final saved solution, the method renders back the competition/openquestion.html with the appropriate code.
    """
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
            solution.lang=language
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
    """Processes the POST request from the competition/openquestion.html on pressing the run button.

    See codes app and coding app for the compilation details
    Args:
        A POST request and a string which is the identifier for the question for which the solution is being run.
    Returns:
        Returns by rendering the competition/openquestion.html, but this time with stderr or stdout being shown as an additional textarea.
    """
    question=Questionnaire.objects.get(identifier=string)
    numdays=question.time_limit
    deadline=question.pub_date + datetime.timedelta(days=numdays)
    solution=Solution.objects.get(solver=request.user, question=question)
    code_text=solution.code
    lang=solution.lang
    input_data=request.POST["input_data"]
    inputs=bytes(input_data, "UTF-8")
    if lang=='C':
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
            return render(request, 'competition/openquestion.html', {
                "code_display":code_text, "name":question.identifier, "compiler_error":k1.stderr, "question":question, "deadline":deadline
            })
        else:
            k2=subprocess.run(string2, input=inputs, capture_output=True, shell=False)
            return render(request, "competition/openquestion.html", {
                "code_display":code_text, "name":question.identifier, "stdout":k2.stdout.decode('UTF-8'), "question":question, "deadline":deadline
            })
    elif lang=='P':
        p1="files/"+request.user.username+"/templates/template."
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
                "code_display":code_text, "name":question.identifier, "stdout":k2.stdout, "question":question, "deadline":deadline
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
    """Processes the GET/POST requests for validation.

    This is a secret function which the users will not know. 
    Validation happens by checking each of the test cases from the CorrectSolutions table. 
    The code will be run in similar manner and the test cases are checked against each of the solutions given by the users.
    Args:
        A GET/POST request, and a string which is the identifier of the question
    Returns:
        Returns by rendering the main dashboard of the website
    """
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
                    k1=subprocess.run(["g++", s1, "-o", s2], capture_output=True, text=True, shell=False)
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
                    myinpfile.write(inputs[i])
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
    """Processes the GET request on pressing the Progress button on the top right of the main page of the website.

    First the status of the user for each question is displayed. These include "Not Attempted", "Passed", "Failed"
    Then the points acquired by each of the registered user is displayed in the decreasing order of the points acquired.
    Args:
        A GET request requesting the Progress of the user
    Returns:
        A html page that has entire progress displayed.(competition/results.html)
    """
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
    
            