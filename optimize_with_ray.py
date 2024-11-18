from math import gamma
import numpy as np
from ray.tune.schedulers import ASHAScheduler
import json
import os
from ray import tune
import ray

# Tạo thư mục lưu trữ kết quả và thư mục tạm nếu chưa có
os.makedirs("C:/ray_results", exist_ok=True)
os.makedirs("C:/ray_temp", exist_ok=True)

# Khởi tạo Ray với thư mục tạm tùy chỉnh
ray.init(_temp_dir="C:/ray_temp")

# Tùy chỉnh tên thử nghiệm để rút ngắn đường dẫn
def custom_trial_name_creator(trial):
    return f"trial_{trial.trial_id}"

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
    return np.random.randint(0, 2, (pop_size, num_teachers, num_classes))

# Hàm đánh giá
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

    # Ràng buộc 4: Mỗi giảng viên phải được phân công ít nhất một môn
    for i in range(individual.shape[0]):
        if np.sum(individual[i, :]) == 0:
            penalty += penalty_weights["no_assignment_teacher"]

    # Ràng buộc 5: Tất cả môn học phải có giảng viên giảng dạy
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) == 0:
            penalty += penalty_weights["no_teacher_class"]

    # Tính điểm dựa trên số lớp được phân công hợp lệ
    score += np.sum(individual)
    return score - penalty

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

# Hàm mục tiêu để tối ưu hóa
def objective(config):
    pop_size = config["pop_size"]
    max_iter = config["max_iter"]
    pa = config["pa"]
    beta = config["beta"]
    penalty_weights = {
        "class_conflict": config["class_conflict_weight"],
        "invalid_subject": config["invalid_subject_weight"],
        "no_assignment_teacher": config["no_assignment_teacher_weight"],
        "no_teacher_class": config["no_teacher_class_weight"],
    }

    # Chạy thuật toán Cuckoo Search
    best_solution, best_score = cuckoo_search(
        teachers, classes, pop_size, max_iter, pa, beta, penalty_weights
    )

    # Báo cáo điểm
    tune.report(score=best_score)

# Không gian tìm kiếm tham số
search_space = {
    "pop_size": tune.randint(10, 101),
    "max_iter": tune.randint(50, 501),
    "pa": tune.uniform(0.1, 0.5),
    "beta": tune.uniform(1.2, 2.0),
    "class_conflict_weight": tune.randint(100, 501),
    "invalid_subject_weight": tune.randint(100, 501),
    "no_assignment_teacher_weight": tune.randint(100, 501),
    "no_teacher_class_weight": tune.randint(100, 501),
}

def custom_trial_name_creator(trial):
    return f"trial_{trial.trial_id}"

if __name__ == "__main__":
    import ray
    import data_kb1

    # Tải dữ liệu
    teachers = data_kb1.get_list_teacher("SV1.xlsx")
    classes = data_kb1.get_time_table("TKB_600.xlsx")

    # Khởi tạo Ray
    ray.init()

    # Lịch trình dừng sớm
    scheduler = ASHAScheduler(
        metric="score",
        mode="max",
        max_t=500,
        grace_period=10,
        reduction_factor=2,
    )

    # Chạy Ray Tune
    analysis = tune.run(
        objective,
        config=search_space,
        num_samples=50,
        scheduler=scheduler,
        storage_path="C:/ray_results", 
        trial_name_creator=custom_trial_name_creator,
    )

    # Lấy kết quả tốt nhất
    best_config = analysis.get_best_config(metric="score", mode="max")
    best_score = analysis.get_best_trial(metric="score", mode="max").last_result["score"]

    print("Best Parameters:", best_config)
    print("Best Score:", best_score)

    # Lưu tham số tốt nhất
    with open("best_params_ray.json", "w", encoding="utf-8") as f:
        json.dump(best_config, f, indent=4)

    # Tắt Ray
    ray.shutdown()
