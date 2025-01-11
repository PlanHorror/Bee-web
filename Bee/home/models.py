from django.db import models
from django.contrib.auth.models import User
User._meta.get_field('email').blank = True
User._meta.get_field('email').null = True
# Create your models here.
class Bee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    return_video = models.FileField(upload_to='return_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username