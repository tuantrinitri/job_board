from ortools.sat.python import cp_model
from django.utils import timezone
from .models import Worker, Machine, Job

def solve_production_scheduling(budget):
    workers = Worker.objects.all()
    machines = Machine.objects.all()
    jobs = Job.objects.all()

    model = cp_model.CpModel()

    horizon = int(max(job.deadline.timestamp() for job in jobs))

    job_intervals = {}
    job_starts = {}
    job_ends = {}
    for job in jobs:
        duration = int(job.quantity / 1)  # Giả định đơn giản
        start_var = model.NewIntVar(0, horizon, f'start_{job.id}')
        end_var = model.NewIntVar(0, horizon, f'end_{job.id}')
        interval_var = model.NewIntervalVar(start_var, duration, end_var, f'interval_{job.id}')
        job_intervals[job.id] = interval_var
        job_starts[job.id] = start_var
        job_ends[job.id] = end_var

    worker_assignments = {}
    machine_assignments = {}
    for job in jobs:
        for worker in workers:
            if job.required_skills in worker.skills:
                worker_assignments[(job.id, worker.id)] = model.NewBoolVar(f'assign_w_{job.id}_{worker.id}')
        for machine in machines:
            if machine.type == job.required_machine_type and machine.status == "sẵn sàng":
                machine_assignments[(job.id, machine.id)] = model.NewBoolVar(f'assign_m_{job.id}_{machine.id}')

    for job in jobs:
        model.AddExactlyOne(worker_assignments[(job.id, w.id)] for w in workers if (job.id, w.id) in worker_assignments)
        model.AddExactlyOne(machine_assignments[(job.id, m.id)] for m in machines if (job.id, m.id) in machine_assignments)

    for worker in workers:
        intervals = [job_intervals[job.id] for job in jobs if (job.id, worker.id) in worker_assignments]
        model.AddNoOverlap(intervals)

    for machine in machines:
        intervals = [job_intervals[job.id] for job in jobs if (job.id, machine.id) in machine_assignments]
        model.AddNoOverlap(intervals)

    for job in jobs:
        model.Add(job_ends[job.id] <= int(job.deadline.timestamp()))

    for job in jobs:
        if job.predecessor:
            model.Add(job_starts[job.id] >= job_ends[job.predecessor.id])

    total_cost = sum(worker.salary * duration * worker_assignments[(job.id, worker.id)]
                     for job in jobs for worker in workers if (job.id, worker.id) in worker_assignments) + \
                 sum(machine.operating_cost * duration * machine_assignments[(job.id, machine.id)]
                     for job in jobs for machine in machines if (job.id, machine.id) in machine_assignments)
    model.Add(total_cost <= budget)

    model.Minimize(total_cost)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = {
            "worker_assignments": [],
            "machine_assignments": [],
            "completed_jobs": [],
            "total_cost": solver.Value(total_cost),
            "jobs_completed": 0,
            "on_time_rate": 0
        }
        completed_jobs = 0
        on_time_jobs = 0
        for job in jobs:
            start_time = solver.Value(job_starts[job.id])
            end_time = solver.Value(job_ends[job.id])
            for worker in workers:
                if (job.id, worker.id) in worker_assignments and solver.Value(worker_assignments[(job.id, worker.id)]):
                    result["worker_assignments"].append({
                        "worker_id": worker.id,
                        "job_id": job.id,
                        "start_time": start_time,
                        "end_time": end_time
                    })
            for machine in machines:
                if (job.id, machine.id) in machine_assignments and solver.Value(machine_assignments[(job.id, machine.id)]):
                    result["machine_assignments"].append({
                        "machine_id": machine.id,
                        "job_id": job.id,
                        "start_time": start_time,
                        "end_time": end_time
                    })
            result["completed_jobs"].append({
                "job_id": job.id,
                "actual_completion": end_time
            })
            completed_jobs += 1
            if end_time <= int(job.deadline.timestamp()):
                on_time_jobs += 1
        
        result["jobs_completed"] = completed_jobs
        result["on_time_rate"] = on_time_jobs / len(jobs) if jobs else 0
        return result
    else:
        return {"error": "Không tìm thấy giải pháp tối ưu"}