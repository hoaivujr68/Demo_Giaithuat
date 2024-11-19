from math import gamma
import numpy as np
import optuna
import json
import optuna.visualization as viz
import plotly

# Khởi tạo hàm Levy Flight
def levy_flight(beta):
    sigma = (
        np.sqrt(gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2)))
    )
    u = np.random.normal(0, sigma)
    v = np.random.normal(0, 1)
    return u / abs(v) ** (1 / beta)

# Khởi tạo quần thể
def init_population(pop_size, num_teachers, num_classes):
    population = np.random.randint(0, 2, (pop_size, num_teachers, num_classes))

    for p in range(pop_size):
        individual = population[p]
        # Đảm bảo mỗi giảng viên có ít nhất một lớp
        for i in range(num_teachers):
            if np.sum(individual[i, :]) == 0:
                individual[i, np.random.randint(0, num_classes)] = 1
        # Đảm bảo mỗi lớp có ít nhất một giảng viên
        for j in range(num_classes):
            if np.sum(individual[:, j]) == 0:
                individual[np.random.randint(0, num_teachers), j] = 1

    return population


def evaluate(individual, teachers, classes, penalty_weights):
    penalty = 0
    score = 0
    class_keys = list(classes.keys())
    teacher_keys = list(teachers.keys())

    # Ràng buộc 1: Mỗi lớp chỉ có một giảng viên
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) > 1:
            penalty += penalty_weights["class_conflict"]

    # Ràng buộc 2: Giảng viên chỉ dạy các môn mà họ có thể dạy
    for i in range(individual.shape[0]):
        teacher_key = teacher_keys[i]
        for j in range(individual.shape[1]):
            class_key = class_keys[j]
            if individual[i, j] == 1 and classes[class_key]["subject"] not in teachers[teacher_key]["teachable_subjects"]:
                penalty += penalty_weights["invalid_subject"]

    for i in range(individual.shape[0]):
        if np.sum(individual[i, :]) == 0:
            penalty += penalty_weights["no_assignment_teacher"]  # Trọng số phạt nếu không có lớp

    # Ràng buộc 5: Tất cả môn học phải có giảng viên giảng dạy
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) == 0:
            penalty += penalty_weights["no_teacher_class"]  # Trọng số phạt nếu lớp không có giảng viên

    # Tính điểm dựa trên số lớp được phân công hợp lệ
    score += np.sum(individual) * 10
    return score - penalty

    # # Ràng buộc 3: Tổng giờ giảng không vượt quá giới hạn
    # for i in range(individual.shape[0]):
    #     teacher_key = teacher_keys[i]
    #     total_hours = np.sum(individual[i, :] * [classes[class_key]["quy_doi_gio"] for class_key in class_keys])
    #     max_hours = teachers[teacher_key]["time_gl"]
    #     if total_hours > 2 * max_hours:
    #         penalty += penalty_weights["over_hours"]

    # Ràng buộc 4: Mỗi giảng viên phải được phân công ít nhất một môn

# Thuật toán Cuckoo Search
def cuckoo_search(teachers, classes, pop_size, max_iter, pa, beta, penalty_weights):
    num_teachers = len(teachers)
    num_classes = len(classes)

    # Khởi tạo quần thể
    population = init_population(pop_size, num_teachers, num_classes)
    fitness = np.array([evaluate(ind, teachers, classes, penalty_weights) for ind in population])
    best_individual = population[np.argmax(fitness)]
    best_fitness = np.max(fitness)

    for iteration in range(max_iter):
        new_population = []
        for ind in population:
            step_size = levy_flight(beta)
            step_direction = np.random.randint(0, 2, (num_teachers, num_classes))
            new_ind = (ind + step_size * step_direction).astype(int)
            new_ind = np.clip(new_ind, 0, 1)
            new_population.append(new_ind)

        new_population = np.array(new_population)
        new_fitness = np.array([evaluate(ind, teachers, classes, penalty_weights) for ind in new_population])

        # Cập nhật tổ tốt hơn
        better_idx = new_fitness > fitness
        population[better_idx] = new_population[better_idx]
        fitness[better_idx] = new_fitness[better_idx]

        # Cập nhật tổ tốt nhất
        if np.max(fitness) > best_fitness:
            best_individual = population[np.argmax(fitness)]
            best_fitness = np.max(fitness)

        # Loại bỏ tổ xấu (pa% tổ ngẫu nhiên bị thay thế)
        abandon_count = int(pa * pop_size)
        random_indices = np.random.choice(pop_size, abandon_count, replace=False)
        for idx in random_indices:
            population[idx] = np.random.randint(0, 2, (num_teachers, num_classes))
            fitness[idx] = evaluate(population[idx], teachers, classes, penalty_weights)

    return best_individual, best_fitness

# Hàm mục tiêu cho Optuna
def objective(trial):
    # Lấy tham số từ Optuna
    pop_size = trial.suggest_int("pop_size", 40, 100)
    max_iter = trial.suggest_int("max_iter", 200, 400)
    pa = trial.suggest_float("pa", 0.2, 0.4)
    beta = trial.suggest_float("beta", 1.2, 1.8)
    penalty_weights = {
        "class_conflict": trial.suggest_int("over_hours_weight", 100, 200),
        "invalid_subject": trial.suggest_int("over_hours_weight", 100, 200),
        # "over_hours": trial.suggest_int("over_hours_weight", 100, 300),
        "no_assignment_teacher": trial.suggest_int("over_hours_weight", 100, 200),
        "no_teacher_class": trial.suggest_int("over_hours_weight", 100, 200),
    }

    # Chạy thuật toán
    best_solution, best_score = cuckoo_search(
        teachers, classes, pop_size, max_iter, pa, beta, penalty_weights
    )

    return best_score

# Chạy tối ưu hóa với Optuna
if __name__ == "__main__":
    import data_kb1

    # Tải dữ liệu
    teachers = data_kb1.get_list_teacher("SV1.xlsx")
    classes = data_kb1.get_time_table("TKB_600.xlsx")

    # Tối ưu hóa với Optuna
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=10)

    fig = viz.plot_optimization_history(study)
    fig.write_html("optimization_history.html")

    # In kết quả tốt nhất
    print("Best Parameters:", study.best_params)
    print("Best Score:", study.best_value)

    # Ghi kết quả vào file JSON
    with open("best_params.json", "w", encoding="utf-8") as f:
        json.dump(study.best_params, f, indent=4)
