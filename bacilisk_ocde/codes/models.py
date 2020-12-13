from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
class Code(models.Model):
    """class that represents the table "Code" in the database.

    Attributes:
        name: name of the file as decided by the user
        lang: programming language in which the code is written
        code: the actual code
        coder: points to the user who stores the code in database.
    """
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