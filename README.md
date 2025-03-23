Dưới đây là nội dung README hướng dẫn sử dụng cho ứng dụng lập kế hoạch sản xuất, được viết bằng tiếng Việt theo yêu cầu của bạn:

---

# README: Ứng Dụng Lập Kế Hoạch Sản Xuất

## Giới thiệu
Ứng dụng này được thiết kế để hỗ trợ lập kế hoạch sản xuất tối ưu, giúp phân bổ nhân lực và thiết bị cho các công việc sản xuất dựa trên các ràng buộc như kỹ năng, thời gian, chi phí và công việc tiền nhiệm. Ứng dụng sử dụng **Python Django** để quản lý dữ liệu và giao diện, kết hợp với **Google OR-Tools** để giải bài toán lập lịch một cách hiệu quả.

## Yêu cầu hệ thống
- **Phần mềm**:
  - Python 3.7 hoặc cao hơn
  - Django 3.0 hoặc cao hơn
  - Google OR-Tools
- **Phần cứng**:
  - Không có yêu cầu đặc biệt, có thể chạy trên máy tính cá nhân thông thường.

## Cài đặt
Để cài đặt và chạy ứng dụng, làm theo các bước sau:

1. **Cài đặt Python**  
   Nếu chưa có Python, tải và cài đặt từ [python.org](https://www.python.org/).

2. **Cài đặt các thư viện cần thiết**  
   Mở terminal và chạy các lệnh sau:
   ```
   pip install django
   pip install ortools
   ```
3. **Thiết lập models**  
   File `scheduling/models.py` để định nghĩa các mô hình dữ liệu như `Worker`, `Machine`, và `Job`.

4. **Đăng ký models trong admin**  
    `scheduling/admin.py` để quản lý dữ liệu qua giao diện admin.

5. **Tạo và áp dụng migrations**  
   Chạy các lệnh sau để tạo bảng cơ sở dữ liệu:
   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py populate_data 
   ```
   Chú ý: lệnh python manage.py populate_data  là lệnh tạo dữ liệu chuẩn, dữ liệu càng nhiều thì điều chỉnh tham số buget trong file production_planning/core/views.py càng lớn sẽ ra kết quả

6. **Tạo tài khoản quản trị (superuser)**  
   Chạy lệnh sau và làm theo hướng dẫn để tạo tài khoản:
   ```
   python manage.py createsuperuser
   ```

7. **Thêm dữ liệu mẫu**  
   Khởi động server bằng lệnh:
   ```
   python manage.py runserver
   ```
   Sau đó, truy cập `http://127.0.0.1:8000/admin` để thêm dữ liệu cho `Worker` (nhân viên), `Machine` (thiết bị), và `Job` (công việc).

8.  **File solver**  
     `scheduling/solver.py` để xử lý bài toán lập lịch.

## Cấu hình
- Ứng dụng không yêu cầu cấu hình đặc biệt. Tuy nhiên, hãy đảm bảo rằng dữ liệu đã được nhập đầy đủ và chính xác thông qua giao diện admin trước khi sử dụng.

## Sử dụng
1. **Khởi động server**  
   Chạy lệnh sau trong terminal:
   ```
   python manage.py runserver
   ```

2. **Truy cập ứng dụng**  
   Mở trình duyệt và truy cập địa chỉ:
   ```
   http://127.0.0.1:8000/schedule/
   ```
   Trang này sẽ hiển thị lịch trình sản xuất đã được tối ưu.

3. **Nhập dữ liệu**  
   - Truy cập giao diện admin tại `http://127.0.0.1:8000/admin`.
   - Thêm, sửa hoặc xóa thông tin về nhân viên (`Worker`), thiết bị (`Machine`), và công việc (`Job`) theo nhu cầu.

4. **Xem kết quả**  
   Sau khi nhập dữ liệu, truy cập lại `/schedule/` để xem kế hoạch sản xuất, bao gồm:
   - Phân bổ nhân lực và thiết bị cho từng công việc.
   - Thông tin chi tiết về thời gian hoàn thành và chi phí (nếu có).

## Giải thích về OR-Tools
**Google OR-Tools** là một thư viện mã nguồn mở do Google phát triển, được sử dụng để giải các bài toán tối ưu hóa như lập lịch, phân bổ tài nguyên, và nhiều bài toán phức tạp khác. Trong ứng dụng này, OR-Tools đóng vai trò mô hình hóa bài toán lập kế hoạch sản xuất và tìm ra giải pháp tối ưu dựa trên các ràng buộc về kỹ năng, thời gian, và tài nguyên.

## Lưu ý
- **Dữ liệu đầu vào**: Đảm bảo rằng thông tin về nhân viên, thiết bị và công việc đã được nhập đầy đủ trước khi chạy ứng dụng. Nếu dữ liệu thiếu hoặc không hợp lệ, kết quả có thể không chính xác.
- **Thời gian thực hiện**: Trong phiên bản cơ bản, thời gian hoàn thành công việc (`duration`) được tính đơn giản dựa trên số lượng sản phẩm. Bạn có thể tùy chỉnh logic này trong `solver.py` để phù hợp hơn với thực tế.
- **Ràng buộc**: Ứng dụng giả định rằng tất cả công việc đều có thể hoàn thành trong khoảng thời gian cho phép. Nếu không khả thi, hãy kiểm tra lại dữ liệu hoặc điều chỉnh các ràng buộc.

## Giải quyết vấn đề
- **Lỗi "Không tìm thấy giải pháp tối ưu"**  
  - Kiểm tra dữ liệu đầu vào trong admin, đặc biệt là kỹ năng của nhân viên, loại thiết bị, và thời hạn công việc.
  - Đảm bảo có đủ tài nguyên (nhân viên và thiết bị) phù hợp với yêu cầu của từng công việc.

- **Lỗi khi cài đặt OR-Tools**  
  - Xác minh phiên bản Python đang sử dụng (phải là 3.7 trở lên).
  - Thử cài đặt lại bằng lệnh:
    ```
    pip install ortools
    ```

- **Lỗi khi truy cập trang `/schedule/`**  
  - Đảm bảo server đang chạy bằng lệnh `python manage.py runserver`.
  - Kiểm tra file `urls.py` để xác nhận rằng đường dẫn đã được cấu hình đúng.

---