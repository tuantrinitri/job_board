from ortools.sat.python import cp_model
from django.utils import timezone
from .models import Worker, Machine, Job
from datetime import datetime

SCALING_FACTOR = 100  

def solve_production_scheduling(budget):
    try:
        budget = int(float(budget) * SCALING_FACTOR)  
        if budget < 0:
            return {"error": "Budget cannot be negative"}
    except (ValueError, TypeError):
        return {"error": "Invalid budget value"}

    workers = list(Worker.objects.all())
    machines = list(Machine.objects.all())
    jobs = list(Job.objects.all())

    if not jobs:
        return {"error": "No jobs available for scheduling"}

    model = cp_model.CpModel()
    horizon = max((int(job.deadline.timestamp()) for job in jobs), default=1)

    job_intervals, job_starts, job_ends = {}, {}, {}

    for job in jobs:
        duration = max(1, int(job.quantity))
        start_var = model.NewIntVar(0, horizon, f'start_{job.id}')
        end_var = model.NewIntVar(0, horizon, f'end_{job.id}')
        interval_var = model.NewIntervalVar(start_var, duration, end_var, f'interval_{job.id}')

        job_intervals[job.id] = interval_var
        job_starts[job.id] = start_var
        job_ends[job.id] = end_var

    worker_assignments, machine_assignments = {}, {}

    for job in jobs:
        required_skills = set(job.required_skills.values_list('name', flat=True))

        valid_workers = [w for w in workers if required_skills.issubset(set(w.skills.values_list('name', flat=True)))]
        valid_machines = [m for m in machines if m.type == job.required_machine_type and m.status == "available"]

        if not valid_workers or not valid_machines:
            return {"error": f"Job {job.id} has no suitable workers or machines"}

        for worker in valid_workers:
            worker_assignments[(job.id, worker.id)] = model.NewBoolVar(f'assign_w_{job.id}_{worker.id}')
        for machine in valid_machines:
            machine_assignments[(job.id, machine.id)] = model.NewBoolVar(f'assign_m_{job.id}_{machine.id}')

        model.AddExactlyOne(worker_assignments[(job.id, w.id)] for w in valid_workers)
        model.AddExactlyOne(machine_assignments[(job.id, m.id)] for m in valid_machines)

    for worker in workers:
        model.AddNoOverlap([job_intervals[job.id] for job in jobs if (job.id, worker.id) in worker_assignments])

    for machine in machines:
        model.AddNoOverlap([job_intervals[job.id] for job in jobs if (job.id, machine.id) in machine_assignments])

    for job in jobs:
        model.Add(job_ends[job.id] <= int(job.deadline.timestamp()))
        if job.predecessor and job.predecessor.id in job_ends:
            model.Add(job_starts[job.id] >= job_ends[job.predecessor.id])

    for machine in machines:
        model.Add(
            sum(job.quantity * machine_assignments[(job.id, machine.id)]
                for job in jobs if (job.id, machine.id) in machine_assignments) <= int(machine.max_hours_per_day * SCALING_FACTOR)
        )

    total_cost_var = model.NewIntVar(0, budget, "total_cost")
    model.Add(
        total_cost_var == sum(
            int(worker.salary * SCALING_FACTOR) * job.quantity * worker_assignments[(job.id, worker.id)]
            for job in jobs for worker in workers if (job.id, worker.id) in worker_assignments
        ) + sum(
            int(machine.operating_cost * SCALING_FACTOR) * job.quantity * machine_assignments[(job.id, machine.id)]
            for job in jobs for machine in machines if (job.id, machine.id) in machine_assignments
        )
    )

    priority_weight = {1: 1, 2: 2, 3: 3, 4: 5, 5: 10}
    model.Minimize(total_cost_var - sum(priority_weight[job.priority] * job_starts[job.id] for job in jobs))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30  
    solver.parameters.num_search_workers = 4   

    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        execution_time = solver.WallTime()

        worker_results = []
        machine_results = []
        completed_jobs = []
        jobs_completed = 0
        on_time_jobs = 0

        for job in jobs:
            actual_start = solver.Value(job_starts[job.id])
            actual_end = solver.Value(job_ends[job.id])

            assigned_worker = next((w for w in workers if (job.id, w.id) in worker_assignments and solver.Value(worker_assignments[(job.id, w.id)]) == 1), None)
            assigned_machine = next((m for m in machines if (job.id, m.id) in machine_assignments and solver.Value(machine_assignments[(job.id, m.id)]) == 1), None)

            formatted_start = datetime.fromtimestamp(actual_start).strftime("%d/%m/%y %H:%M")
            formatted_end = datetime.fromtimestamp(actual_end).strftime("%d/%m/%y %H:%M")

            if assigned_worker:
                worker_results.append({
                    "worker_name": assigned_worker.name,
                    "job_id": job.id,
                    "start_time": formatted_start,
                    "end_time": formatted_end
                })

            if assigned_machine:
                machine_results.append({
                    "machine_id": assigned_machine.id,
                    "job_id": job.id,
                    "start_time": formatted_start,
                    "end_time": formatted_end
                })

            completed_jobs.append({
                "job_id": job.id,
                "actual_completion": formatted_end
            })

            jobs_completed += 1
            if actual_end <= int(job.deadline.timestamp()):
                on_time_jobs += 1

        on_time_rate = (on_time_jobs / jobs_completed) * 100 if jobs_completed else 0

        return {
            "worker_assignments": worker_results,
            "machine_assignments": machine_results,
            "completed_jobs": completed_jobs,
            "total_cost": solver.Value(total_cost_var) / SCALING_FACTOR,
            "jobs_completed": jobs_completed,
            "on_time_rate": on_time_rate,
            "execution_time": execution_time
        }

    return {"error": "Không tìm thấy lịch sản xuất phù hợp"}
