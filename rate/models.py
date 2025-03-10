from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Professor (models.Model):
    id = models.CharField(unique=True, max_length = 8, primary_key=True)
    name = models.CharField(max_length = 40)
    
    def __str__ (self):
        return self.name

class Module (models.Model):
    code = models.CharField(unique=True, max_length = 10, primary_key=True)
    desc = models.CharField(max_length = 100)

    def __str__ (self):
        return self.desc

class Module_instance (models.Model):
    prof = models.ManyToManyField(Professor)
    year = models.IntegerField()
    sem = models.IntegerField(choices={1:"1",2:"2"}, null=True)
    mod = models.ForeignKey(Module, on_delete=models.PROTECT)
    
    def __str__ (self):
        return f"{self.mod.code} {self.year} {self.sem}"


class Rating (models.Model):
    stars = models.IntegerField()
    professor = models.ForeignKey(Professor, on_delete=models.PROTECT)
    module = models.ForeignKey(Module_instance, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    class Meta:
        # Ensure a user can only rate a specific professor for a specific module instance once
        unique_together = ('user', 'professor', 'module')


