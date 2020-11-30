import datetime
from datetime import date, time
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django.utils import timezone
# Create your models here.
class Questionnaire(models.Model):
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
    LANGUAGES=(
        ('C', 'C++'),
        ('P', 'Python'),
        ('J', 'Java'),
    )
    question=models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    code=models.TextField()
    lang=models.CharField(max_length=1, choices=LANGUAGES, default='C')
    solver=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='solutions')

