### Giải thích đoạn code **Xây dựng biến tổng chi phí và hàm mục tiêu tối ưu**  

#### **1. Tạo biến tổng chi phí (`total_cost_var`)**  
```python
total_cost_var = model.NewIntVar(0, budget, "total_cost")
```
- `total_cost_var` là một biến số nguyên trong khoảng từ `0` đến `budget`.  
- Biến này sẽ lưu tổng chi phí của lịch trình sản xuất (bao gồm chi phí công nhân và chi phí vận hành máy móc).  
- Giá trị này cần được tối ưu hóa để đảm bảo chi phí không vượt quá ngân sách cho phép.

---

#### **2. Ràng buộc tổng chi phí**  
```python
model.Add(
    total_cost_var == sum(
        int(worker.salary * SCALING_FACTOR) * job.quantity * worker_assignments[(job.id, worker.id)]
        for job in jobs for worker in workers if (job.id, worker.id) in worker_assignments
    ) + sum(
        int(machine.operating_cost * SCALING_FACTOR) * job.quantity * machine_assignments[(job.id, machine.id)]
        for job in jobs for machine in machines if (job.id, machine.id) in machine_assignments
    )
)
```
- **Tính toán tổng chi phí nhân công**:  
  ```python
  sum(
      int(worker.salary * SCALING_FACTOR) * job.quantity * worker_assignments[(job.id, worker.id)]
      for job in jobs for worker in workers if (job.id, worker.id) in worker_assignments
  )
  ```
  - `worker.salary * SCALING_FACTOR`: Lương công nhân được nhân với `SCALING_FACTOR` để đảm bảo độ chính xác của phép tính số thực.
  - `job.quantity`: Số lượng công việc cần thực hiện.
  - `worker_assignments[(job.id, worker.id)]`: Biến boolean (`1` nếu công nhân `worker` được gán cho công việc `job`, `0` nếu không).
  - **Tổng hợp chi phí lương** cho tất cả công nhân được gán vào các công việc.

- **Tính toán tổng chi phí vận hành máy móc**:  
  ```python
  sum(
      int(machine.operating_cost * SCALING_FACTOR) * job.quantity * machine_assignments[(job.id, machine.id)]
      for job in jobs for machine in machines if (job.id, machine.id) in machine_assignments
  )
  ```
  - Cách tính tương tự phần lương công nhân, nhưng áp dụng cho chi phí vận hành máy móc.

- **Ràng buộc tổng chi phí**:  
  ```python
  model.Add(total_cost_var == <tổng chi phí nhân công> + <tổng chi phí vận hành máy móc>)
  ```
  - Ràng buộc này đảm bảo `total_cost_var` phản ánh chính xác tổng chi phí sản xuất.

---

#### **3. Định nghĩa hàm mục tiêu tối ưu**  
```python
priority_weight = {1: 1, 2: 2, 3: 3, 4: 5, 5: 10}
model.Minimize(
    total_cost_var - sum(priority_weight[job.priority] * job_starts[job.id] for job in jobs)
)
```
- **Mục tiêu tối ưu hóa**:  
  - **Giảm tổng chi phí** (`total_cost_var`).
  - **Ưu tiên công việc có độ ưu tiên cao hơn**:
    - `job.priority`: Mức độ ưu tiên của công việc (1 là thấp nhất, 5 là cao nhất).
    - `priority_weight[job.priority]`: Trọng số ưu tiên (công việc ưu tiên cao sẽ có trọng số lớn hơn).
    - `job_starts[job.id]`: Thời điểm bắt đầu công việc.
    - **Công thức `sum(priority_weight[job.priority] * job_starts[job.id])` khuyến khích giải pháp lên lịch các công việc có ưu tiên cao càng sớm càng tốt.**

- **Giải thích công thức mục tiêu**:
  ```python
  total_cost_var - sum(priority_weight[job.priority] * job_starts[job.id])
  ```
  - **Tổng chi phí nhỏ nhất** → giúp tối ưu hóa ngân sách.
  - **Công việc quan trọng được bắt đầu sớm hơn** → giúp cải thiện hiệu suất sản xuất.

---

### **Tóm tắt**
1. **Tạo biến tổng chi phí** (`total_cost_var`) để theo dõi tổng chi phí nhân công + máy móc.
2. **Thiết lập ràng buộc** để đảm bảo tổng chi phí bằng tổng tiền lương nhân công và chi phí vận hành máy móc.
3. **Xây dựng hàm mục tiêu**:
   - Giảm tổng chi phí (`total_cost_var`).
   - Cố gắng sắp xếp công việc ưu tiên cao **bắt đầu sớm**.