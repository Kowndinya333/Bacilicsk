
import datetime
from datetime import date, time
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
# Create your models here.
class Questionnaire(models.Model):
    """Class that represents the table "Questionnaire" in the database.

    Attributes:
        question_text: The description of the question
        pub_date: The date of publication of the question
        time_limit: The integer which is the time_limit to solve the question in days.
        identifier: The unique identifier that identifies with the particular question in the table
    """
    question_text=models.CharField(max_length=200)
    pub_date=models.DateTimeField('date published')
    time_limit=models.IntegerField(default=1)
    identifier=models.CharField(max_length=100)

    def __str__(self):
        return self.identifier

    def end_date(self):
        return self.pub_date + datetime.timedelta(days=self.time_limit)

    def active(self):
        return self.pub_date + datetime.timedelta(days=self.time_limit) > timezone.now()

    

class Solution(models.Model):
    """Class that represents the table "Solution" in the database.

    Attributes:
        question: the question for which the given entry is a solution
        code: the actual code which is the solution of the question
        lang: the programming language of the code written
        solver: the user that gave the solution
        is_Correct: it is 'P' if pending, 'Y' if correct, 'N' if incorrect.
    """
    LANGUAGES=(
        ('C', 'C++'),
        ('P', 'Python'),
        ('J', 'Java'),
    )
    question=models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    code=models.TextField()
    lang=models.CharField(max_length=1, choices=LANGUAGES, default='C')
    solver=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='solutions')
    is_Correct=models.CharField(max_length=1, default='P')

class CorrectSolution(models.Model):
    """Class that represents the table "CorrectSolution" in the table.

    Attributes:
        question: question for which the solution is a correct solution to.
        input1:test case input1
        output1:test case output1
        input2:test case input2
        output2: test case output2
        input3: test case input3
        output3: test case output3
    """
    question=ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name="relatedq")
    input1=models.TextField(blank=True, default=None)
    output1=models.TextField(default=None)
    input2=models.TextField(blank=True, default=None)
    output2=models.TextField(default=None)
    input3=models.TextField(blank=True, default=None)
    output3=models.TextField(default=None)