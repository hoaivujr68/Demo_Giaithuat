from mip import Model, xsum, BINARY, minimize, maximize, CONTINUOUS, LinExpr
import mip
import pandas as pd
from pprint import pprint
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import getdata
from timer import *
import data_kb1
def create_model_giang_day(sv_sheet, tkb_sheet):
    print("Đang đọc dữ liệu...", end="")
    start_timer()
    # aspirations = getdata.get_list_nguyen_vong(sv_sheet)
    classes = data_kb1.get_time_table(tkb_sheet)
    teachers = data_kb1.get_list_teacher(sv_sheet)
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
    for i in teachers:
        for k in classes:
            model_giang_day += xsum(x[i, j] for j in classes if classes[j]["day"] == classes[k]["day"] and
                              set(classes[j]["period"]).intersection(set(classes[k]["period"])) and
                              set(classes[j]["week"]).intersection(set(classes[k]["week"]))) <= 1
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
    teacher_tables = {}
    classes_no_teacher = [j for j in classes if xsum(x[i, j] for i in teachers).x == 0]
    # hiển thị theo day và period tăng dần
    classes = dict(sorted(classes.items(), key=lambda item: (item[1]["day"], item[1]["period"])))
    for i in teachers:
        is_have_class = False
        teacher_tables[i] = {'Thứ 2': [], 'Thứ 3': [], 'Thứ 4': [], 'Thứ 5': [], 'Thứ 6': [], 'Thứ 7': [],
                             'Tổng số tiết': None}
        for j in classes:
            if type(x[i, j].x) == float and x[i, j].x == 1:
                is_have_class = True
                teacher_tables[i]['Thứ ' + str(classes[j]['day'])].append(
                    f"{classes[j]['period']}: {classes[j]['subject']} ({j})")
        if is_have_class:
            teacher_tables[i]['Tổng số tiết'] = xsum(x[i, j] * len(classes[j]['period']) for j in classes).x
    teacher_no_class = [i for i in teachers if i not in teacher_tables]
    return teacher_tables, classes_no_teacher, teacher_no_class


if __name__ == '__main__':
    teachers, classes, model_giang_day, x = create_model_giang_day('SV1.xlsx', 'TKB_600.xlsx')
    teacher_tables, classes_no_teacher, teacher_no_class = solve(teachers, classes, model_giang_day, x)
    pprint(teacher_tables)
    print('Tổng thời gian chạy: ', get_total_time())
    list_over_gl = []
    for i in teachers:
        time_thuc_te = sum([classes[j]['quy_doi_gio'] for j in classes if x[i, j].x == 1])
        time_max = teachers[i]['time_gl']
        if time_thuc_te > time_max:
            list_over_gl.append((i, round(time_thuc_te, 2), time_max))
    # Số giảng viên bị quá GL: + Danh sách
    print('Số giảng viên bị quá GL: ', len(list_over_gl))
    for i in list_over_gl:
        print("Giảng viên %s: %s/%s(%s%%)" % (i[0], i[1], i[2], round(i[1] / i[2] * 100, 2)))
    # Số giảng viên không bị quá GL: + Danh sách
    print('Số giảng viên không bị quá GL: ', len(teachers) - len(list_over_gl))
    print('Số giảng viên không có lớp: ', len(teacher_no_class))
    if len(teacher_no_class) > 0:
        print('Danh sách giảng viên không có lớp: ', teacher_no_class)
    print('Số lớp không có giảng viên: ', len(classes_no_teacher))
    if len(classes_no_teacher) > 0:
        print('Danh sách lớp không có giảng viên: ', classes_no_teacher)
