import random
import numpy as np
from pprint import pprint
import sys

sys.path.append(r"D:\Demo_Giaithuat")
import getdata1

# Harmony Search parameters
HARMONY_MEMORY_SIZE = 100
HARMONY_MEMORY_CONSIDERATION_RATE = 0.9
PITCH_ADJUSTMENT_RATE = 0.3
MAX_ITERATIONS = 1000

def calculate_workload(teacher, assignment):
    return sum(
        classes[class_id]["quy_doi_gio"]
        for class_id, teacher_id in assignment.items()
        if teacher_id == teacher
    )

def generate_random_harmony():
    harmony = {}
    for class_id, class_info in classes.items():
        eligible_teachers = [
            teacher_id
            for teacher_id, teacher_info in teachers.items()
            if class_info["subject"] in teacher_info["teachable_subjects"]
        ]
        if eligible_teachers:
            harmony[class_id] = random.choice(eligible_teachers)

    return harmony


# Objective function to calculate the quality of a solution
def objective_function(harmony):
    total_utility = 0

    for class_id, teacher_id in harmony.items():
        if teacher_id in teachers:
            class_info = classes[class_id]
            teacher_info = teachers[teacher_id]

            current_workload = calculate_workload(teacher_id, harmony)
            max_workload = teacher_info["time_gl"] * 2

            if current_workload > max_workload:
                total_utility -= 10
            else:
                total_utility += 1

    return total_utility


# Hàm cập nhật hòa âm
def update_harmony(harmony_memory, teachers, classes, new_solution):
    # Xóa các phần tử cũ nếu giải pháp mới tốt hơn
    worst_solution = min(harmony_memory, key=lambda sol: objective_function(sol))
    worst_score = objective_function(worst_solution)
    new_score = objective_function(new_solution)

    if new_score > worst_score:
        harmony_memory.remove(worst_solution)
        harmony_memory.append(new_solution)
    return harmony_memory


def harmony_search_teaching_assignment(teachers, classes):
    harmony_memory = []
    for _ in range(HARMONY_MEMORY_SIZE):
        harmony = generate_random_harmony()
        harmony_memory.append(harmony)

    # best_harmony = None
    best_harmony = max(harmony_memory, key=objective_function)

    # Main Harmony Search loop
    for _ in range(MAX_ITERATIONS):
        new_harmony = {}
        for class_id, class_info in classes.items():
            eligible_teachers = [
                teacher_id
                for teacher_id, teacher_info in teachers.items()
                if class_info["subject"] in teacher_info["teachable_subjects"]
                and teachers[teacher_id]["time_gl"] * 2
                >= calculate_workload(teacher_id, new_harmony)
                + class_info["quy_doi_gio"]
            ]
            if eligible_teachers:
                random_teacher = random.choice(eligible_teachers)
                if (
                    calculate_workload(random_teacher, new_harmony)
                    + class_info["quy_doi_gio"]
                    <= 2 * teachers[random_teacher]["time_gl"]
                ):
                    new_harmony[class_id] = random_teacher
                else:
                    new_harmony[class_id] = None
        harmony_memory = update_harmony(harmony_memory, teachers, classes, new_harmony)

    return best_harmony, objective_function(best_harmony)


if __name__ == "__main__":
    teachers = getdata1.get_list_teacher("NCM2.xlsx")
    classes = getdata1.get_time_table("TKB1.xlsx")

    best_solution, best_score = harmony_search_teaching_assignment(teachers, classes)

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
        if time_thuc_te > time_max:
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
        teaching_schedule = [
            (class_id, classes[class_id])
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        ]
        if teaching_schedule:
            for class_id, class_info in teaching_schedule:
                print(
                    f"  - Lớp: {class_id}, Môn: {class_info['subject']}, "
                    f"Thứ: {class_info['day']}, Tiết: {class_info['period']}"
                )
        else:
            print("  Không có lớp nào được phân công.")
