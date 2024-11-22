import json
import numpy as np
import pandas as pd
from math import gamma
from pprint import pprint
import optuna
import numpy as np
import data_kb1
import getdata

import numpy as np 

# Khởi tạo hàm Levy Flight
def levy_flight(beta):
    sigma = (
        gamma(1 + beta) * np.sin(np.pi * beta / 2) / 
        (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = np.random.normal(0, sigma)
    v = np.random.normal(0, 1)
    step = u / abs(v) ** (1 / beta)
    return step

# Hàm khởi tạo quần thể
def init_population(pop_size, num_teachers, num_classes):
    return np.random.randint(0, 2, (pop_size, num_teachers, num_classes))

# Hàm tính fitness
def evaluate(individual, teachers, classes, teacher_subject_matrix):
    penalty = 0
    score = 0

    class_keys = list(classes.keys())
    teacher_keys = list(teachers.keys())

    # Ràng buộc 1: Mỗi lớp chỉ có một giảng viên
    for j in range(individual.shape[1]):
        assigned_teachers = np.sum(individual[:, j])
        if assigned_teachers > 1:
            penalty += 200
        elif assigned_teachers == 0:
            penalty += 150
        else:
            score += 10

    # Ràng buộc 2: Mỗi giảng viên được phân ít nhất 1 môn
    for i in range(individual.shape[0]):
        if np.sum(individual[i, :]) == 0:
            penalty += 100
        else:
            score += 10

    # Ràng buộc 3: Giảng viên chỉ dạy môn hợp lệ
    for i in range(individual.shape[0]):
        invalid_assignments = np.sum(
            individual[i, :] * (1 - teacher_subject_matrix[i, :])
        )
        penalty += invalid_assignments * 100

    # Ràng buộc 4: Giờ dạy thực tế < tối đa 2 lần giờ max
    for i in range(individual.shape[0]):
        total_hours = np.sum(individual[i, :] * [classes[key]["quy_doi_gio"] for key in class_keys])
        max_hours = teachers[teacher_keys[i]]["time_gl"]
        if total_hours > 2 * max_hours:
            penalty += 300
        elif total_hours < max_hours:
            penalty += 50
        else:
            score += 10

    return score - penalty

# Cuckoo Search cải tiến
def cuckoo_search(teachers, classes, pop_size=25, max_iter=50, pa=0.25, beta=1.5):
    num_teachers = len(teachers)
    num_classes = len(classes)

    # Khởi tạo quần thể
    population = init_population(pop_size, num_teachers, num_classes)

    # Ma trận khả năng dạy
    teacher_keys = list(teachers.keys())
    class_keys = list(classes.keys())
    teacher_subject_matrix = np.zeros((num_teachers, num_classes), dtype=int)
    for i, teacher_key in enumerate(teacher_keys):
        for j, class_key in enumerate(class_keys):
            if classes[class_key]["subject"] in teachers[teacher_key]["teachable_subjects"]:
                teacher_subject_matrix[i, j] = 1

    fitness = np.array([evaluate(ind, teachers, classes, teacher_subject_matrix) for ind in population])
    best_individual = population[np.argmax(fitness)]
    best_fitness = np.max(fitness)

    for iteration in range(max_iter):
        # Tạo quần thể mới bằng Lévy Flight
        new_population = []
        for ind in population:
            step_size = levy_flight(beta)
            step_direction = np.random.randint(0, 2, ind.shape)
            new_ind = (ind + step_size * step_direction).astype(int)
            new_ind = np.clip(new_ind, 0, 1)
            new_population.append(new_ind)
        new_population = np.array(new_population)

        # Cập nhật fitness
        new_fitness = np.array([evaluate(ind, teachers, classes, teacher_subject_matrix) for ind in new_population])
        better_idx = new_fitness > fitness
        population[better_idx] = new_population[better_idx]
        fitness[better_idx] = new_fitness[better_idx]

        # Cập nhật cá thể tốt nhất
        if np.max(fitness) > best_fitness:
            best_individual = population[np.argmax(fitness)]
            best_fitness = np.max(fitness)

        # Thay thế pa% cá thể tồi nhất
        abandon_count = int(pa * pop_size)
        worst_indices = np.argsort(fitness)[:abandon_count]
        for idx in worst_indices:
            population[idx] = np.random.randint(0, 2, (num_teachers, num_classes))
            fitness[idx] = evaluate(population[idx], teachers, classes, teacher_subject_matrix)
            
              # Cập nhật cá thể tốt nhất
        if np.max(fitness) > best_fitness:
            best_individual = population[np.argmax(fitness)]
            best_fitness = np.max(fitness)

        print(f"Iteration {iteration + 1}/{max_iter}: Best Fitness = {best_fitness}")

    return best_individual, best_fitness


if __name__ == "__main__":
    from pprint import pprint
    import data_kb1

    # Lấy dữ liệu từ file Excel
    teachers = data_kb1.get_list_teacher('SV1.xlsx')
    classes = data_kb1.get_time_table('TKB_600.xlsx')
    total_time_gl = sum(teacher["time_gl"] for teacher in teachers.values())

    # Tính tổng quy_doi_gio của lớp
    total_quy_doi_gio = sum(class_info["quy_doi_gio"] for class_info in classes.values())

    # In ra kết quả
    print("Tổng time_gl của giáo viên:", total_time_gl)
    print("Tổng quy_doi_gio của lớp:", total_quy_doi_gio)
    with open('classes_try.json', 'w', encoding='utf-8') as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)

    with open('teachers_try.json', 'w', encoding='utf-8') as teachers123_file:
        json.dump(teachers, teachers123_file, ensure_ascii=False, indent=4)

    # Chạy thuật toán Cuckoo Search
    best_solution, best_score = cuckoo_search(teachers, classes)

    print("Best Score:", best_score)

    # Danh sách khóa
    teacher_keys = list(teachers.keys())
    class_keys = list(classes.keys())

    # In thông tin phân công lớp cho giảng viên
    teacher_assignments = {}
    classes_no_teacher = []  # Danh sách lớp không có giảng viên
    unassigned_teachers = []  # Danh sách giáo viên không được phân công
    teacher_workload_ratios = {}  # Tỉ lệ giờ được phân trên giờ thực tế

    for j, class_key in enumerate(class_keys):
        assigned = False
        for i, teacher_key in enumerate(teacher_keys):
            if best_solution[i, j] == 1:
                if teacher_key not in teacher_assignments:
                    teacher_assignments[teacher_key] = []
                teacher_assignments[teacher_key].append({
                    "class_key": class_key,
                })
                assigned = True
                break
        if not assigned:
            classes_no_teacher.append({
                "class_key": class_key,
            })

    # Kiểm tra giáo viên không được phân công và tính tỉ lệ
    for i, teacher_key in enumerate(teacher_keys):
        assigned_classes = []
        total_assigned_hours = 0

        for j, class_key in enumerate(class_keys):
            if best_solution[i, j] == 1:  # Nếu giáo viên này được phân công lớp này
                assigned_classes.append(class_key)
                total_assigned_hours += classes[class_key]["quy_doi_gio"]  # Cộng quy_doi_gio

        # Nếu giáo viên không được phân công lớp nào
        if not assigned_classes:
            unassigned_teachers.append(teacher_key)
        else:
            # Lấy giờ thực tế tối đa từ dữ liệu giáo viên
            actual_hours = teachers[teacher_key]["time_gl"]
            workload_ratio = total_assigned_hours / actual_hours if actual_hours > 0 else 0

            teacher_workload_ratios[teacher_key] = {
                "assigned_hours": round(total_assigned_hours, 2),  # Tổng số giờ dạy
                "time_gl": actual_hours,  # Giờ tối đa
                "workload_ratio": round(workload_ratio, 2),  # Tỉ lệ giờ dạy
                "assigned_classes": assigned_classes  # Danh sách các lớp được phân
            }

            # Ghi thông tin vào file JSON

   # Ghi vào file JSON
    with open("result.json", "w", encoding="utf-8") as file:
        json.dump(teacher_assignments, file, indent=4, ensure_ascii=False)
        
    with open("classes_no_teacher.json", "w", encoding="utf-8") as file:
        json.dump(classes_no_teacher, file, indent=4, ensure_ascii=False)
    with open("teacher_workload_ratios.json", "w", encoding="utf-8") as file:
        json.dump(teacher_workload_ratios, file, indent=4, ensure_ascii=False)
    with open("unassigned_teachers.json", "w", encoding="utf-8") as file:
        json.dump(unassigned_teachers, file, indent=4, ensure_ascii=False)
    print("\nThông tin phân công đã được ghi vào file 'result.json'")



