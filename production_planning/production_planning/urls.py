from django.contrib import admin
from django.urls import path
from scheduling.views import production_schedule

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schedule/', production_schedule, name='schedule'),
]