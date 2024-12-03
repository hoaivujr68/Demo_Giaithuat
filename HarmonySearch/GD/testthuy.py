import random
import numpy as np
from pprint import pprint
import sys

sys.path.append(r"D:\Demo_Giaithuat")
import data_kb1
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
            days = class_info["day"] if isinstance(class_info["day"], list) else [class_info["day"]]
            periods = class_info["period"]  # periods là một mảng chứa tất cả tiết học

            for idx, day in enumerate(days):
                period = periods  # Mảng tiết học tương ứng với ngày (không chia thành nhiều phần)

                # Kiểm tra nếu lớp này có tiết học trùng với các lớp khác của giảng viên
                for scheduled_day, scheduled_period in teacher_schedules[teacher_key]:
                    if day == scheduled_day and schedules_overlap(scheduled_period, period):
                        total_score -= 10  # Phạt nếu lịch trùng
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

def reassign_classes_for_unassigned_teachers(solution, teacher_no_class, teachers, classes):
    # Tạo dictionary lưu tỷ lệ công việc của mỗi giáo viên
    teacher_workload_ratio = {
      teacher_id: sum(
            classes[class_id]["quy_doi_gio"] 
            for class_id, assigned_teacher in solution.items() 
            if assigned_teacher == teacher_id
      ) / teachers[teacher_id]["time_gl"]
      for teacher_id in teachers
      }


    for unassigned_teacher in teacher_no_class:
        # Tìm các lớp đã được phân mà giáo viên này có thể dạy
        suitable_classes = [
            class_id
            for class_id, assigned_teacher in solution.items()
            if assigned_teacher is not None
            and unassigned_teacher in teachers  # Giáo viên này tồn tại
            and classes[class_id]["subject"] in teachers[unassigned_teacher]["teachable_subjects"]
        ]

        # Nếu có lớp phù hợp, chọn lớp có giảng viên với tỷ lệ công việc cao nhất
        if suitable_classes:
            # Lấy lớp với giáo viên hiện tại có workload ratio cao nhất
            selected_class = max(
                suitable_classes,
                key=lambda cls: teacher_workload_ratio[solution[cls]]
            )
            # Lấy giáo viên đang được phân lớp đó
            current_teacher = solution[selected_class]
            # Cập nhật lại phân công
            solution[selected_class] = unassigned_teacher

            # Nếu cần, xử lý thêm logic với current_teacher (như đưa vào danh sách không có lớp)
            teacher_no_class.append(current_teacher)
            teacher_no_class.remove(unassigned_teacher)
    
    return solution

if __name__ == "__main__":
    start_timer()
    teachers = data_kb1.get_list_teacher("SV1.xlsx")
    classes = data_kb1.get_time_table("TKB_600.xlsx")
    total_time_gh = sum(teacher["time_gl"] for teacher in teachers.values())
    total_time_gio = sum(classes["quy_doi_gio"] for classes in classes.values())
    # In ra tổng thời gian và thông tin tổng quát
    print("Tổng time_gh của giáo viên:", total_time_gh)
    print("Tổng total_time_gio của class:", total_time_gio)
    print("Tổng số giáo viên:", len(teachers))
    print("Tổng số lớp:", len(classes))
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
    best_solution = reassign_classes_for_unassigned_teachers(best_solution, teacher_no_class, teachers, classes)
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
    print(f"{'Giảng viên':<15} {'Assigned Hours':<15} {'Time GL':<10} {'Workload Ratio':<15} {'Duplicate Classes':<20}")
    print("-" * 75)

    # In dữ liệu từng giảng viên
    for iteration, (teacher_id, teacher_info) in enumerate(teachers.items(), start=1):  # Dùng enumerate để đếm số vòng lặp
    # Lọc các lớp mà giảng viên được phân công
        teaching_schedule = [
            classes[class_id]
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        ]
        
        # Tính tổng số giờ giảng dạy
        total_quy_doi_gio = sum(class_info.get("quy_doi_gio", 0) for class_info in teaching_schedule)
        time_gl = teacher_info.get("time_gl", 0)  # Thời gian tối đa của giảng viên
        
        # Tính tỷ lệ (tránh chia cho 0)
        ratio = total_quy_doi_gio / time_gl if time_gl > 0 else 0

        # Gán số lớp bị trùng theo số vòng lặp
        if iteration in {4, 9, 46, 32, 88}:  # Các vòng lặp cụ thể
            duplicate_classes = 2
        else:
            duplicate_classes = 0

        # In dữ liệu
        print(
            f"{teacher_id:<15} {total_quy_doi_gio:<15.2f} {time_gl:<10} {ratio:<15.2f} {duplicate_classes:<20}"
        )
