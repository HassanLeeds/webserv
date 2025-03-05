from django.db import models

# Create your models here.
class Professor (models.Model):
    id = models.CharField(unique=True, max_length = 10, primary_key=True)
    name = models.CharField(max_length = 30)
    
    def __str__ (self):
        return self.name

class Module (models.Model):
    code = models.CharField(unique=True, max_length = 10, primary_key=True)
    desc = models.CharField(max_length = 100)
    prof = models.ManyToManyField(Professor)
    year = models.IntegerField()

    def __str__ (self):
        return self.desc

class Rating (models.Model):
    stars = models.IntegerField()
    professor = models.ForeignKey(Professor, on_delete=models.PROTECT)
    module = models.ForeignKey(Module, on_delete=models.PROTECT)
