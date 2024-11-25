import random
import numpy as np
from pprint import pprint
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import data_kb1

# Harmony Search parameters
HARMONY_MEMORY_SIZE = 100
HARMONY_MEMORY_CONSIDERATION_RATE = 0.7
PITCH_ADJUSTMENT_RATE = 0.3
MAX_ITERATIONS = 1000
IMPROVISATION_RATE = 0.4


def harmony_search_teaching_assignment(teachers, classes):
    """
    Harmony Search algorithm to solve the teaching assignment problem.
    """
    # Helper function to calculate workload of a teacher
    def calculate_workload(teacher, assignment):
        return sum(
            classes[class_id]["quy_doi_gio"]
            for class_id, teacher_id in assignment.items()
            if teacher_id == teacher
        )

    # Generate a random initial solution
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
            else:
                print(f"Không có giảng viên nào có thể dạy lớp {class_id} ({class_info['subject']})")
        return harmony

    # Objective function to calculate the quality of a solution
    def objective_function(harmony):
        total_utility = 0
        for class_id, teacher_id in harmony.items():
            if teacher_id in teachers:
                total_utility += 100
        return total_utility

    # Check if the harmony is feasible
    def is_feasible(harmony):

        # for class_id, class_info in classes.items():
        #     assigned_teacher = harmony.get(class_id)
        #     if assigned_teacher not in teachers or class_info["subject"] not in teachers[assigned_teacher]["teachable_subjects"]:
        #         return False

        teacher_workloads = {teacher: calculate_workload(teacher, harmony) for teacher in teachers}
        for teacher, workload in teacher_workloads.items():
            if workload > 2 * teachers[teacher]["time_gl"]:
                # print(f"Giảng viên {teacher} vi phạm: Workload {workload} > {2 * teachers[teacher]['time_gl']}.")
                return False
        for teacher in teachers:
            scheduled_classes = [
                class_id
                for class_id, assigned_teacher in harmony.items()
                if assigned_teacher == teacher
            ]
            for class_id1 in scheduled_classes:
                for class_id2 in scheduled_classes:
                    if class_id1 != class_id2 and (
                        classes[class_id1]["day"] == classes[class_id2]["day"]
                        and set(classes[class_id1]["period"]).intersection(classes[class_id2]["period"])
                        and set(classes[class_id1]["week"]).intersection(classes[class_id2]["week"])
                    ):
                        return False

        return True

    # Initialize Harmony Memory
    harmony_memory = []
    for _ in range(HARMONY_MEMORY_SIZE):
        harmony = generate_random_harmony()
        # if is_feasible(harmony):
        harmony_memory.append(harmony)
    if not harmony_memory:
      print("Không tìm thấy lời giải hợp lệ trong Harmony Memory!")
      return None, None

    # best_harmony = None
    best_harmony = max(harmony_memory, key=objective_function)

    # Main Harmony Search loop
    for _ in range(MAX_ITERATIONS):
        new_harmony = {}
        for class_id, class_info in classes.items():
            if random.random() < HARMONY_MEMORY_CONSIDERATION_RATE:
                # Consider harmony memory
                # candidate = random.choice(harmony_memory)
                # new_harmony[class_id] = candidate[class_id]
                candidate = random.choice(harmony_memory)
                
                assigned_teacher = candidate[class_id]

                # Kiểm tra ràng buộc trước khi gán
                if assigned_teacher in teachers and calculate_workload(assigned_teacher, new_harmony) + class_info["quy_doi_gio"] <= 2 * teachers[assigned_teacher]["time_gl"]:
                    new_harmony[class_id] = assigned_teacher
                
                #  # Áp dụng Pitch Adjustment
                # if random.random() < PITCH_ADJUSTMENT_RATE:
                #     eligible_teachers = [
                #         teacher_id
                #         for teacher_id, teacher_info in teachers.items()
                #         if class_info["subject"] in teacher_info["teachable_subjects"]
                #         and teachers[teacher_id]["time_gl"] * 2 >= calculate_workload(teacher_id, new_harmony) + class_info["quy_doi_gio"]
                #     ]
                #     if eligible_teachers:
                #         # Chọn một giảng viên khác ngẫu nhiên
                #         best_teacher = min(eligible_teachers, key=lambda t: calculate_workload(t, new_harmony))
                #         if calculate_workload(best_teacher, new_harmony) + class_info["quy_doi_gio"] <= 2 * teachers[best_teacher]["time_gl"]:
                #             new_harmony[class_id] = best_teacher
                #         else:
                #             print(f"Không thể gán lớp {class_id} cho giảng viên {teacher_id}: Workload vượt quá giới hạn.")
                        
            elif random.random() < IMPROVISATION_RATE:
                # Improvisation step (adjust teacher for the class)
                eligible_teachers = [
                    teacher_id
                    for teacher_id, teacher_info in teachers.items()
                    if class_info["subject"] in teacher_info["teachable_subjects"]
                    and teachers[teacher_id]["time_gl"] * 2 >= calculate_workload(teacher_id, new_harmony) + class_info["quy_doi_gio"]
                ]
                if eligible_teachers:
                    # Ưu tiên giảng viên có ít giờ dạy nhất
                    best_teacher = min(eligible_teachers, key=lambda t: calculate_workload(t, new_harmony))
                    if calculate_workload(best_teacher, new_harmony) + class_info["quy_doi_gio"] <= 2 * teachers[best_teacher]["time_gl"]:
                        new_harmony[class_id] = best_teacher
                        
                    # else:
                    #     print(f"Không thể gán lớp {class_id} cho giảng viên {best_teacher}: Workload vượt quá giới hạn.")
            else:
                # Random assignment
                eligible_teachers = [
                    teacher_id
                    for teacher_id, teacher_info in teachers.items()
                    if class_info["subject"] in teacher_info["teachable_subjects"]
                    and teachers[teacher_id]["time_gl"] * 2 >= calculate_workload(teacher_id, new_harmony) + class_info["quy_doi_gio"]
                ]
                if eligible_teachers:
                    random_teacher = random.choice(eligible_teachers)
                    if calculate_workload(random_teacher, new_harmony) + class_info["quy_doi_gio"] <= 2 * teachers[random_teacher]["time_gl"]:
                        new_harmony[class_id] = random_teacher
                    # else:
                    #     print(f"Không thể gán lớp {class_id} cho giảng viên {best_teacher}: Workload vượt quá giới hạn.")


        # Xử lý lớp chưa được phân công
        unassigned_classes = [class_id for class_id in classes if class_id not in new_harmony]
        if unassigned_classes:
            for class_id in unassigned_classes:
                eligible_teachers = [
                    teacher_id
                    for teacher_id, teacher_info in teachers.items()
                    if classes[class_id]["subject"] in teacher_info["teachable_subjects"]
                    and calculate_workload(teacher_id, new_harmony) + classes[class_id]["quy_doi_gio"] <= 2 * teachers[teacher_id]["time_gl"]
                ]
                if eligible_teachers:
                    new_harmony[class_id] = random.choice(eligible_teachers)
                
        if is_feasible(new_harmony):
            if len(harmony_memory) < HARMONY_MEMORY_SIZE:
                harmony_memory.append(new_harmony)
            else:
                worst_harmony = min(harmony_memory, key=objective_function)
                if objective_function(new_harmony) > objective_function(worst_harmony):
                    harmony_memory.remove(worst_harmony)
                    harmony_memory.append(new_harmony)

            if objective_function(new_harmony) > objective_function(best_harmony):
                best_harmony = new_harmony

    return best_harmony, objective_function(best_harmony)


if __name__ == "__main__":
      teachers = data_kb1.get_list_teacher('SV1.xlsx')
      classes = data_kb1.get_time_table('TKB_600.xlsx')

      best_solution, best_score = harmony_search_teaching_assignment(teachers, classes)

      # Kiểm tra nếu lời giải trả về hợp lệ
      if not best_solution:
            print("Không tìm thấy lời giải hợp lệ!")
            exit()

      # Tính toán thời gian thực tế của giảng viên
      list_over_gl = []
      for teacher_id, teacher_info in teachers.items():
            time_thuc_te = sum(
                  classes[class_id]['quy_doi_gio']
                  for class_id, assigned_teacher in best_solution.items()
                  if assigned_teacher == teacher_id
            )
            time_max = teacher_info["time_gl"]
            if time_thuc_te > time_max:
                  list_over_gl.append((teacher_id, round(time_thuc_te, 2), time_max))

      print('Số giảng viên bị quá GL:', len(list_over_gl))
      for teacher in list_over_gl:
            print(f"Giảng viên {teacher[0]}: {teacher[1]}/{teacher[2]} ({round(teacher[1] / teacher[2] * 100, 2)}%)")

      print('Số giảng viên không bị quá GL:', len(teachers) - len(list_over_gl))
      teacher_no_class = [
            teacher_id for teacher_id in teachers
            if teacher_id not in best_solution.values()
      ]
      print('Số giảng viên không có lớp:', len(teacher_no_class))
      if teacher_no_class:
            print('Danh sách giảng viên không có lớp:', teacher_no_class)
            
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
                print(f"  - Lớp: {class_id}, Môn: {class_info['subject']}, "
                      f"Thứ: {class_info['day']}, Tiết: {class_info['period']}")
        else:
            print("  Không có lớp nào được phân công.")
