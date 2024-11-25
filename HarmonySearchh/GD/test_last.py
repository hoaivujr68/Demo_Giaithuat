import random
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import data_kb1

teachers = data_kb1.get_list_teacher('SV1.xlsx')
classes = data_kb1.get_time_table('TKB_600.xlsx')

# Các tham số của Harmony Search
HMS = 50  # Kích thước bộ nhớ hòa âm
HMCR = 0.9  # Harmony Memory Consideration Rate
PAR = 0.3  # Pitch Adjustment Rate
iterations = 1000  # Số lần lặp tối đa

# Khởi tạo bộ nhớ hòa âm (Harmony Memory)
def initialize_harmony_memory():
    harmony_memory = []
    for _ in range(HMS):
        solution = {}
        for class_id, class_info in classes.items():
            assigned_teacher = None
            possible_teachers = [
                teacher_id for teacher_id, teacher_info in teachers.items()
                if class_info["subject"] in teacher_info["teachable_subjects"]
            ]
            if possible_teachers:
                assigned_teacher = random.choice(possible_teachers)
            solution[class_id] = assigned_teacher
        harmony_memory.append(solution)
    return harmony_memory

# Hàm đánh giá (evaluate) lời giải
def evaluate_solution(solution):
    total_classes_assigned = 0
    teacher_workload = {teacher_id: 0 for teacher_id in teachers}

    for class_id, teacher_id in solution.items():
        if teacher_id is not None:
            total_classes_assigned += 1
            teacher_workload[teacher_id] += classes[class_id]["quy_doi_gio"]

    # Kiểm tra ràng buộc
    for teacher_id, workload in teacher_workload.items():
        if workload > 2 * teachers[teacher_id]["time_gl"]:
            return -1  # Lời giải không hợp lệ

    return total_classes_assigned

# Cải thiện lời giải mới (Improvisation)
def create_new_solution(harmony_memory):
    new_solution = {}
    for class_id, class_info in classes.items():
        if random.random() < HMCR:  # Chọn từ bộ nhớ hòa âm
            new_solution[class_id] = random.choice([
                solution[class_id] for solution in harmony_memory
            ])
        else:  # Tạo ngẫu nhiên
            possible_teachers = [
                teacher_id for teacher_id, teacher_info in teachers.items()
                if class_info["subject"] in teacher_info["teachable_subjects"]
            ]
            new_solution[class_id] = random.choice(possible_teachers) if possible_teachers else None

        if new_solution[class_id] and random.random() < PAR and possible_teachers:
            new_solution[class_id] = random.choice(possible_teachers)

    return new_solution

# Cập nhật bộ nhớ hòa âm
def update_harmony_memory(harmony_memory, new_solution):
    worst_solution = min(harmony_memory, key=evaluate_solution)
    if evaluate_solution(new_solution) > evaluate_solution(worst_solution):
        harmony_memory.remove(worst_solution)
        harmony_memory.append(new_solution)

# Hàm chính của Harmony Search
def harmony_search():
    harmony_memory = initialize_harmony_memory()
    best_solution = max(harmony_memory, key=evaluate_solution)

    for _ in range(iterations):
        new_solution = create_new_solution(harmony_memory)
        update_harmony_memory(harmony_memory, new_solution)
        current_best = max(harmony_memory, key=evaluate_solution)
        if evaluate_solution(current_best) > evaluate_solution(best_solution):
            best_solution = current_best

    return best_solution, evaluate_solution(best_solution)

if __name__ == "__main__":
      # teachers = data_kb1.get_list_teacher('SV1.xlsx')
      # classes = data_kb1.get_time_table('TKB_600.xlsx')

      best_solution, best_score = harmony_search()

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
            if time_thuc_te > 2 * time_max:
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

