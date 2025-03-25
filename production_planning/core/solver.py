from ortools.sat.python import cp_model
from django.utils import timezone
from scheduling.models import Worker, Machine, Job
from datetime import datetime

SCALING_FACTOR = 100  # Hệ số nhân để xử lý số thực chính xác hơn


def solve_production_scheduling(budget):
    try:
        # Chuyển đổi ngân sách thành số nguyên để xử lý
        budget = int(float(budget) * SCALING_FACTOR)
        if budget < 0:
            return {"error": "Ngân sách không thể âm"}
    except (ValueError, TypeError):
        return {"error": "Giá trị ngân sách không hợp lệ"}

    # Lấy danh sách công nhân, máy móc và công việc từ cơ sở dữ liệu
    workers = list(Worker.objects.all())
    machines = list(Machine.objects.all())
    jobs = list(Job.objects.all())

    if not jobs:
        return {"error": "Không có công việc để lập lịch"}

    model = cp_model.CpModel()
    # khung thời gian tối đa để hoàn thành công việc
    horizon = max((int(job.deadline.timestamp()) for job in jobs), default=1)

    job_intervals, job_starts, job_ends = {}, {}, {}

    # Khởi tạo biến quyết định cho mỗi công việc
    for job in jobs:
        duration = max(1, int(job.quantity))  # Thời lượng thực hiện công việc
        start_var = model.NewIntVar(0, horizon, f"start_{job.id}")
        end_var = model.NewIntVar(0, horizon, f"end_{job.id}")
        interval_var = model.NewIntervalVar(
            start_var, duration, end_var, f"interval_{job.id}"
        )

        job_intervals[job.id] = interval_var
        job_starts[job.id] = start_var
        job_ends[job.id] = end_var

    worker_assignments, machine_assignments = {}, {}

    # Gán công nhân và máy móc phù hợp cho từng công việc
    for job in jobs:
        required_skills = set(job.required_skills.values_list("name", flat=True))

        valid_workers = [
            w
            for w in workers
            if required_skills.issubset(set(w.skills.values_list("name", flat=True)))
        ]
        valid_machines = [
            m
            for m in machines
            if m.type == job.required_machine_type and m.status == "available"
        ]

        if not valid_workers or not valid_machines:
            return {
                "error": f"Công việc {job.id} không có công nhân hoặc máy móc phù hợp"
            }

        for worker in valid_workers:
            worker_assignments[(job.id, worker.id)] = model.NewBoolVar(
                f"assign_w_{job.id}_{worker.id}"
            )
        for machine in valid_machines:
            machine_assignments[(job.id, machine.id)] = model.NewBoolVar(
                f"assign_m_{job.id}_{machine.id}"
            )

        # Đảm bảo mỗi công việc có đúng một công nhân và một máy móc
        model.AddExactlyOne(worker_assignments[(job.id, w.id)] for w in valid_workers)
        model.AddExactlyOne(machine_assignments[(job.id, m.id)] for m in valid_machines)

    # Ràng buộc lịch trình công nhân
    for worker in workers:
        model.AddNoOverlap(
            [
                job_intervals[job.id]
                for job in jobs
                if (job.id, worker.id) in worker_assignments
            ]
        )

    # Ràng buộc lịch trình máy móc
    for machine in machines:
        model.AddNoOverlap(
            [
                job_intervals[job.id]
                for job in jobs
                if (job.id, machine.id) in machine_assignments
            ]
        )

    # Ràng buộc thời gian hoàn thành công việc và thứ tự thực hiện
    for job in jobs:
        model.Add(job_ends[job.id] <= int(job.deadline.timestamp()))
        if job.predecessor and job.predecessor.id in job_ends:
            model.Add(job_starts[job.id] >= job_ends[job.predecessor.id])

    # Giới hạn giờ làm việc của máy móc
    for machine in machines:
        model.Add(
            sum(
                job.quantity * machine_assignments[(job.id, machine.id)]
                for job in jobs
                if (job.id, machine.id) in machine_assignments
            )
            <= int(machine.max_hours_per_day * SCALING_FACTOR)
        )

    # Xây dựng biến tổng chi phí và hàm mục tiêu tối ưu
    total_cost_var = model.NewIntVar(0, budget, "total_cost")
    model.Add(
        total_cost_var
        == sum(
            int(worker.salary * SCALING_FACTOR)
            * job.quantity
            * worker_assignments[(job.id, worker.id)]
            for job in jobs
            for worker in workers
            if (job.id, worker.id) in worker_assignments
        )
        + sum(
            int(machine.operating_cost * SCALING_FACTOR)
            * job.quantity
            * machine_assignments[(job.id, machine.id)]
            for job in jobs
            for machine in machines
            if (job.id, machine.id) in machine_assignments
        )
    )

    priority_weight = {1: 1, 2: 2, 3: 3, 4: 5, 5: 10}
    model.Minimize(
        total_cost_var
        - sum(priority_weight[job.priority] * job_starts[job.id] for job in jobs)
    )

    # Thiết lập bộ giải ràng buộc
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30  # thời gian toi da thuc hien trong
    solver.parameters.num_search_workers = 4  # thay đổi trong request

    status = solver.Solve(model)

    # Xử lý kết quả tối ưu
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        execution_time = solver.WallTime()
        worker_results, machine_results, completed_jobs = [], [], []
        jobs_completed, on_time_jobs = 0, 0

        for job in jobs:
            actual_start = solver.Value(job_starts[job.id])
            actual_end = solver.Value(job_ends[job.id])

            assigned_worker = next(
                (
                    w
                    for w in workers
                    if (job.id, w.id) in worker_assignments
                    and solver.Value(worker_assignments[(job.id, w.id)]) == 1
                ),
                None,
            )
            assigned_machine = next(
                (
                    m
                    for m in machines
                    if (job.id, m.id) in machine_assignments
                    and solver.Value(machine_assignments[(job.id, m.id)]) == 1
                ),
                None,
            )

            formatted_start = datetime.fromtimestamp(actual_start).strftime(
                "%d/%m/%y %H:%M"
            )
            formatted_end = datetime.fromtimestamp(actual_end).strftime(
                "%d/%m/%y %H:%M"
            )

            if assigned_worker:
                worker_results.append(
                    {
                        "worker_name": assigned_worker.name,
                        "job_id": job.name,
                        "start_time": formatted_start,
                        "end_time": formatted_end,
                    }
                )
            if assigned_machine:
                machine_results.append(
                    {
                        "machine_id": assigned_machine.name,
                        "job_id": job.name,
                        "start_time": formatted_start,
                        "end_time": formatted_end,
                    }
                )

            completed_jobs.append(
                {"job_id": job.name, "actual_completion": formatted_end}
            )
            jobs_completed += 1
            if actual_end <= int(job.deadline.timestamp()):
                on_time_jobs += 1

        return {
            # "execution_time": execution_time,
            "jobs_completed": jobs_completed,
            "on_time_rate": on_time_jobs / jobs_completed,
            "worker_assignments": worker_results,
            "machine_assignments": machine_results,
            "completed_jobs": completed_jobs,
            "total_cost": solver.Value(total_cost_var) / SCALING_FACTOR,
        }

    return {"error": "Không tìm thấy lịch sản xuất phù hợp"}
