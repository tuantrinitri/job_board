import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.forms import AuthenticationForm

from core.solver import solve_production_scheduling


# Create your views here.
@login_required
def dashboard(request):
    budget = request.GET.get("budget")
    result = solve_production_scheduling(budget)
    return render(request, "dashboard.html", {"result": result})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")  # Nếu có app_name
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def user_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
