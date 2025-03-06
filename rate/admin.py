from django.contrib import admin

# Register your models here.
from .models import Professor, Module, Rating, Module_instance
from django.contrib.auth.models import User

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(Module_instance)
admin.site.register(Rating)
