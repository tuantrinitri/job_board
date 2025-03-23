from django.contrib import admin

# Register your models here.
from .models import Worker, Machine, Job

admin.site.register(Worker)
admin.site.register(Machine)
admin.site.register(Job)

