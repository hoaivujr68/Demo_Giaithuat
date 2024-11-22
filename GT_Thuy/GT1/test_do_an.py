from mip import Model, xsum, BINARY, minimize, maximize, CONTINUOUS, LinExpr
import mip
import sys
import pandas as pd
from pprint import pprint
import json 
import sys
sys.path.append(r"D:\Demo_Giaithuat")
from timer import *
import data_kb1

def create_model_nguyen_vong(sv_sheet, tkb_sheet):
    # da_xep_truoc: dict, key: teacher_id, value: list of class_id
    print("Đang đọc dữ liệu...", end="")
    start_timer()
    aspirations = data_kb1.get_list_nguyen_vong(sv_sheet)
    classes = data_kb1.get_time_table(tkb_sheet)
    teachers = data_kb1.get_list_teacher(sv_sheet)
    # giảm teacher còn 20
    # teachers = dict(list(teachers.items())[:90])
    # giảm aspirations còn 20
    # aspirations = dict(list(aspirations.items())[:100])
    print("OK. " + len(teachers).__str__() + " giảng viên, " + len(
        aspirations).__str__() + " nguyện vọng. (" + get_timer().__str__() + "s)")

    # Khởi tạo mô hình tối ưu xếp nguyện vọng
    print("Khởi tạo mô hình tối ưu xếp nguyện vọng...", end="")
    start_timer()
    model_nguyen_vong = Model()

    # Biến quyết định: a[i, j] = 1 nếu giảng viên i hướng dẫn nguyện vọng j
    a = {(i, j): model_nguyen_vong.add_var(var_type=BINARY, lb=0, ub=1)
         for i in teachers for j in aspirations}

    # Biến liên tục là thời gian hướng dẫn tất cả nguyện vọng của giảng viên i
    cur_time = {i: model_nguyen_vong.add_var(var_type=CONTINUOUS, lb=0, ub=40) for i in teachers}
    # cur_time_datn = {i: model_nguyen_vong.add_var(var_type=CONTINUOUS, lb=0, ub=40) for i in teachers}
    # cur_time_damh = {i: model_nguyen_vong.add_var(var_type=CONTINUOUS, lb=0, ub=40) for i in teachers}

    for i in teachers:
        model_nguyen_vong += cur_time[i] == xsum(a[i, j] * aspirations[j]['gio'] for j in aspirations) / teachers[i][
            'time_gh']
        # model_nguyen_vong += cur_time_datn[i] == xsum(a[i, j] * aspirations[j]['gio']
        # if aspirations[j]['section_type'] == 'ĐATN' else 0 for j in aspirations)/teachers[i]['time_gh']
        # model_nguyen_vong += cur_time_damh[i] == xsum(a[i, j] * aspirations[j]['gio']
        # if aspirations[j]['section_type'] == 'ĐAMH' else 0 for j in aspirations)/teachers[i]['time_gh']

    # Xếp hướng dẫn nguyện vọng theo thứ tự ưu tiên 1, 2, 3
    # Nếu 3 thứ tự ưu tiên không có giảng viên nào hướng dẫn, chọn random giảng viên có hệ số thấp nhất
    # Hàm mục tiêu: Tối đa hóa số điểm của tất cả nguyện vọng
    model_nguyen_vong.objective = maximize(
        xsum(4 * a[aspirations[j]['nguyen_vong']['1'], j] + \
             3 * a[aspirations[j]['nguyen_vong']['2'], j] + \
             2 * a[aspirations[j]['nguyen_vong']['3'], j] for j in aspirations)
    )
    # Ràng buộc: GHt (giờ hướng dẫn nguyện vọng thực tế)/GH (giờ hướng dẫn nguyện vọng lý tưởng = 46% GD)
    # của các giảng viên chênh lệch nhau không quá 10%
    for i1 in teachers:
        for i2 in teachers:
            if i1 != i2:
                model_nguyen_vong += cur_time[i1] - cur_time[i2] <= 0.2 or cur_time[i2] - cur_time[i1] <= 0.2
                # model_nguyen_vong += cur_time_datn[i1] - cur_time_datn[i2] <=
                # 0.1 or cur_time_datn[i2] - cur_time_datn[i1] <= 0.1
                # model_nguyen_vong += cur_time_damh[i1] - cur_time_damh[i2] <=
                # 0.1 or cur_time_damh[i2] - cur_time_damh[i1] <= 0.1
    # Ràng buộc: Tất cả nguyện vọng phải được hướng dẫn
    for j in aspirations:
        model_nguyen_vong += xsum(a[i, j] for i in teachers) == 1

    # Ràng buộc: Mỗi giảng viên không thể hướng dẫn quá 5 nguyện vọng với mỗi mã học phần
    for i in teachers:
        for j in aspirations:
            model_nguyen_vong += xsum(
                a[i, k] for k in aspirations if aspirations[k]['course_id'] == aspirations[j]['course_id']) <= 5

    # for i in teachers_assigned:
    #     model_nguyen_vong += a[i["giang_vien"], i["mssv"]] == 1
    # Ràng buộc: Mỗi giảng viên không thể hướng dẫn quá 30 nguyện vọng
    # for i in teachers:
    #     model_nguyen_vong += xsum(a[i, j] for j in aspirations) <= 30
    print("OK. (" + get_timer().__str__() + "s)")
    return teachers, aspirations, model_nguyen_vong, a


def solve(teachers, aspirations, model_nguyen_vong, a):
    # Giải bài toán tối ưu xếp nguyện vọng
    print("Đang giải bài toán tối ưu xếp nguyện vọng...", end="")
    start_timer()
    model_nguyen_vong.verbose = False
    model_nguyen_vong.optimize(max_seconds=180)
    print("OK. (" + get_timer().__str__() + "s)")
    print("Gia tri ham muc tieu: ", model_nguyen_vong.objective_value)
    # print("So solution: ", model_nguyen_vong.num_solutions)
    # In kết quả
    teachers_aspirations = {}
    for i in teachers:
        for j in aspirations:
            if a[i, j].x == 1:
                if i not in teachers_aspirations:
                    teachers_aspirations[i] = {}
                teachers_aspirations[i][j] = aspirations[j]['course_id']

    aspirations_no_teacher = [(j, aspirations[j]['course_id']) for j in aspirations if
                              all(a[i, j].x == 0 for i in teachers)]
    teachers_no_aspiration = [i for i in teachers if all(a[i, j].x == 0 for j in aspirations)]
    return teachers_aspirations, aspirations_no_teacher, teachers_no_aspiration


if __name__ == '__main__':
    teachers, aspirations, model_nguyen_vong, a = create_model_nguyen_vong('SV1.xlsx', 'TKB_600.xlsx')
    teachers_aspirations, aspirations_no_teacher, teachers_no_aspiration = solve(teachers, aspirations,
                                                                                 model_nguyen_vong, a)
    pprint(teachers_aspirations)
    print("Tổng thời gian chạy: " + get_total_time().__str__() + "s")
    # Số giảng viên bị quá GH: + Danh sách
    overtime_gh_teacher = []
    for i in teachers:
        time_gh = sum(a[i, j].x * aspirations[j]['gio'] for j in aspirations)
        time_gh_datn = sum(
            a[i, j].x * aspirations[j]['gio'] if aspirations[j]['section_type'] == 'ĐATN' else 0 for j in aspirations)
        time_gh_damh = sum(
            a[i, j].x * aspirations[j]['gio'] if aspirations[j]['section_type'] == 'ĐAMH' else 0 for j in aspirations)

        time_gh_max = round(teachers[i]['time_gh'], 2)
        time_gh = round(time_gh, 2)
        time_gh_datn = round(time_gh_datn, 2)
        time_gh_damh = round(time_gh_damh, 2)

        pt_time_gh = round((time_gh / time_gh_max) * 100, 2)
        pt_time_gh_datn = round((time_gh_datn / time_gh_max) * 100, 2)
        pt_time_gh_damh = round((time_gh_damh / time_gh_max) * 100, 2)

        print("%s: GHt(DATN): %4s/%4s (%4s%%) || GHt(DAMH): %4s/%4s (%4s%%) || GHt: %4s/%4s (%4s%%)" % (
            i, time_gh_datn, time_gh_max, pt_time_gh_datn, time_gh_damh, time_gh_max, pt_time_gh_damh, time_gh,
            time_gh_max, pt_time_gh))
        if teachers[i]['time_gh'] < time_gh:
            overtime_gh_teacher.append(i)
    print("Số giảng viên bị quá GH: ", len(overtime_gh_teacher))
    if len(overtime_gh_teacher) > 0:
        print("Danh sách giảng viên bị quá GH: ")
        pprint(overtime_gh_teacher)
    # Số giảng viên không bị quá GH: + Danh sách

    # Số giảng viên có <= 30 NV: + Danh sách

    # Số giảng viên có trên 30 NV: + Danh sách

    print("Số nguyện vọng không được hướng dẫn: ", len(aspirations_no_teacher))
    if len(aspirations_no_teacher) > 0:
        print("Danh sách nguyện vọng không được hướng dẫn: ")
        pprint(aspirations_no_teacher)

    print("Số giảng viên không hướng dẫn nguyện vọng: ", len(teachers_no_aspiration))
    if len(teachers_no_aspiration) > 0:
        print("Danh sách giảng viên không hướng dẫn nguyện vọng: ")
        pprint(teachers_no_aspiration)