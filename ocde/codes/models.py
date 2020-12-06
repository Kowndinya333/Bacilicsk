from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
class Code(models.Model):
    LANGUAGES=(
        ('C', 'C++'),
        ('P', 'Python'),
        ('J', 'Java'),
    )
    name=models.CharField(max_length=30, default='NULL')
    lang=models.CharField(max_length=1, choices=LANGUAGES)
    code=models.TextField()
    coder=models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="codes")

    def __str__(self):
        if self.lang=='C':
            full='C++'
        elif self.lang=='P':
            full='Python'
        else:
            full='Java'
        return "{}({})".format(self.name, full)