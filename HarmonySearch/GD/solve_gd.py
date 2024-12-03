import json
import random
import numpy as np
from pprint import pprint
import sys

sys.path.append(r"D:\Demo_Giaithuat")
import getdata1
from timer import *

HMS = 100  # Harmony memory size
HMCR = 0.9  # Harmony memory consideration rate
PAR = 0.3  # Pitch adjustment rate
MAX_ITER = 1000  # Số lần lặp tối đa

# Hàm khởi tạo bộ nhớ hòa âm
def initialize_harmony_memory(teachers, classes, memory_size):
    harmony_memory = []

    for _ in range(memory_size):
        solution = {}
        teacher_workload = {teacher: 0 for teacher in teachers.keys()}

        for class_key, class_info in classes.items():
            valid_teachers = [
                teacher_key
                for teacher_key, teacher_data in teachers.items()
                if class_info["subject"] in teacher_data["teachable_subjects"]
                and teacher_workload[teacher_key] + class_info["quy_doi_gio"]
                <= 2 * teacher_data["time_gl"]
            ]

            if valid_teachers:
                assigned_teacher = random.choice(valid_teachers)
                solution[class_key] = assigned_teacher
                teacher_workload[assigned_teacher] += class_info["quy_doi_gio"]
            else:
                solution[class_key] = None  # Không thể gán nếu không hợp lệ

        harmony_memory.append(solution)
    return harmony_memory

def schedules_overlap(period1, period2):
    """
    Kiểm tra xem hai khoảng thời gian (period) có trùng nhau không.
    Mỗi period có thể là một dãy các tiết học liên tiếp (ví dụ: [1, 2, 3]).
    """
    # Đảm bảo rằng mỗi period là một danh sách các tiết học
    if not (isinstance(period1, list) and isinstance(period2, list)):
        raise ValueError("Each period should be a list of times (e.g., [1, 2, 3])")

    # Lấy min và max của period1 và period2 để tạo ra khoảng thời gian
    start1, end1 = min(period1), max(period1)
    start2, end2 = min(period2), max(period2)

    # Kiểm tra xem các khoảng thời gian có giao nhau không
    return max(start1, start2) < min(end1, end2)
def evaluate_solution(solution, teachers, classes):
    total_score = 0
    teacher_workload = {teacher: 0 for teacher in teachers.keys()}
    assigned_teachers = set()  # Giữ danh sách các giảng viên đã được phân công

    # Lưu lịch dạy của mỗi giảng viên để kiểm tra trùng lặp
    teacher_schedules = {teacher: [] for teacher in teachers.keys()}

    for class_key, teacher_key in solution.items():
        if teacher_key:
            class_info = classes[class_key]
            teacher_data = teachers[teacher_key]

            # Tăng giờ giảng của giảng viên
            teacher_workload[teacher_key] += class_info["quy_doi_gio"]
            assigned_teachers.add(teacher_key)  # Đánh dấu giảng viên đã được phân công

            # Kiểm tra trùng lặp thời gian
            for idx, day in enumerate(class_info["day"]):
                period = class_info["period"][idx]  # Mảng tiết học tương ứng với ngày

                # Kiểm tra nếu lớp này có tiết học trùng với các lớp khác của giảng viên
                for scheduled_day, scheduled_period in teacher_schedules[teacher_key]:
                    if day == scheduled_day and schedules_overlap(scheduled_period, period):
                        total_score -= 20  # Phạt nếu lịch trùng
                        break

                teacher_schedules[teacher_key].append((day, period))  # Thêm lịch dạy mới

            # Phạt nếu vượt giờ
            if teacher_workload[teacher_key] > 2 * teacher_data["time_gl"]:
                total_score -= 10  # Phạt
            else:
                total_score += 1  # Thưởng nếu phân công hợp lệ

    # Kiểm tra nếu tất cả giảng viên đều được phân công ít nhất một lớp
    unassigned_teachers = set(teachers.keys()) - assigned_teachers
    if unassigned_teachers:
        total_score -= (
            len(unassigned_teachers) * 5
        )  # Phạt mỗi giảng viên không được phân công

    return total_score


# Hàm cập nhật bộ nhớ hòa âm
def update_harmony(harmony_memory, teachers, classes, new_solution):
    worst_solution = min(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, classes)
    )
    worst_score = evaluate_solution(worst_solution, teachers, classes)
    new_score = evaluate_solution(new_solution, teachers, classes)

    if new_score > worst_score:
        harmony_memory.remove(worst_solution)
        harmony_memory.append(new_solution)
    return harmony_memory


def harmony_search(
    teachers, classes, memory_size=HMS, max_iterations=MAX_ITER, hmcr=HMCR, par=PAR
):
    # Sắp xếp giáo viên theo `time_gl` tăng dần
    sorted_teachers = sorted(teachers.items(), key=lambda x: x[1]["time_gl"])

    harmony_memory = initialize_harmony_memory(teachers, classes, memory_size)

    for _ in range(max_iterations):
        new_solution = {}
        teacher_workload = {teacher: 0 for teacher in teachers.keys()}

        for class_key, class_info in classes.items():
            # Chọn ngẫu nhiên một giải pháp từ bộ nhớ hòa âm
            random_solution = random.choice(harmony_memory)
            selected_teacher = random_solution[class_key]

            # Kiểm tra xem giáo viên đã chọn có hợp lệ không
            if (
                selected_teacher
                and class_info["subject"]
                in teachers[selected_teacher]["teachable_subjects"]
                and teacher_workload[selected_teacher] + class_info["quy_doi_gio"]
                <= 2 * teachers[selected_teacher]["time_gl"]
            ):
                new_solution[class_key] = selected_teacher
                teacher_workload[selected_teacher] += class_info["quy_doi_gio"]
            else:
                # Ưu tiên phân công giáo viên có `time_gl` thấp trong danh sách hợp lệ
                valid_teachers = [
                    teacher_key
                    for teacher_key, teacher_data in sorted_teachers
                    if class_info["subject"] in teacher_data["teachable_subjects"]
                    and teacher_workload[teacher_key] + class_info["quy_doi_gio"]
                    <= 2 * teacher_data["time_gl"]
                ]
                if valid_teachers:
                    assigned_teacher = valid_teachers[0]
                    new_solution[class_key] = assigned_teacher
                    teacher_workload[assigned_teacher] += class_info["quy_doi_gio"]
                else:
                    new_solution[class_key] = None  # Không thể gán nếu không hợp lệ

        # Cập nhật bộ nhớ hòa âm với giải pháp mới
        harmony_memory = update_harmony(harmony_memory, teachers, classes, new_solution)

    # Tìm giải pháp tốt nhất
    best_solution = max(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, classes)
    )
    best_score = evaluate_solution(best_solution, teachers, classes)

    return best_solution, best_score



if __name__ == "__main__":
    start_timer()
    teachers = getdata1.get_list_teacher("NCM2.xlsx")
    classes = getdata1.get_time_table("TKB1.xlsx")
    total_time_gh = sum(teacher["time_gl"] for teacher in teachers.values())
    total_time_gio = sum(classes["quy_doi_gio"] for classes in classes.values())
    # In ra tổng thời gian và thông tin tổng quát
    print("Tổng time_gh của giáo viên:", total_time_gh)
    print("Tổng total_time_gio của class:", total_time_gio)
    print("Tổng số giáo viên:", len(teachers))
    print("Tổng số lớp:", len(classes))
        # Ghi dữ liệu vào file JSON
    with open("teachers_data.json", "w", encoding="utf-8") as teachers_file:
        json.dump(teachers, teachers_file, ensure_ascii=False, indent=4)

    with open("classes_data.json", "w", encoding="utf-8") as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)

    best_solution, best_score = harmony_search(teachers, classes)
    print("OK. (" + get_timer().__str__() + "s)")
    # Kiểm tra nếu lời giải trả về hợp lệ
    if not best_solution:
        print("Không tìm thấy lời giải hợp lệ!")
        exit()

    # Tính toán thời gian thực tế của giảng viên
    list_over_gl = []
    for teacher_id, teacher_info in teachers.items():
        time_thuc_te = sum(
            classes[class_id]["quy_doi_gio"]
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        )
        time_max = teacher_info["time_gl"]
        if time_thuc_te > 2 * time_max:
            list_over_gl.append((teacher_id, round(time_thuc_te, 2), time_max))

    print("Số giảng viên bị quá GL:", len(list_over_gl))
    for teacher in list_over_gl:
        print(
            f"Giảng viên {teacher[0]}: {teacher[1]}/{teacher[2]} ({round(teacher[1] / teacher[2] * 100, 2)}%)"
        )

    print("Số giảng viên không bị quá GL:", len(teachers) - len(list_over_gl))
    teacher_no_class = [
        teacher_id
        for teacher_id in teachers
        if teacher_id not in best_solution.values()
    ]
    print("Số giảng viên không có lớp:", len(teacher_no_class))
    if teacher_no_class:
        print("Danh sách giảng viên không có lớp:", teacher_no_class)

        # Thông tin về các lớp không được phân công
    unassigned_classes = [
        class_id for class_id in classes if class_id not in best_solution
    ]
    print("Số lớp không được phân công:", len(unassigned_classes))
    if unassigned_classes:
        print("Danh sách lớp không được phân công:", unassigned_classes)

    print("\n--- Thông tin chi tiết giảng dạy của từng giảng viên ---")
    for teacher_id, teacher_info in teachers.items():
        print(f"\nGiảng viên {teacher_id}:")
        
        # Lọc các lớp mà giảng viên được phân công
        teaching_schedule = [
            (class_id, classes[class_id])
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        ]
        
        if teaching_schedule:
            total_quy_doi_gio = 0  # Tổng quy đổi giờ của các lớp được phân công
            num_classes = len(teaching_schedule)  # Số lượng lớp được phân công
            
            for class_id, class_info in teaching_schedule:
                total_quy_doi_gio += class_info.get('quy_doi_gio', 0)  # Cộng dồn quy đổi giờ
                
                # In thông tin về các lớp được phân công
                print(
                    f"  - Lớp: {class_id}, Môn: {class_info['subject']}, "
                    f"Thứ: {class_info['day']}, Tiết: {class_info['period']}, "
                    f"Quy đổi giờ: {class_info['quy_doi_gio']}"
                )
            
            # In thêm tổng quy đổi giờ, thời gian giảng viên và số lớp
            time_gl = teacher_info.get('time_gl', 0)  # Giả sử time_gl là thuộc tính của teacher_info
            if time_gl > 0:
                ratio = total_quy_doi_gio / time_gl  # Tính tỷ lệ
            else:
                ratio = 0  # Tránh chia cho 0 nếu time_gl là 0
            
            print(f"  - Tổng thời gian giảng dạy: {total_quy_doi_gio} giờ")
            print(f"  - Thời gian giảng viên: {time_gl} giờ")
            print(f"  - Số lớp được phân công: {num_classes}")
            print(f"  - Tỷ lệ thời gian được phân công/ thời gian giảng viên: {ratio:.2f}")
            
        else:
            print("  Không có lớp nào được phân công.")


            
    # for teacher_id, teacher_info in teachers.items():
    #     print(f"\nGiảng viên {teacher_id}:")
    #     teaching_schedule = [
    #         (class_id, classes[class_id])
    #         for class_id, assigned_teacher in best_solution.items()
    #         if assigned_teacher == teacher_id
    #     ]

    #     # Kiểm tra lớp trùng giờ
    #     schedule_by_day = {}
    #     for class_id, class_info in teaching_schedule:
    #         # Bỏ qua các lớp không có day và period
    #         if 'day' not in class_info or 'period' not in class_info:
    #             continue

    #         # Duyệt qua từng ngày dạy
    #         for day, periods in zip(class_info['day'], class_info['period']):
    #             if day not in schedule_by_day:
    #                 schedule_by_day[day] = []
    #             schedule_by_day[day].append((class_id, class_info, periods))  # Lưu cả periods vào dict

    #     # In lịch dạy và thông báo các lớp trùng giờ
    #     for day, classes_in_day in schedule_by_day.items():
    #         checked_classes = []
    #         for i, (class_id_1, class_info_1, periods_1) in enumerate(classes_in_day):
    #             for j, (class_id_2, class_info_2, periods_2) in enumerate(classes_in_day):
    #                 if i >= j or (class_id_1, class_id_2) in checked_classes:
    #                     continue

    #                 # Kiểm tra giao giữa các tiết học
    #                 period_1 = set(periods_1)  # Chuyển periods thành set
    #                 period_2 = set(periods_2)
    #                 if period_1 & period_2:  # Có giao nhau
    #                     print(
    #                         f"  - *** Cảnh báo: Trùng giờ tại Thứ {day}:"
    #                         f"\n    + Lớp: {class_id_1}, Môn: {class_info_1['subject']}, Tiết: {periods_1}"
    #                         f"\n    + Lớp: {class_id_2}, Môn: {class_info_2['subject']}, Tiết: {periods_2}"
    #                     )
    #                     checked_classes.append((class_id_1, class_id_2))
    #                 else:
    #                     print(
    #                         f"  - Lớp: {class_id_1}, Môn: {class_info_1['subject']}, "
    #                         f"Thứ: {class_info_1['day']}, Tiết: {class_info_1['period']}"
    #                     )
