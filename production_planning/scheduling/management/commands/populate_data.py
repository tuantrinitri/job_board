from django.utils import timezone
from scheduling.models import Skill, Worker, Machine, Job, Shift

Skill.objects.all().delete()
Worker.objects.all().delete()
Machine.objects.all().delete()
Job.objects.all().delete()
Shift.objects.all().delete()

# Tạo kỹ năng
skill_welding = Skill.objects.create(name="Hàn")
skill_assembly = Skill.objects.create(name="Lắp ráp")
skill_painting = Skill.objects.create(name="Sơn")

# Tạo ca làm việc
shift_morning = Shift.objects.create(name="Ca sáng")
shift_night = Shift.objects.create(name="Ca đêm")

# Tạo nhân viên với kỹ năng và ca làm việc
worker1 = Worker.objects.create(
    name="Nguyễn Văn A", productivity=1.2, salary=200, overtime_cost=50
)
worker1.skills.add(skill_welding)
worker1.shifts.add(shift_morning)

worker2 = Worker.objects.create(
    name="Trần Thị B", productivity=1.0, salary=180, overtime_cost=45
)
worker2.skills.add(skill_assembly)
worker2.shifts.add(shift_night)

worker3 = Worker.objects.create(
    name="Lê Văn C", productivity=1.5, salary=220, overtime_cost=60
)
worker3.skills.add(skill_painting)
worker3.shifts.add(shift_morning)

# Tạo máy móc phù hợp với công việc
machine_welding = Machine.objects.create(
    name="Máy Hàn 1",
    type="Hàn",
    capacity=10,
    status="available",
    max_hours_per_day=8,
    operating_cost=30,
)
machine_assembly = Machine.objects.create(
    name="Máy Lắp ráp 1",
    type="Lắp ráp",
    capacity=8,
    status="available",
    max_hours_per_day=8,
    operating_cost=25,
)
machine_painting = Machine.objects.create(
    name="Máy Sơn 1",
    type="Sơn",
    capacity=12,
    status="available",
    max_hours_per_day=8,
    operating_cost=40,
)

# Tạo công việc phù hợp với nhân viên và máy móc
job1 = Job.objects.create(
    name="Hàn khung thép",
    product_type="Khung thép",
    quantity=50,
    deadline=timezone.now() + timezone.timedelta(days=2),
    priority=3,
    required_machine_type="Hàn",
)
job1.required_skills.add(skill_welding)

job2 = Job.objects.create(
    name="Lắp ráp thiết bị",
    product_type="Thiết bị",
    quantity=40,
    deadline=timezone.now() + timezone.timedelta(days=3),
    priority=4,
    required_machine_type="Lắp ráp",
)
job2.required_skills.add(skill_assembly)

job3 = Job.objects.create(
    name="Sơn bề mặt",
    product_type="Bề mặt",
    quantity=30,
    deadline=timezone.now() + timezone.timedelta(days=1),
    priority=5,
    required_machine_type="Sơn",
)
job3.required_skills.add(skill_painting)

print("✅ Dữ liệu chuẩn đã được tạo thành công!")
