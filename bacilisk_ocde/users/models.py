from django.db import models
from django.db.models.fields.related import ForeignKey
from django.contrib.auth import get_user_model
# Create your models here.
class MyUser(models.Model):
    """Class that stores the subscription information of the user.
    
    Attributes:
        Paid_User: It is 'Y' if the user is subscribed and 'N' if not
        relatedUser": It points to which user we are speaking of
    """
    STATUS=(
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    Paid_User=models.CharField(max_length=1, default='N')
    relatedUser=ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="subscription")
