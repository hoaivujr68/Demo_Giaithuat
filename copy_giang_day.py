
import numpy as np
from math import gamma
import random
import data_kb1
from pprint import pprint
from timer import *
import json
import getdata

def objective_function(solution, classes):
    no_teacher_classes = 0

    # Đếm số lớp không có giảng viên dạy
    for j in classes:
        if j not in solution.values():  # Nếu lớp j không có giảng viên dạy
            no_teacher_classes += 1

    return no_teacher_classes

def check_constraints(solution, teachers123, classes):
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
        if teacher is not None:
            if classes[j]["subject"] not in teachers123[teacher]["teachable_subjects"]:
                return False

    # Ràng buộc: Giảng viên không thể dạy quá số giờ tối đa và không vượt quá 200% thời gian tối đa
    current_hours = {i: 0 for i in teachers123}
    for j, teacher in solution.items():
        if teacher is not None:
            current_hours[teacher] += classes[j]['quy_doi_gio']
            # Kiểm tra nếu vượt quá số giờ tối đa
            if current_hours[teacher] > teachers123[teacher]['time_gl']:
                return False
            # Kiểm tra nếu tỷ lệ dạy quá giờ vượt quá 200%
            if current_hours[teacher] > 2 * teachers123[teacher]['time_gl']:
                return False

    # Ràng buộc: Mỗi giảng viên phải dạy ít nhất một môn
    for teacher in teachers123:
        if teacher not in solution.values():
            return False

    # Ràng buộc: Mỗi giảng viên chỉ dạy 1 lớp trong 1 thời điểm (tiết học, ngày học, tuần học)
    teacher_schedule = {i: set() for i in teachers123}  # Tạo một set để lưu lịch giảng dạy của mỗi giảng viên
    for j, teacher in solution.items():
        if teacher is not None:
            # Lấy thời gian dạy của lớp học, đảm bảo rằng period và week là tuple
            class_time = (tuple(classes[j]["period"]), classes[j]["day"], tuple(classes[j]["week"]))

            # Nếu thời gian này đã tồn tại trong lịch của giảng viên, trả về False
            if class_time in teacher_schedule[teacher]:
                return False
            
            # Thêm thời gian dạy vào lịch của giảng viên
            teacher_schedule[teacher].add(class_time)

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

def choose_new_teacher(teachers123, classes, j, solution, current_hours, subject_to_teachers123, teacher_schedule):

    subject = classes[j]['subject']
    possible_teachers123 = subject_to_teachers123.get(subject, [])
    class_time = (tuple(classes[j]["period"]), classes[j]["day"], tuple(classes[j]["week"]))

    if possible_teachers123:
        # Ưu tiên giảng viên có số giờ dạy còn lại ít hơn và không có trùng lịch
        possible_teachers123 = [i for i in possible_teachers123 if class_time not in teacher_schedule[i]]
        possible_teachers123.sort(key=lambda i: teachers123[i]['time_gl'] - current_hours.get(i, 0))

        # Chọn ngẫu nhiên trong số 3 giảng viên có số giờ còn lại ít nhất
        if possible_teachers123:
            chosen_teacher = random.choice(possible_teachers123[:3])
            teacher_schedule[chosen_teacher].add(class_time)  # Cập nhật lịch của giảng viên mới
            return chosen_teacher
    
    return None  # Nếu không có giảng viên nào dạy được lớp này


def build_subject_to_teachers123(teachers123, classes):
    """
    Tạo từ điển ánh xạ môn học với danh sách các giảng viên có thể dạy môn đó.
    """
    subject_to_teachers123 = {}
    for i in teachers123:
        for subject in teachers123[i]['teachable_subjects']:
            if subject not in subject_to_teachers123:
                subject_to_teachers123[subject] = []
            subject_to_teachers123[subject].append(i)
    return subject_to_teachers123

def random_solution(teachers123, classes, max_attempts=10):
    """
    Khởi tạo giải pháp ngẫu nhiên, đảm bảo rằng mỗi giảng viên chỉ dạy các lớp mà họ có thể dạy.
    Phân ít nhất một lớp cho mỗi giảng viên nếu có thể.
    """
    best_solution = None
    min_no_teacher_classes = float('inf')
    
    for attempt in range(max_attempts):
        solution = {}
        teachers123_assigned = set()
        teacher_schedule = {teacher: set() for teacher in teachers123}
        remaining_classes = list(classes.keys())
        
        # Phân ít nhất một lớp cho mỗi giảng viên (nếu có thể dạy môn đó)
        for teacher in teachers123:
            possible_classes = [j for j in remaining_classes if classes[j]['subject'] in teachers123[teacher]['teachable_subjects']]
            if possible_classes:
                assigned_class = None
                while possible_classes:
                    candidate_class = random.choice(possible_classes)
                    class_time = (classes[candidate_class]['day'], tuple(classes[candidate_class]['period']), tuple(classes[candidate_class]['week']))
                    
                    if class_time not in teacher_schedule[teacher]:
                        assigned_class = candidate_class
                        solution[assigned_class] = teacher
                        teachers123_assigned.add(teacher)
                        teacher_schedule[teacher].add(class_time)
                        remaining_classes.remove(assigned_class)
                        break
                    else:
                        possible_classes.remove(candidate_class)

        # Phân các lớp còn lại cho các giảng viên có thể dạy lớp đó
        for j in remaining_classes:
            possible_teachers123 = [i for i in teachers123 if classes[j]['subject'] in teachers123[i]['teachable_subjects']]
            teacher_chosen = None
            class_time = (classes[j]['day'], tuple(classes[j]['period']), tuple(classes[j]['week']))
            
            while possible_teachers123:
                candidate_teacher = random.choice(possible_teachers123)
                if class_time not in teacher_schedule[candidate_teacher]:
                    teacher_chosen = candidate_teacher
                    solution[j] = teacher_chosen
                    teachers123_assigned.add(teacher_chosen)
                    teacher_schedule[teacher_chosen].add(class_time)
                    break
                else:
                    possible_teachers123.remove(candidate_teacher)
            if teacher_chosen is None:
                solution[j] = None

        # Kiểm tra và cập nhật giải pháp tốt nhất
        no_teacher_classes = sum(1 for j in classes if solution.get(j) is None)
        if no_teacher_classes < min_no_teacher_classes:
            min_no_teacher_classes = no_teacher_classes
            best_solution = solution

        if min_no_teacher_classes == 0:  # Dừng sớm nếu không còn lớp nào thiếu giảng viên
            break

    return best_solution


def print_summary(teachers123, classes, solution):
    # Tính tổng thời gian thực tế và kiểm tra giảng viên bị quá GL
    list_over_gl = []
    teacher_tables = {}
    teacher_no_class = []
    classes_no_teacher = []
    
    # Ghi dữ liệu ra file JSON
    with open('solution.json', 'w', encoding='utf-8') as f:
        json.dump(solution, f, ensure_ascii=False, indent=4)
    
    for i in teachers123:
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
            if time_thuc_te > teachers123[i]['time_gl']:
                list_over_gl.append({
                    "giang_vien": i, 
                    "gio_thuc_te": round(time_thuc_te, 2), 
                    "gio_gioi_han": teachers123[i]['time_gl'],
                    "phan_tram": round(time_thuc_te / teachers123[i]['time_gl'] * 100, 2)
                })
        else:
            teacher_no_class.append(i)

    for j in classes:
            # Kiểm tra nếu j không có trong solution hoặc solution[j] là None
        if j not in solution or solution[j] is None:
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
    
def cuckoo_search(teachers123, classes, n_nests=25, max_iter=200, Lambda=1.5):
    start_timer()
    # Tạo từ điển ánh xạ môn học với danh sách giảng viên có thể dạy môn đó
    subject_to_teachers123 = build_subject_to_teachers123(teachers123, classes)

    # Khởi tạo tổ chim ban đầu (các giải pháp ngẫu nhiên)
    nests = [random_solution(teachers123, classes) for _ in range(n_nests)]
    fitness = [objective_function(nest, classes) for nest in nests]

    # Tìm tổ chim tốt nhất
    best_solution = nests[np.argmin(fitness)]  # Tìm giải pháp có fitness thấp nhất (ít lớp không có giảng viên nhất)
    best_fitness = min(fitness)

    # Tính tổng số giờ dạy ban đầu cho mỗi giảng viên
    current_hours = {i: 0 for i in teachers123}  # Đảm bảo khởi tạo tất cả giảng viên với giá trị 0
    for j, teacher in best_solution.items():
        if teacher is not None:  # Bỏ qua nếu lớp không có giảng viên
            current_hours[teacher] += classes[j]['quy_doi_gio']

    # Khởi tạo `teacher_schedule` để lưu lịch dạy của mỗi giảng viên
    teacher_schedule = {i: set() for i in teachers123}
    for j, teacher in best_solution.items():
        class_time = (tuple(classes[j]["period"]), classes[j]["day"], tuple(classes[j]["week"]))
        if teacher is not None:
            teacher_schedule[teacher].add(class_time)

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
                    new_teacher = choose_new_teacher(teachers123, classes, j, new_solution, current_hours, subject_to_teachers123, teacher_schedule)
                    if new_teacher:
                        # Cập nhật `new_solution` và `teacher_schedule` cho `new_teacher`
                        old_teacher = new_solution[j]
                        new_solution[j] = new_teacher
                        class_time = (tuple(classes[j]["period"]), classes[j]["day"], tuple(classes[j]["week"]))

                        # Cập nhật `teacher_schedule` cho cả giảng viên cũ và giảng viên mới
                        if old_teacher in teacher_schedule:
                            teacher_schedule[old_teacher].discard(class_time)
                        teacher_schedule[new_teacher].add(class_time)
                        current_hours[new_teacher] += classes[j]['quy_doi_gio']

            # Kiểm tra ràng buộc và tính fitness cho tổ mới
            if check_constraints(new_solution, teachers123, classes):
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
    print_summary(teachers123, classes, best_solution)

    return best_solution, best_fitness


if __name__ == '__main__':
    # Đọc dữ liệu từ file Excel
    # teachers123 = data_kb1.get_list_teacher('SV1.xlsx')
    # classes = data_kb1.get_time_table('TKB_600.xlsx')
    teachers123 = getdata.get_list_teacher('NCM.xlsx')
    classes = getdata.get_time_table('TKB.xlsx')
    with open('classes.json', 'w', encoding='utf-8') as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)
        
    with open('teachers123.json', 'w', encoding='utf-8') as teachers123_file:
        json.dump(teachers123, teachers123_file, ensure_ascii=False, indent=4)

    # Gọi hàm giải bài toán bằng Cuckoo Search
    best_solution, best_fitness = cuckoo_search(teachers123, classes)

    # In tổng thời gian chạy
    print('Tổng thời gian chạy: ', get_total_time())
