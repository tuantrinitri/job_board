from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Bảng kỹ năng nhân viên
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Bảng ca làm việc
class Shift(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Ví dụ: "Ca sáng", "Ca đêm"

    def __str__(self):
        return self.name

# Bảng nhân viên
class Worker(models.Model):
    name = models.CharField(max_length=255)  # Tên nhân viên
    skills = models.ManyToManyField(Skill, related_name="workers")  # Liên kết kỹ năng
    shifts = models.ManyToManyField(Shift, related_name="workers")  # Ca làm việc
    productivity = models.FloatField()  # Năng suất
    salary = models.FloatField()  # Lương cơ bản
    overtime_cost = models.FloatField()  # Chi phí làm thêm giờ

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

# Bảng máy móc
class Machine(models.Model):
    STATUS_CHOICES = [
        ("available", "Sẵn sàng"),
        ("maintenance", "Bảo trì"),
        ("occupied", "Đang sử dụng"),
    ]

    name = models.CharField(max_length=255)  # Tên thiết bị
    type = models.CharField(max_length=255)  # Loại thiết bị
    capacity = models.FloatField()  # Công suất
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")  # Trạng thái
    max_hours_per_day = models.FloatField()  # Giới hạn giờ hoạt động mỗi ngày
    operating_cost = models.FloatField()  # Chi phí vận hành

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

# Bảng công việc
class Job(models.Model):
    PRIORITY_CHOICES = [
        (1, "Thấp"),
        (2, "Trung bình"),
        (3, "Cao"),
        (4, "Rất cao"),
        (5, "Khẩn cấp"),
    ]

    name = models.CharField(max_length=255)  # Tên công việc
    product_type = models.CharField(max_length=255)  # Loại sản phẩm
    quantity = models.IntegerField()  # Số lượng
    deadline = models.DateTimeField()  # Hạn chót
    priority = models.IntegerField(choices=PRIORITY_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    required_skills = models.ManyToManyField(Skill, related_name="jobs")  # Yêu cầu kỹ năng
    required_machine_type = models.CharField(max_length=255)  # Loại thiết bị cần thiết
    predecessor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Công việc trước đó

    def estimated_completion_time(self):
        # Giả định mỗi công việc xử lý 10 sản phẩm/giờ
        estimated_hours = self.quantity / 10  
        return self.deadline - timedelta(hours=estimated_hours)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"
