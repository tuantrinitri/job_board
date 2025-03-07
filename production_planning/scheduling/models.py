from django.db import models

class Worker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)    # Tên nhân viên
    skills = models.CharField(max_length=255)  # Kỹ năng của nhân viên
    productivity = models.FloatField()         # Năng suất
    available_shifts = models.CharField(max_length=255)  # Ca làm việc khả dụng
    salary = models.FloatField()               # Lương cơ bản
    overtime_cost = models.FloatField()        # Chi phí làm thêm giờ

    def __str__(self):
        return f"Worker {self.id}"

class Machine(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)    # Tên thiết bị
    type = models.CharField(max_length=255)    # Loại thiết bị
    capacity = models.FloatField()             # Công suất
    status = models.CharField(max_length=50)   # Trạng thái (ví dụ: sẵn sàng, bảo trì)
    max_hours_per_day = models.FloatField()    # Số giờ tối đa mỗi ngày
    operating_cost = models.FloatField()       # Chi phí vận hành

    def __str__(self):
        return f"Machine {self.id}"

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)    # Tên công việc
    product_type = models.CharField(max_length=255)  # Loại sản phẩm
    quantity = models.IntegerField()           # Số lượng
    deadline = models.DateTimeField()          # Thời hạn hoàn thành
    priority = models.IntegerField()           # Độ ưu tiên
    required_skills = models.CharField(max_length=255)  # Kỹ năng cần thiết
    required_machine_type = models.CharField(max_length=255)  # Loại thiết bị cần thiết
    predecessor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Công việc trước đó

    def __str__(self):
        return f"Job {self.id}"