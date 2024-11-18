
import numpy as np
from math import gamma
import random
import data_kb1
from pprint import pprint
from timer import *
import json
import getdata

def objective_function(solution, classes):
    """
    Hàm tính toán số lớp không có giảng viên dạy.
    Mục tiêu là tối thiểu hóa số lớp không có giảng viên dạy.
    Trả về tổng số lớp không có giảng viên dạy.
    """
    no_teacher_classes = 0

    # Đếm số lớp không có giảng viên dạy
    for j in classes:
        if j not in solution.values():  # Nếu lớp j không có giảng viên dạy
            no_teacher_classes += 1

    return no_teacher_classes

def check_constraints(solution, teachers, classes):
    """
    Hàm kiểm tra các ràng buộc.
    Trả về True nếu giải pháp thỏa mãn tất cả ràng buộc, ngược lại trả về False.
    """
    # Tạo từ điển để lưu số giảng viên đã dạy mỗi lớp
    class_teacher_count = {}

    # Kiểm tra ràng buộc: Mỗi lớp chỉ có một giảng viên dạy
    for j, teacher in solution.items():
        if j not in class_teacher_count:
            class_teacher_count[j] = 1
        else:
            class_teacher_count[j] += 1

        # Nếu có hơn một giảng viên được phân công dạy lớp này, không hợp lệ
        if class_teacher_count[j] > 1:
            return False

    # Ràng buộc: Giảng viên chỉ dạy được các môn mà họ có thể dạy
    for j, teacher in solution.items():
        if classes[j]["subject"] not in teachers[teacher]["teachable_subjects"]:
            return False
    
    # Ràng buộc: Giảng viên không thể dạy quá số giờ tối đa
    current_hours = {i: 0 for i in teachers}
    for j, teacher in solution.items():
        current_hours[teacher] += classes[j]['quy_doi_gio']
        if current_hours[teacher] > teachers[teacher]['time_gl']:
            return False
    
    # Ràng buộc: Mỗi giảng viên phải dạy ít nhất một môn
    for teacher in teachers:
        if teacher not in solution.values():
            return False


    return True

def levy_flight(Lambda):
    """
    Tạo một bước di chuyển Levy Flight.
    """
    sigma = (gamma(1 + Lambda) * np.sin(np.pi * Lambda / 2) / 
            (gamma((1 + Lambda) / 2) * Lambda * 2 ** ((Lambda - 1) / 2))) ** (1 / Lambda)
    u = np.random.normal(0, sigma, 1)
    v = np.random.normal(0, 1, 1)
    step = u / abs(v) ** (1 / Lambda)
    return step

def choose_new_teacher(teachers, classes, j, solution, current_hours, subject_to_teachers):
    """
    Chọn một giảng viên mới cho lớp j dựa trên khả năng dạy lớp và số giờ còn lại của giảng viên.
    current_hours: từ điển lưu trữ tổng số giờ dạy hiện tại của từng giảng viên.
    subject_to_teachers: từ điển ánh xạ môn học với danh sách giảng viên có thể dạy môn đó.
    """
    # Lấy danh sách các giảng viên có thể dạy môn học của lớp j
    subject = classes[j]['subject']
    possible_teachers = subject_to_teachers.get(subject, [])

    if possible_teachers:
        # Ưu tiên giảng viên có số giờ dạy còn lại ít hơn
        possible_teachers.sort(key=lambda i: teachers[i]['time_gl'] - current_hours.get(i, 0))
        
        # Chọn ngẫu nhiên trong số 3 giảng viên có số giờ còn lại ít nhất
        return random.choice(possible_teachers[:3])
    
    return None  # Nếu không có giảng viên nào dạy được lớp này

def build_subject_to_teachers(teachers, classes):
    """
    Tạo từ điển ánh xạ môn học với danh sách các giảng viên có thể dạy môn đó.
    """
    subject_to_teachers = {}
    for i in teachers:
        for subject in teachers[i]['teachable_subjects']:
            if subject not in subject_to_teachers:
                subject_to_teachers[subject] = []
            subject_to_teachers[subject].append(i)
    return subject_to_teachers


import random

def random_solution(teachers, classes):
    """
    Khởi tạo giải pháp ngẫu nhiên, đảm bảo rằng mỗi giảng viên chỉ dạy các lớp mà họ có thể dạy.
    Phân ít nhất một lớp cho mỗi giảng viên nếu có thể.
    """
    solution = {}
    teachers_assigned = set()

    # Tạo danh sách các lớp còn trống
    remaining_classes = list(classes.keys())

    # Phân ít nhất một lớp cho mỗi giảng viên (nếu có thể dạy môn đó)
    for teacher in teachers:
        possible_classes = [j for j in remaining_classes if classes[j]['subject'] in teachers[teacher]['teachable_subjects']]
        if possible_classes:
            assigned_class = random.choice(possible_classes)
            solution[assigned_class] = teacher
            teachers_assigned.add(teacher)
            remaining_classes.remove(assigned_class)

    # Phân các lớp còn lại cho các giảng viên có thể dạy lớp đó
    for j in remaining_classes:
        possible_teachers = [i for i in teachers if classes[j]['subject'] in teachers[i]['teachable_subjects']]
        if possible_teachers:
            teacher_chosen = random.choice(possible_teachers)
            solution[j] = teacher_chosen
            teachers_assigned.add(teacher_chosen)  # Đánh dấu giảng viên đã được phân lớp
        else:
            solution[j] = None  # Lớp không có giảng viên

    # Kiểm tra và phân công lại cho giảng viên chưa được phân lớp
    unassigned_teachers = set(teachers.keys()) - teachers_assigned
    for teacher in unassigned_teachers:
        # Tìm lớp có thể phân công cho giảng viên này
        possible_classes = [j for j in classes if classes[j]['subject'] in teachers[teacher]['teachable_subjects'] and solution.get(j) is None]
        if possible_classes:
            assigned_class = random.choice(possible_classes)
            solution[assigned_class] = teacher
            teachers_assigned.add(teacher)

    # In thông báo nếu vẫn có giảng viên không được phân công
    unassigned_teachers = set(teachers.keys()) - teachers_assigned
    if len(unassigned_teachers) > 0:
        print(f"Warning: These teachers could not be assigned any class due to lack of suitable classes: {unassigned_teachers}")

    return solution


def print_summary(teachers, classes, solution):
    # Tính tổng thời gian thực tế và kiểm tra giảng viên bị quá GL
    list_over_gl = []
    teacher_tables = {}
    teacher_no_class = []
    classes_no_teacher = []
    
    # Ghi dữ liệu ra file JSON
    with open('solution.json', 'w', encoding='utf-8') as f:
        json.dump(solution, f, ensure_ascii=False, indent=4)
    
    for i in teachers:
        teacher_tables[i] = {'Thứ 2': [], 'Thứ 3': [], 'Thứ 4': [], 'Thứ 5': [], 'Thứ 6': [], 'Thứ 7': [], 'Tổng số tiết': 0}
        time_thuc_te = 0
        is_have_class = False

        # Kiểm tra thời gian thực tế cho mỗi giảng viên
        for j, teacher in solution.items():
            if teacher == i:
                is_have_class = True
                time_thuc_te += classes[j]['quy_doi_gio']
                teacher_tables[i]['Thứ ' + str(classes[j]['day'])].append(f"{classes[j]['period']}: {classes[j]['subject']} ({j})")
        
        # Nếu giảng viên có lớp, tính số tiết và kiểm tra quá tải GL
        if is_have_class:
            teacher_tables[i]['Tổng số tiết'] = time_thuc_te
            if time_thuc_te > teachers[i]['time_gl']:
                list_over_gl.append({
                    "giang_vien": i, 
                    "gio_thuc_te": round(time_thuc_te, 2), 
                    "gio_gioi_han": teachers[i]['time_gl'],
                    "phan_tram": round(time_thuc_te / teachers[i]['time_gl'] * 100, 2)
                })
        else:
            teacher_no_class.append(i)
    
    # Kiểm tra các lớp không có giảng viên
    for j in classes:
        if j not in solution:
            classes_no_teacher.append(j)

    # Tạo dictionary chứa toàn bộ thông tin
    summary_data = {
        'so_giang_vien_bi_qua_GL': len(list_over_gl),
        'list_over_gl': list_over_gl,
        'so_giang_vien_khong_co_lop': len(teacher_no_class),
        'teacher_no_class': teacher_no_class,
        'so_lop_khong_co_giang_vien': len(classes_no_teacher),
        'classes_no_teacher': classes_no_teacher,
        'teacher_tables': teacher_tables
    }

    # Ghi dữ liệu ra file JSON
    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=4)

    # In thông tin chi tiết ra màn hình (tùy chọn)
    print('Số giảng viên bị quá GL: ', len(list_over_gl))
    for i in list_over_gl:
        print(f"Giảng viên {i['giang_vien']}: {i['gio_thuc_te']}/{i['gio_gioi_han']} ({i['phan_tram']}%)")

    print('Số giảng viên không có lớp: ', len(teacher_no_class))
    if len(teacher_no_class) > 0:
        print('Danh sách giảng viên không có lớp: ', teacher_no_class)

    print('Số lớp không có giảng viên: ', len(classes_no_teacher))
    if len(classes_no_teacher) > 0:
        print('Danh sách lớp không có giảng viên: ', classes_no_teacher)

    # In bảng phân bổ giảng viên
    pprint(teacher_tables)
    
def cuckoo_search(teachers, classes, n_nests=70, max_iter=200, Lambda=1.5):
    start_timer()
    # Tạo từ điển ánh xạ môn học với danh sách giảng viên có thể dạy môn đó
    subject_to_teachers = build_subject_to_teachers(teachers, classes)

    # Khởi tạo tổ chim ban đầu (các giải pháp ngẫu nhiên)
    nests = [random_solution(teachers, classes) for _ in range(n_nests)]
    fitness = [objective_function(nest, classes) for nest in nests]

    # Tìm tổ chim tốt nhất
    best_solution = nests[np.argmin(fitness)]  # Tìm giải pháp có fitness thấp nhất (ít lớp không có giảng viên nhất)
    best_fitness = min(fitness)

    # Tính tổng số giờ dạy ban đầu cho mỗi giảng viên
    current_hours = {i: 0 for i in teachers}  # Đảm bảo khởi tạo tất cả giảng viên với giá trị 0
    for j, teacher in best_solution.items():
        current_hours[teacher] += classes[j]['quy_doi_gio']

    # Bắt đầu vòng lặp tối ưu
    for _ in range(max_iter):
        new_nests = []
        for nest in nests:
            # Sao chép tổ hiện tại
            new_solution = nest.copy()

            # Áp dụng Levy Flight để sinh tổ mới
            step_size = levy_flight(Lambda)
            for j in classes:
                # Thay đổi giảng viên dựa trên Levy Flight
                if random.random() < min(1, abs(step_size)):
                    new_teacher = choose_new_teacher(teachers, classes, j, new_solution, current_hours, subject_to_teachers)
                    if new_teacher:
                        # Cập nhật giảng viên mới cho lớp j
                        old_teacher = new_solution[j]
                        new_solution[j] = new_teacher

                        # Cập nhật lại tổng số giờ dạy cho giảng viên cũ và mới
                        if old_teacher:
                            current_hours[old_teacher] -= classes[j]['quy_doi_gio']
                        current_hours[new_teacher] += classes[j]['quy_doi_gio']

            # Kiểm tra ràng buộc và tính fitness cho tổ mới
            if check_constraints(new_solution, teachers, classes):
                new_fitness = objective_function(new_solution, classes)
                new_nests.append(new_solution)

                # Cập nhật tổ tốt nhất nếu tìm thấy tổ tốt hơn
                if new_fitness < best_fitness:  # Tìm giải pháp có ít lớp không có giảng viên nhất
                    best_solution = new_solution
                    best_fitness = new_fitness
            else:
                new_nests.append(nest)  # Giữ nguyên tổ nếu tổ mới không hợp lệ

        nests = new_nests
    print("OK. (" + get_timer().__str__() + "s)")
    # Sau khi tìm thấy giải pháp tốt nhất, in kết quả ra file JSON
    print_summary(teachers, classes, best_solution)

    return best_solution, best_fitness

if __name__ == '__main__':
    # Đọc dữ liệu từ file Excel
#     teachers = data_kb1.get_list_teacher('SV1.xlsx')
#     classes = data_kb1.get_time_table('TKB_600.xlsx')
    teachers = getdata.get_list_teacher('NCM.xlsx')
    classes = getdata.get_time_table('TKB.xlsx')
    with open('classes.json', 'w', encoding='utf-8') as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)
        
    with open('teachers.json', 'w', encoding='utf-8') as teachers_file:
        json.dump(teachers, teachers_file, ensure_ascii=False, indent=4)
    # Gọi hàm giải bài toán bằng Cuckoo Search
    best_solution, best_fitness = cuckoo_search(teachers, classes)

    # In tổng thời gian chạy
    print('Tổng thời gian chạy: ', get_total_time())
