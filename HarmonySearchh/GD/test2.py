import random
import numpy as np
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import data_kb1

teachers = data_kb1.get_list_teacher('SV1.xlsx')
classes = data_kb1.get_time_table('TKB_600.xlsx')

# Ma trận giảng viên - lớp
teacher_ids = list(teachers.keys())
class_ids = list(classes.keys())
N = len(teacher_ids)  # Số giảng viên
M = len(class_ids)    # Số lớp

# Chuyển đổi từ tên giảng viên và lớp thành chỉ số
teacher_index = {tid: i for i, tid in enumerate(teacher_ids)}
class_index = {cid: j for j, cid in enumerate(class_ids)}

# Các tham số Harmony Search
HMS = 5  # Kích thước bộ nhớ hòa âm
HMCR = 0.9  # Harmony Memory Consideration Rate
PAR = 0.3  # Pitch Adjustment Rate
iterations = 100  # Số lần lặp tối đa

# Hàm kiểm tra tính khả thi của lời giải
def is_feasible(solution):
    # Kiểm tra mỗi lớp chỉ có một giảng viên
    for j in range(M):
        if sum(solution[:, j]) != 1:
            return False
    
    # Kiểm tra giới hạn thời gian của giảng viên
    teacher_workload = np.zeros(N)
    for i in range(N):
        for j in range(M):
            teacher_workload[i] += solution[i][j] * classes[class_ids[j]]["quy_doi_gio"]
        if teacher_workload[i] > 2 *teachers[teacher_ids[i]]["time_gl"]:
            return False
    return True

# Hàm khởi tạo bộ nhớ hòa âm
def initialize_harmony_memory():
    harmony_memory = []
    while len(harmony_memory) < HMS:
        solution = np.zeros((N, M), dtype=int)
        for j in range(M):
            possible_teachers = [
                i for i in range(N) 
                if classes[class_ids[j]]["subject"] in teachers[teacher_ids[i]]["teachable_subjects"]
            ]
            if possible_teachers:
                assigned_teacher = random.choice(possible_teachers)
                solution[assigned_teacher][j] = 1
        if is_feasible(solution):
            harmony_memory.append(solution)
    return harmony_memory

# Hàm đánh giá lời giải
def evaluate_solution(solution):
    return np.sum(solution)

# Hàm cải thiện lời giải mới (Improvisation)
def create_new_solution(harmony_memory):
    new_solution = np.zeros((N, M), dtype=int)
    for j in range(M):
        if random.random() < HMCR:  # Memory consideration
            new_solution[:, j] = random.choice(harmony_memory)[:, j]
        else:  # Random consideration
            possible_teachers = [
                i for i in range(N) 
                if classes[class_ids[j]]["subject"] in teachers[teacher_ids[i]]["teachable_subjects"]
            ]
            if possible_teachers:
                assigned_teacher = random.choice(possible_teachers)
                new_solution[assigned_teacher][j] = 1

        # Pitch adjustment
        if random.random() < PAR:
            possible_teachers = [
                i for i in range(N) 
                if classes[class_ids[j]]["subject"] in teachers[teacher_ids[i]]["teachable_subjects"]
            ]
            if possible_teachers:
                new_solution[:, j] = 0  # Reset column
                assigned_teacher = random.choice(possible_teachers)
                new_solution[assigned_teacher][j] = 1

    return new_solution if is_feasible(new_solution) else None

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
        if new_solution is not None:
            update_harmony_memory(harmony_memory, new_solution)
            current_best = max(harmony_memory, key=evaluate_solution)
            if evaluate_solution(current_best) > evaluate_solution(best_solution):
                best_solution = current_best

    return best_solution, evaluate_solution(best_solution)

# Chạy giải thuật Harmony Search
best_solution, best_value = harmony_search()
print("Best Solution:\n", best_solution)
print("Best Value (Total Classes Assigned):", best_value)
