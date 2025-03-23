from platform import machine
from django.contrib import admin
from django.urls import path
from scheduling.views import (
    add_job,
    add_machine,
    add_worker,
    delete_job,
    delete_machine,
    delete_worker,
    edit_job,
    edit_machine,
    edit_worker,
    jobs,
    list_machine,
    production_schedule,
    worker,
)
from core import views as core_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # login
    path("login/", core_views.user_login, name="login"),
    path("logout/", core_views.logout, name="logout"),
    path("admin/", admin.site.urls),  # Đây là trang admin Django
    path("dashboard/", core_views.dashboard, name="dashboard"),
    path("worker/", worker, name="worker"),
    # create
    path("worker/create/", add_worker, name="worker_create"),
    # edit worker
    path("worker/<int:id>/", edit_worker, name="worker_edit"),
    # delete worker
    path("worker/delete/<int:id>/", delete_worker, name="worker_delete"),
    # list machine
    path("machines/", list_machine, name="machines"),
    # create machine
    path("machine/create/", add_machine, name="machine_create"),
    # edit machine
    path("machine/<int:id>/", edit_machine, name="machine_edit"),
    # delete machine
    path("machine/delete/<int:id>/", delete_machine, name="machine_delete"),
    path("jobs/", jobs, name="jobs"),
    # create job
    path("job/create/", add_job, name="job_create"),
    # edit job
    path("job/<int:id>/", edit_job, name="job_edit"),
    # delete job
    path("job/delete/<int:id>/", delete_job, name="job_delete"),
    path("production-schedule/", production_schedule, name="production_schedule"),
]
