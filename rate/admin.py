from django.contrib import admin

# Register your models here.
from .models import Professor, Module, Rating
from django.contrib.auth.models import User

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(Rating)
