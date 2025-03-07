from django.shortcuts import render
from .solver import solve_production_scheduling

def production_schedule(request):
    budget = 10000  # Ngân sách cố định (có thể lấy từ request)
    result = solve_production_scheduling(budget)
    return render(request, 'schedule.html', {'result': result})