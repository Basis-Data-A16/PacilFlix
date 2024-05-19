from django.db import models
from django.contrib.auth.models import User

#class Ulasan(models.Model):
#    id_tayangan = models.ForeignKey(, on_delete=models.CASCADE)
#    username = models.ForeignKey(User, on_delete=models.CASCADE)
#    timestamp = models.DateTimeField(auto_now_add=True)
#    rating = models.IntegerField(default=0)
#    deskripsi = models.TextField()

#    class Meta:
#        unique_together = ('id_tayangan', 'username')