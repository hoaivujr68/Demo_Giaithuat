# Giải Thuật Phân Công Giảng Dạy và Phân Công Hướng Dẫn Đồ Án

## Mô Tả

Giải thuật phân công giảng dạy và phân công hướng dẫn đồ án nhằm tối ưu hóa việc phân bổ các giảng viên cho các môn học và hướng dẫn sinh viên làm đồ án, dựa trên một số ràng buộc và mục tiêu. Mục tiêu của giải thuật là:

 + Đảm bảo các giảng viên được phân công đúng môn học mà họ có khả năng giảng dạy.
 + Giảm thiểu sự trùng lặp trong lịch giảng dạy.
 + Tối ưu hóa khối lượng công việc của giảng viên, sao cho không giảng viên nào bị phân công quá nhiều công việc (giới hạn số giờ dạy).
 + Cân đối giữa các giảng viên để đảm bảo công bằng trong phân công công việc.
 + Ràng buộc:
     (1) Mỗi lớp chỉ có thể có một giáo viên dạy
     (2) Mỗi giảng viên chỉ dạy được 1 lớp trong 1 thời điểm
     (3) Giảng viên chỉ dạy các học phần thuộc nhóm chuyên môn tham gia
     (4) Mỗi giảng viên nhận hướng dẫn tối đa 5 sinh viên/học phần đồ án/kỳ
     (5) Các nguyện vọng đồ án đều được chỉ định chính xác 1 giáo viên hướng dẫn
     (6) Phân công hướng dẫn theo nguyện vọng 1, 2, 3 của sinh viên
     (7) Tổng giờ hướng dẫn và giờ giảng dạy: GD <= số giờ GD trung bình-NC-PVQL
     (8) Mỗi giảng viên hướng dẫn tối đa 30 sinh viên/kỳ

## Các Yếu Tố Đầu Vào

Giải thuật nhận vào các dữ liệu sau:

1. Giảng viên (`teachers`): Một danh sách các giảng viên với các thông tin về khả năng giảng dạy (môn học có thể giảng dạy), thời gian giảng dạy tối đa (`time_gl`), và các thông tin khác như số giờ giảng dạy tối đa cho phép.
   
2. Môn học (`classes`): Một danh sách các lớp học (môn học), với thông tin về thời gian giảng dạy, ngày học, số tiết học, và số giờ quy đổi.

3. Nguyện vọng học (`aspiration`): Một danh sách các nguyện vọng, với thông tin về mã lớp, mã sinh viên, và số giờ quy đổi.

4. Giải thuật Harmony Search: Giải thuật này sử dụng phương pháp tìm kiếm hòa âm (Harmony Search) để tối ưu hóa quá trình phân công. Harmony Search là một thuật toán metaheuristic được sử dụng để giải quyết các bài toán tối ưu phức tạp.

## Giải Thuật

Giải thuật phân công giảng dạy và hướng dẫn đồ án sử dụng phương pháp Harmony Search với các bước cơ bản sau:

1. Khởi tạo bộ nhớ hòa âm: 
   - Bộ nhớ hòa âm (Harmony Memory - HM) chứa các giải pháp có thể chấp nhận được, trong đó mỗi giải pháp là một cách phân công giảng viên cho các lớp học.
   - Mỗi giảng viên sẽ được phân công cho các lớp học tương ứng với các điều kiện như môn học có thể giảng dạy và khối lượng công việc tối đa.

2. Tìm kiếm hòa âm (Harmony Search):
   - Mỗi lần lặp, một giải pháp mới sẽ được tạo ra từ bộ nhớ hòa âm hiện tại, theo các quy tắc:
     - Lựa chọn ngẫu nhiên giảng viên cho một lớp học.
     - Kiểm tra xem giảng viên có thể giảng dạy lớp học đó hay không (dựa trên các ràng buộc như môn học và số giờ dạy).
     - Cập nhật bộ nhớ hòa âm nếu giải pháp mới tốt hơn.

3. Đánh giá giải pháp:
   - Các giải pháp được đánh giá dựa trên các tiêu chí sau:
     - Khối lượng công việc của giảng viên: Phạt nếu giảng viên vượt quá số giờ giảng dạy tối đa.
     - Trùng lặp lịch: Phạt nếu các lớp học được phân công cho giảng viên có lịch trùng nhau.
     - Giảng viên chưa được phân công: Phạt nếu giảng viên không được phân công ít nhất một lớp học.
     - Tối ưu hóa phân công: Thưởng nếu các lớp học được phân công hợp lý, tránh việc giảng viên quá tải.

4. Cập nhật bộ nhớ hòa âm:
   - Các giải pháp tốt sẽ được lưu lại trong bộ nhớ hòa âm để tiếp tục sử dụng trong các lần lặp sau.

5. Tiêu chí dừng:
   - Quá trình tìm kiếm sẽ dừng lại sau một số lần lặp nhất định hoặc khi không có sự cải thiện nào trong bộ nhớ hòa âm.

## Hướng Dẫn Cài Đặt

### Yêu cầu

- Python 3.x
- Các thư viện cần thiết:
  - `random` (Python standard library)
  - `numpy` (Có thể dùng để tối ưu hóa và hỗ trợ các tính toán)

### Cài đặt và sử dụng

1. Clone repository:

```bash
git clone https://github.com/hoaivujr68/Demo_Giaithuat
```

2. Cài đặt các thư viện phụ thuộc (nếu cần thiết):

```bash
pip install -r requirements.txt
```

3. Chạy giải thuật:

```bash
Vào thư mục Harmony Search:
+ Phân công giảng dạy: cd GD -> python solve_gd.py
+ Phân công đồ án: cd DA -> python solve_da.py
```

### Tùy chỉnh tham số

- `MAX_ITER`: Số lần lặp tối đa cho giải thuật.
- `HMS`: Kích thước bộ nhớ hòa âm.
- `HMCR`: Tỷ lệ chọn giải pháp từ bộ nhớ hòa âm.
- `PAR`: Tỷ lệ xác suất thay đổi trong quá trình tìm kiếm.

## Kết Quả

Giải thuật phân công sẽ trả về các giải pháp tối ưu nhất dựa trên các tiêu chí đã đề ra, bao gồm phân công giảng viên hợp lý, không trùng lặp lịch và đảm bảo khối lượng công việc hợp lý cho các giảng viên.
