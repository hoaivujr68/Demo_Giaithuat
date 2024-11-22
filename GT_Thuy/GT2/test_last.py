from mip import Model, xsum, BINARY, minimize, maximize, CONTINUOUS, LinExpr
import mip
import pandas as pd
from pprint import pprint
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import getdata
import data_kb1
from timer import *
import getdata1

def create_model_giang_day(sv_sheet, tkb_sheet):
    print("Đang đọc dữ liệu...", end="")
    start_timer()
    # aspirations = getdata.get_list_nguyen_vong(sv_sheet)
    classes = getdata1.get_time_table(tkb_sheet)
    teachers = getdata1.get_list_teacher(sv_sheet)
    # giảm class còn 20
    # classes = dict(list(classes.items())[:20])
    print("OK. " + len(teachers).__str__() + " giảng viên, " + len(classes).__str__() + " lớp. (" + get_timer().__str__() + "s)")
    print("Bắt đầu khởi tạo mô hình...")
    model_giang_day = Model()
    print("Mô hình đã được khởi tạo thành công.")

    # Biến quyết định: x[i, j] = 1 nếu giảng viên i dạy lớp j
    x = {(i, j): model_giang_day.add_var(var_type=BINARY, lb=0, ub=1)
         for i in teachers for j in classes}

    # Biến liên tục là thời gian giảng dạy thực tế của giảng viên i
    cur_time = {i: model_giang_day.add_var(var_type=CONTINUOUS, lb=0, ub=80) for i in teachers}
    for i in teachers:
        model_giang_day += cur_time[i] == xsum(x[i, j] * classes[j]["quy_doi_gio"] for j in classes) / teachers[i]["time_gl"]

    # Hàm mục tiêu: Tối đa hóa số giảng viên mà có GL (giờ giảng dạy trên lớp = 54% GD) - GHt (giờ giảng dạy trên lớp thực tế) < 2
    # Ràng buộc mềm: Ưu tiên giảng viên dạy các môn có thời gian học trong cùng 1 ngày
    SAMEDAY_VALUE = 100
    # # Ràng buộc mềm: Giảng viên muốn được xếp vào một số thứ (2,3,4,5,6) trong tuần theo nguyện vọng
    # want_day = {
    #     'GV011': [2, 3, 4],
    #     'GV012': [3, 4, 5],
    #     'GV013': [4, 5],
    # }
    # WANTDAY_VALUE = 100
    model_giang_day.objective = maximize(
        xsum(100 * x[i, j] for i in teachers for j in classes)
        # xsum(SAMEDAY_VALUE * len(set(classes[j]["day"] * x[i, j] for j in classes)) for i in teachers)
        # xsum(WANTDAY_VALUE * x[i, j] for i in want_day for j in classes if classes[j]["day"] not in want_day[i])
    )

    # Ràng buộc: Tỷ lệ overtime của mỗi giảng viên ko quá 200%
    for i in teachers:
        model_giang_day += cur_time[i] <= 2.0

    # Ràng buộc: Mỗi lớp chỉ có một giảng viên dạy
    for j in classes:
        model_giang_day += xsum(
            x[i, j] for i in teachers) <= 1
    # Ràng buộc: Mỗi giảng viên chỉ dạy được những môn mà giảng viên đó có thể dạy
    for i in teachers:
        for j in classes:
            if classes[j]["subject"] not in teachers[i]["teachable_subjects"]:
                model_giang_day += x[i, j] == 0
    # # Ràng buộc: Mỗi giảng viên không thể dạy quá số giờ tối đa
    # for i in teachers:
    #     model_giang_day += xsum(x[i, j] * classes[j]["quy_doi_gio"] for j in classes) <= teachers[i]["time_gl"]

    # Ràng buộc: Mỗi giảng viên chỉ dạy được 1 lớp trong 1 thời điểm (tiết học, ngày học, tuần học)
    for i in teachers:  # Với từng giảng viên
      for k in classes:  # Với từng lớp k
            for j in classes:  # Với từng lớp j
                  if j != k:  # Chỉ kiểm tra xung đột giữa hai lớp khác nhau
                  # Điều kiện trùng thời gian (ngày, tiết, tuần)
                        same_day = classes[j]["day"] == classes[k]["day"]

                        # Làm phẳng danh sách period
                        period_j = set(item for sublist in classes[j]["period"] for item in sublist)
                        period_k = set(item for sublist in classes[k]["period"] for item in sublist)
                        overlapping_period = period_j.intersection(period_k)

                        overlapping_week = set(classes[j]["week"]).intersection(set(classes[k]["week"]))

                        if same_day and overlapping_period and overlapping_week:
                              # Ràng buộc: Nếu giảng viên i dạy lớp j, không được dạy lớp k cùng thời điểm
                              model_giang_day += x[i, j] + x[i, k] <= 1


    # # # Ràng buộc mềm: Ưu tiên giảng viên dạy các môn có thời gian học gần nhau
    # # for i in teachers:
    # #     for j in classes:
    # #         for k in classes:
    # #             if classes[j]["day"] == classes[k]["day"] and \
    # #                     set(classes[j]["period"]).intersection(set(classes[k]["period"])):
    # #                 model += x[i, j] + x[i, k] <= 1
    print("OK. (" + get_timer().__str__() + "s)")
    return teachers, classes, model_giang_day, x


def solve(teachers, classes, model_giang_day, x):
    # Giải bài toán tối ưu xếp thời khóa biểu
    print("Đang giải bài toán tối ưu xếp thời khóa biểu...", end="")
    start_timer()
    model_giang_day.verbose = False
    model_giang_day.optimize(max_seconds=180)
    print("OK. (" + get_timer().__str__() + "s)")

    # Khởi tạo kết quả
    teacher_tables = {}
    classes_no_teacher = []
    teacher_no_class = []

    # Lọc các lớp không có giảng viên
    for j in classes:
        if sum(x[i, j].x for i in teachers) == 0:
            classes_no_teacher.append(j)

    # Sắp xếp các lớp theo day và period tăng dần
# Sắp xếp các lớp theo day và period tăng dần, xử lý trường hợp period rỗng
    classes = dict(sorted(classes.items(), key=lambda item: (
      item[1]["day"],
      min(item[1]["period"]) if item[1]["period"] else float('inf')  # Giá trị mặc định nếu period rỗng
      )))


    for i in teachers:
      is_have_class = False
      teacher_tables[i] = {
            'Thứ 2': [], 'Thứ 3': [], 'Thứ 4': [], 'Thứ 5': [], 'Thứ 6': [], 'Thứ 7': [], 'Tổng số tiết': 0
      }

      for j in classes:
            # Kiểm tra và chuẩn hóa giá trị 'day'
            if isinstance(classes[j]['day'], list):
                  if len(classes[j]['day']) > 0:  # Nếu không rỗng, lấy giá trị đầu tiên
                        class_day = classes[j]['day'][0]
                  else:  # Nếu rỗng, bỏ qua hoặc gán giá trị mặc định
                        print(f"Lớp {j} có 'day' rỗng. Bỏ qua.")
                        continue
            else:
                  class_day = classes[j]['day']

            if isinstance(x[i, j].x, (int, float)) and x[i, j].x == 1:
                  is_have_class = True
                  teacher_tables[i]['Thứ ' + str(class_day)].append(
                  f"Tiết {','.join(map(str, classes[j]['period']))}: {classes[j]['subject']} ({j})"
                  )
                  teacher_tables[i]['Tổng số tiết'] += len(classes[j]['period'])

      if not is_have_class:
            teacher_no_class.append(i)


    return teacher_tables, classes_no_teacher, teacher_no_class



if __name__ == '__main__':
    # Khởi tạo mô hình
    teachers, classes, model_giang_day, x = create_model_giang_day('NCM1.xlsx', 'TKB1.xlsx')

    # Giải quyết bài toán
    teacher_tables, classes_no_teacher, teacher_no_class = solve(teachers, classes, model_giang_day, x)
    
    # Hiển thị kết quả
    print("\n==== KẾT QUẢ PHÂN CÔNG ====\n")
    from pprint import pprint
    pprint(teacher_tables)

    print("\nTổng thời gian chạy: ", get_total_time())

    # Kiểm tra giảng viên bị quá giới hạn thời gian giảng dạy
    list_over_gl = []
    for i in teachers:
        # Tổng thời gian thực tế giảng dạy
        time_thuc_te = sum(classes[j]['quy_doi_gio'] for j in classes if x[i, j].x == 1)
        # Giới hạn thời gian của giảng viên
        time_max = teachers[i]['time_gl']
        
        # Kiểm tra nếu vượt quá giới hạn
        if time_thuc_te > time_max:
            list_over_gl.append((i, round(time_thuc_te, 2), time_max))

    # In kết quả
    print("\n==== BÁO CÁO GIẢNG VIÊN ====\n")
    print(f"Số giảng viên bị quá GL: {len(list_over_gl)}")
    if list_over_gl:
        print("Danh sách giảng viên bị quá GL:")
        for i in list_over_gl:
            print(f"  Giảng viên {i[0]}: {i[1]} / {i[2]} ({round(i[1] / i[2] * 100, 2)}%)")

    print(f"\nSố giảng viên không bị quá GL: {len(teachers) - len(list_over_gl)}")
    print(f"Số giảng viên không có lớp: {len(teacher_no_class)}")
    if teacher_no_class:
        print("Danh sách giảng viên không có lớp:")
        print("  ", teacher_no_class)

    # Báo cáo lớp học
    print("\n==== BÁO CÁO LỚP HỌC ====\n")
    print(f"Số lớp không có giảng viên: {len(classes_no_teacher)}")
    if classes_no_teacher:
        print("Danh sách lớp không có giảng viên:")
        print("  ", classes_no_teacher)

