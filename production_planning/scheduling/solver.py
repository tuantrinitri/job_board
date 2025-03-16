# Import thư viện OR-Tools để giải quyết bài toán tối ưu hóa
from ortools.sat.python import cp_model
# Import timezone từ Django để xử lý thời gian
from django.utils import timezone
# Import các model từ ứng dụng hiện tại
from .models import Worker, Machine, Job

# Hàm giải quyết bài toán lập lịch sản xuất với ngân sách cho trước


def solve_production_scheduling(budget):
    budget = int(budget)  # Chuyển đổi ngân sách sang kiểu số nguyên
    try:
        budget = int(float(budget))  # Converts string or float to int
        if budget < 0:
            raise ValueError("Budget cannot be negative")
    except (ValueError, TypeError):
        return {"error": "Invalid budget value"}
    # Lấy tất cả dữ liệu về công nhân, máy móc và công việc từ cơ sở dữ liệu
    workers = Worker.objects.all()
    machines = Machine.objects.all()
    jobs = Job.objects.all()

    # Khởi tạo mô hình tối ưu hóa ràng buộc
    model = cp_model.CpModel()

    # Tính toán chân trời gand  lập kế hoạch là deadline xa nhất của tất cả công việc (đơn vị timestamp)
    horizon = int(max(job.deadline.timestamp() for job in jobs))

    # Tạo các biến quyết định cho mỗi công việc
    job_intervals = {}
    job_starts = {}
    job_ends = {}
    for job in jobs:
        # Ước tính thời gian thực hiện công việc dựa trên số lượng
        duration = int(job.quantity / 1)  # Giả định đơn giản
        # Biến thời điểm bắt đầu công việc
        start_var = model.NewIntVar(0, horizon, f'start_{job.id}')
        # Biến thời điểm kết thúc công việc
        end_var = model.NewIntVar(0, horizon, f'end_{job.id}')
        # Biến khoảng thời gian của công việc
        interval_var = model.NewIntervalVar(
            start_var, duration, end_var, f'interval_{job.id}')
        # Lưu các biến vào dictionary để dễ sử dụng sau này
        job_intervals[job.id] = interval_var
        job_starts[job.id] = start_var
        job_ends[job.id] = end_var

    # Tạo các biến quyết định cho việc phân công công nhân và máy móc
    worker_assignments = {}
    machine_assignments = {}
    for job in jobs:
        # Chỉ xem xét công nhân có kỹ năng phù hợp với công việc
        for worker in workers:
            if job.required_skills in worker.skills:
                worker_assignments[(job.id, worker.id)] = model.NewBoolVar(
                    f'assign_w_{job.id}_{worker.id}')
        # Chỉ xem xét máy có loại phù hợp và đang sẵn sàng
        for machine in machines:
            if machine.type == job.required_machine_type and machine.status == "sẵn sàng":
                machine_assignments[(job.id, machine.id)] = model.NewBoolVar(
                    f'assign_m_{job.id}_{machine.id}')

    # Ràng buộc mỗi công việc phải được gán đúng một công nhân và một máy phù hợp
    for job in jobs:
        model.AddExactlyOne(worker_assignments[(job.id, w.id)] for w in workers if (
            job.id, w.id) in worker_assignments)
        model.AddExactlyOne(machine_assignments[(job.id, m.id)] for m in machines if (
            job.id, m.id) in machine_assignments)

    # Ràng buộc một công nhân không thể làm nhiều công việc cùng lúc
    for worker in workers:
        intervals = [job_intervals[job.id]
                     for job in jobs if (job.id, worker.id) in worker_assignments]
        model.AddNoOverlap(intervals)

    # Ràng buộc một máy không thể thực hiện nhiều công việc cùng lúc
    for machine in machines:
        intervals = [job_intervals[job.id]
                     for job in jobs if (job.id, machine.id) in machine_assignments]
        model.AddNoOverlap(intervals)

    # Ràng buộc mỗi công việc phải hoàn thành trước deadline
    for job in jobs:
        model.Add(job_ends[job.id] <= int(job.deadline.timestamp()))

    # Ràng buộc thứ tự công việc: nếu có công việc tiên quyết thì phải hoàn thành trước
    for job in jobs:
        if job.predecessor:
            model.Add(job_starts[job.id] >= job_ends[job.predecessor.id])

    # Tính tổng chi phí dựa trên lương công nhân và chi phí vận hành máy móc
    # Tính tổng chi phí dựa trên lương công nhân và chi phí vận hành máy móc
    total_cost = sum(int(worker.salary) * duration * worker_assignments[(job.id, worker.id)]
                     for job in jobs for worker in workers if (job.id, worker.id) in worker_assignments) + \
        sum(int(machine.operating_cost) * duration * machine_assignments[(job.id, machine.id)]
            for job in jobs for machine in machines if (job.id, machine.id) in machine_assignments)
    # Ràng buộc tổng chi phí không vượt quá ngân sách
    model.Add(total_cost <= budget)

    # Mục tiêu tối ưu: tối thiểu hóa tổng chi phí
    model.Minimize(total_cost)

    # Khởi tạo solver và giải quyết mô hình
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Xử lý kết quả nếu tìm được giải pháp
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = {
            "worker_assignments": [],
            "machine_assignments": [],
            "completed_jobs": [],
            "total_cost": solver.Value(total_cost),
            "jobs_completed": 0,
            "on_time_rate": 0
        }
        # Đếm số công việc hoàn thành và số công việc hoàn thành đúng hạn
        completed_jobs = 0
        on_time_jobs = 0
        for job in jobs:
            # Lấy thời gian bắt đầu và kết thúc thực tế của công việc
            start_time = solver.Value(job_starts[job.id])
            end_time = solver.Value(job_ends[job.id])
            # Xác định công nhân nào được gán cho công việc này
            for worker in workers:
                if (job.id, worker.id) in worker_assignments and solver.Value(worker_assignments[(job.id, worker.id)]):
                    result["worker_assignments"].append({
                        "worker_id": worker.id,
                        "job_id": job.id,
                        "start_time": start_time,
                        "end_time": end_time
                    })
            # Xác định máy nào được gán cho công việc này
            for machine in machines:
                if (job.id, machine.id) in machine_assignments and solver.Value(machine_assignments[(job.id, machine.id)]):
                    result["machine_assignments"].append({
                        "machine_id": machine.id,
                        "job_id": job.id,
                        "start_time": start_time,
                        "end_time": end_time
                    })
            # Thêm thông tin về công việc hoàn thành vào kết quả
            result["completed_jobs"].append({
                "job_id": job.id,
                "actual_completion": end_time
            })
            completed_jobs += 1
            # Kiểm tra xem công việc có hoàn thành đúng hạn không
            if end_time <= int(job.deadline.timestamp()):
                on_time_jobs += 1

        # Cập nhật tỷ lệ hoàn thành đúng hạn và trả về kết quả
        result["jobs_completed"] = completed_jobs
        result["on_time_rate"] = on_time_jobs / len(jobs) if jobs else 0
        return result
    else:
        # Trả về thông báo lỗi nếu không tìm được giải pháp
        return {"error": "Không tìm thấy giải pháp tối ưu"}
