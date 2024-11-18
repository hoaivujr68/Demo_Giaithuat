import json
import numpy as np
import pandas as pd
from math import gamma
from pprint import pprint
import optuna
import numpy as np
import data_kb1
import getdata

# Khởi tạo hàm Levy Flight
def levy_flight(beta):
    sigma = (
        gamma(1 + beta) * np.sin(np.pi * beta / 2) / (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = np.random.normal(0, sigma)
    v = np.random.normal(0, 1)
    step = u / abs(v) ** (1 / beta)
    return step

# Khởi tạo quần thể
def init_population(pop_size, num_teachers, num_classes):
    population = []
    for _ in range(pop_size):
        # Ma trận nhị phân kích thước [num_teachers x num_classes]
        individual = np.random.randint(0, 2, (num_teachers, num_classes))
        population.append(individual)
    return np.array(population)

def evaluate(individual, teachers, classes):
    penalty = 0
    score = 0

    # Lấy danh sách các khóa của classes và teachers
    class_keys = list(classes.keys())
    teacher_keys = list(teachers.keys())

    # Ràng buộc 1: Mỗi lớp chỉ có một giảng viên
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) > 1:
            penalty += 100   # Phạt nặng hơn nếu một lớp có nhiều giảng viên

    # Ràng buộc 2: Giảng viên chỉ dạy các môn mà họ có thể dạy
    for i in range(individual.shape[0]):
        teacher_key = teacher_keys[i]
        for j in range(individual.shape[1]):
            class_key = class_keys[j]
            if individual[i, j] == 1 and classes[class_key]["subject"] not in teachers[teacher_key]["teachable_subjects"]:
                penalty += 100   # Phạt nặng nếu giảng viên dạy môn không hợp lệ

    # # Ràng buộc 3: Tổng số giờ giảng dạy của giáo viên phải bé hơn 2 lần số giờ tối đa
    for i in range(individual.shape[0]):
        if np.sum(individual[i, :]) == 0:
            penalty += 100  # Trọng số phạt nếu không có lớp

    # Ràng buộc 5: Tất cả môn học phải có giảng viên giảng dạy
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) == 0:
            penalty += 100
    # for i in range(individual.shape[0]):
    #     teacher_key = teacher_keys[i]
    #     total_hours = np.sum(individual[i, :] * [classes[class_key]["quy_doi_gio"] for class_key in class_keys])
    #     max_hours = teachers[teacher_key]["time_gl"]
    #     if total_hours > 2 * max_hours:
    #         penalty += 100
            
        # Ràng buộc 4: Mỗi giảng viên phải được phân công ít nhất một môn

    return score - penalty


# Thuật toán Cuckoo Search
def cuckoo_search(teachers, classes, pop_size=50, max_iter=200, pa=0.25, beta=1.5):
    num_teachers = len(teachers)
    num_classes = len(classes)

    # Khởi tạo quần thể
    population = init_population(pop_size, num_teachers, num_classes)
    fitness = np.array([evaluate(ind, teachers, classes) for ind in population])

    best_individual = population[np.argmax(fitness)]
    best_fitness = np.max(fitness)

    for iteration in range(max_iter):
        new_population = np.empty_like(population)
        for idx, individual in enumerate(population):
            step_size = levy_flight(beta)
            step_direction = np.random.randint(0, 2, (num_teachers, num_classes))
            new_individual = (individual + step_size * step_direction).astype(int)
            new_individual = np.clip(new_individual, 0, 1)
            new_population[idx] = new_individual

        # Tính toán fitness cho quần thể mới
        new_fitness = np.array([evaluate(ind, teachers, classes) for ind in new_population])

        # Cập nhật tổ tốt hơn
        better_idx = new_fitness > fitness
        population[better_idx] = new_population[better_idx]
        fitness[better_idx] = new_fitness[better_idx]

        # Cập nhật tổ tốt nhất
        if np.max(fitness) > best_fitness:
            best_individual = population[np.argmax(fitness)]
            best_fitness = np.max(fitness)
            
        abandon_count = int(pa * pop_size)
        random_indices = np.random.choice(pop_size, abandon_count, replace=False)
        for idx in random_indices:
            population[idx] = np.random.randint(0, 2, (num_teachers, num_classes))
            fitness[idx] = evaluate(population[idx], teachers, classes)

        print(f"Iteration {iteration + 1}/{max_iter}: Best Fitness = {best_fitness}")

    return best_individual, best_fitness

import json

if __name__ == "__main__":
    from pprint import pprint
    import data_kb1

    # Lấy dữ liệu từ file Excel
    teachers = data_kb1.get_list_teacher('SV1.xlsx')
    classes = data_kb1.get_time_table('TKB_600.xlsx')
    with open('classes_try.json', 'w', encoding='utf-8') as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)
        
    with open('teachers_try.json', 'w', encoding='utf-8') as teachers123_file:
        json.dump(teachers, teachers123_file, ensure_ascii=False, indent=4)

    # Chạy thuật toán Cuckoo Search
    best_solution, best_score = cuckoo_search(teachers, classes)

    print("Best Solution:")
    pprint(best_solution)
    print("Best Score:", best_score)

    # Danh sách khóa
    teacher_keys = list(teachers.keys())
    class_keys = list(classes.keys())

   # In thông tin phân công lớp cho giảng viên
    teacher_assignments = {}
    classes_no_teacher = []  # Danh sách lớp không có giảng viên
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

    # Ghi vào file JSON
    with open("result.json", "w", encoding="utf-8") as file:
        json.dump(teacher_assignments, file, indent=4, ensure_ascii=False)

    with open("classes_no_teacher.json", "w", encoding="utf-8") as file:
        json.dump(classes_no_teacher, file, indent=4, ensure_ascii=False)
    print("\nThông tin phân công đã được ghi vào file 'result.json'")


