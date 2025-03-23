import re
from django.shortcuts import get_object_or_404, redirect, render
from scheduling.models import Job, Machine, Shift, Skill, Worker
from core.solver import solve_production_scheduling


# list worker
def worker(request):
    workers = Worker.objects.all()
    workers_data = [
        {
            "id": worker.id,
            "name": worker.name,
            "productivity": worker.productivity,
            "salary": worker.salary,
            "overtime_cost": worker.overtime_cost,
            "skills": [skill.name for skill in worker.skills.all()],
            "shifts": [shift.name for shift in worker.shifts.all()],
        }
        for worker in workers
    ]

    return render(request, "workers/worker.html", {"workers_data": workers_data})


# add worker
def add_worker(request):
    if request.method == "POST":
        name = request.POST.get("name")
        productivity = request.POST.get("productivity")
        salary = request.POST.get("salary")
        overtime_cost = request.POST.get("overtime_cost")

        # Tạo worker mới
        worker = Worker.objects.create(
            name=name,
            productivity=productivity,
            salary=salary,
            overtime_cost=overtime_cost,
        )

        # Lấy danh sách skills và shifts từ form
        skills = request.POST.getlist("skills")
        shifts = request.POST.getlist("shifts")

        # Gán ManyToMany fields
        worker.skills.set(skills)
        worker.shifts.set(shifts)

        # Chuyển hướng về trang danh sách worker sau khi thêm thành công
        return redirect("worker")

    # Trả về form tạo mới worker
    return render(
        request,
        "workers/form.html",
        {"skills": Skill.objects.all(), "shifts": Shift.objects.all()},
    )


# edit worker
def edit_worker(request, id):
    worker = Worker.objects.get(id=id)

    if request.method == "POST":
        name = request.POST.get("name")  # Lấy giá trị input name
        productivity = request.POST.get("productivity")
        salary = request.POST.get("salary")
        overtime_cost = request.POST.get("overtime_cost")

        skills = request.POST.getlist("skills")  # Dùng getlist để lấy nhiều giá trị
        shifts = request.POST.getlist("shifts")

        # Cập nhật worker
        worker.name = name
        worker.productivity = productivity
        worker.salary = salary
        worker.overtime_cost = overtime_cost
        worker.skills.set(skills)  # Gán ManyToMany
        worker.shifts.set(shifts)
        worker.save()

        return redirect("worker")  # Chuyển hướng về trang danh sách nhân viên

    return render(
        request,
        "workers/form.html",
        {
            "worker": worker,
            "skills": Skill.objects.all(),
            "shifts": Shift.objects.all(),
        },
    )


# delete worker
def delete_worker(request, id):
    worker = Worker.objects.get(id=id)
    worker.delete()
    return redirect("worker")


def list_machine(request):
    machines = Machine.objects.all()
    machines_data = [
        {
            "id": machine.id,
            "name": machine.name,
            "type": machine.type,
            "capacity": machine.capacity,
            "status": machine.status,
            "max_hours_per_day": machine.max_hours_per_day,
            "operating_cost": machine.operating_cost,
        }
        for machine in machines
    ]
    return render(request, "machines/machines.html", {"machines_data": machines_data})


def add_machine(request):
    if request.method == "POST":
        name = request.POST.get("name")
        type = request.POST.get("type")
        capacity = request.POST.get("capacity")
        status = request.POST.get("status")
        max_hours_per_day = request.POST.get("max_hours_per_day")
        operating_cost = request.POST.get("operating_cost")
        Machine.objects.create(
            name=name,
            type=type,
            capacity=capacity,
            status=status,
            max_hours_per_day=max_hours_per_day,
            operating_cost=operating_cost,
        )
        return redirect("machines")
    return render(request, "machines/form.html", {"machine": {}})


def edit_machine(request, id):
    machine = get_object_or_404(Machine, id=id)
    if request.method == "POST":
        machine.name = request.POST.get("name")
        machine.type = request.POST.get("type")
        machine.capacity = request.POST.get("capacity")
        machine.status = request.POST.get("status")
        machine.max_hours_per_day = request.POST.get("max_hours_per_day")
        machine.operating_cost = request.POST.get("operating_cost")
        machine.save()
        return redirect("machines")
    return render(request, "machines/form.html", {"machine": machine})


def delete_machine(request, id):
    machine = Machine.objects.get(id=id)
    machine.delete()
    return redirect("machines")


def jobs(request):
    jobs = Job.objects.all()
    return render(request, "jobs/job.html", {"jobs": jobs})


def add_job(request):
    if request.method == "POST":
        name = request.POST.get("name")
        product_type = request.POST.get("product_type")
        quantity = request.POST.get("quantity")
        deadline = request.POST.get("deadline")
        priority = request.POST.get("priority")
        required_skills = request.POST.getlist("required_skills")
        required_machine_type = request.POST.get("required_machine_type")
        predecessor_id = request.POST.get("predecessor")
        predecessor = Job.objects.get(id=predecessor_id) if predecessor_id else None

        job = Job.objects.create(
            name=name,
            product_type=product_type,
            quantity=quantity,
            deadline=deadline,
            priority=priority,
            required_machine_type=required_machine_type,
            predecessor=predecessor,
        )
        job.required_skills.set(required_skills)
        return redirect("jobs")

    all_skills = Skill.objects.all()
    all_jobs = Job.objects.all()
    all_machines = Machine.objects.all()
    return render(
        request,
        "jobs/form.html",
        {"skills": all_skills, "jobs": all_jobs, "machines": all_machines},
    )


def edit_job(request, id):
    job = get_object_or_404(Job, id=id)
    if request.method == "POST":
        job.name = request.POST.get("name")
        job.product_type = request.POST.get("product_type")
        job.quantity = request.POST.get("quantity")
        job.deadline = request.POST.get("deadline")
        job.priority = request.POST.get("priority")
        required_skills = request.POST.getlist("required_skills")
        job.required_machine_type = request.POST.get("required_machine_type")
        predecessor_id = request.POST.get("predecessor")
        job.predecessor = Job.objects.get(id=predecessor_id) if predecessor_id else None

        job.required_skills.set(required_skills)
        job.save()
        return redirect("jobs")

    all_skills = Skill.objects.all()
    all_jobs = Job.objects.all()
    all_machines = Machine.objects.all()
    return render(
        request,
        "jobs/form.html",
        {"job": job, "skills": all_skills, "jobs": all_jobs, "machines": all_machines},
    )


def delete_job(request, id):
    job = Job.objects.get(id=id)
    job.delete()
    return redirect("jobs")


def production_schedule(request):
    budget = 1000000  # Ngân sách cố định (có thể lấy từ request)
    result = solve_production_scheduling(budget)
    return render(request, "schedule.html", {"result": result})
