from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Questionnaire)
admin.site.register(Solution)
admin.site.register(CorrectSolution)
