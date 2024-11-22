import json
import numpy as np
import pandas as pd
from math import gamma
from pprint import pprint
import numpy as np
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import getdata1

# import getdata1

# Khởi tạo hàm Levy Flight
def levy_flight(beta):
    sigma = (
        gamma(1 + beta) * np.sin(np.pi * beta / 2) / (gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = np.random.normal(0, sigma)
    v = np.random.normal(0, 1)
    step = u / abs(v) ** (1 / beta)
    return step

def init_population(pop_size, num_teachers, num_aspirations, aspirations, teacher_keys):
      # """
      # Khởi tạo quần thể với điều kiện các nguyện vọng có `giang_vien` sẽ được gán trước.
      # """
      # population = []
      # for _ in range(pop_size):
      #       # Ma trận nhị phân kích thước [num_teachers x num_aspirations]
      #       individual = np.zeros((num_teachers, num_aspirations), dtype=int)
            
      #       for j, aspiration in enumerate(aspirations.values()):
      #             if "giang_vien" in aspiration and aspiration["giang_vien"] in teacher_keys:
      #             # Tìm chỉ số của giảng viên trong danh sách teacher_keys
      #                   teacher_index = teacher_keys.index(aspiration["giang_vien"])
      #                   # Gán giảng viên được phân công
      #                   individual[teacher_index, j] = 1
      #             else:
      #             # Random cho các vị trí khác
      #                   teacher_index = np.random.choice(num_teachers)
      #                   individual[teacher_index, j] = 1

      #       population.append(individual)
      population = []
      for _ in range(pop_size):
            # Ma trận nhị phân kích thước [num_teachers x num_classes]
            individual = np.random.randint(0, 2, (num_teachers, num_aspirations))
            population.append(individual)
      return np.array(population)

      return np.array(population)


def evaluate(individual, teachers, aspirations):
    penalty = 0
    score = 0

    # Lấy danh sách các khóa của aspirations và teachers
    aspiration_keys = list(aspirations.keys())
    teacher_keys = list(teachers.keys())

    # Tạo một dictionary lưu tải trọng công việc của từng giảng viên
     # Tạo một dictionary lưu tải trọng công việc của từng giảng viên
    teacher_workloads = {teacher_key: {course_id: 0 for course_id in set(aspiration['course_id'] for aspiration in aspirations.values())} 
                         for teacher_key in teacher_keys}

    # Ràng buộc 1: Mỗi lớp chỉ có một giảng viên
    for j in range(individual.shape[1]):
        if np.sum(individual[:, j]) > 1:
            penalty += 350   # Phạt nặng hơn nếu một lớp có nhiều giảng viên
        
        elif np.sum(individual[:, j]) == 0:
            penalty += 200 
        else: score += 15 # Lớp có giảng viên được phân công

    # Ràng buộc 2: Mỗi giảng viên được phân ít nhất 1 nguyện vọng
    for i in range(individual.shape[0]):
        if np.sum(individual[i, :]) == 0:
            penalty += 350  # Giảng viên không được phân công lớp nào
        else:
            score += 15  # Giảng viên được phân công ít nhất một lớp
            
#     for i in range(individual.shape[0]):  # Duyệt qua từng giảng viên
#         teacher_key = teacher_keys[i]
#         for j in range(individual.shape[1]):  # Duyệt qua từng nguyện vọng (học phần)
#             if individual[i, j] == 1:  # Nếu giảng viên i được phân công nguyện vọng j
#                 course_id = aspirations[aspiration_keys[j]]['course_id']  # Lấy mã học phần của nguyện vọng
#                 teacher_workloads[teacher_key][course_id] += 1   # Tăng tải trọng của giảng viên i cho học phần course_id

#     # Kiểm tra ràng buộc: Mỗi giảng viên không thể hướng dẫn quá 5 nguyện vọng cho mỗi mã học phần
#     for teacher in teachers:
#         for course_id, workload in teacher_workloads[teacher].items():
#             if workload > 5:
#                 penalty += 300
#             else: score +=10

#     # Xử lý thứ tự ưu tiên và cập nhật điểm
#     for j, aspiration_key in enumerate(aspiration_keys):
#         aspiration = aspirations[aspiration_key]
#         preferences = aspiration.get("nguyen_vong", {})
#         priority_scores = {1: 4, 2: 3, 3: 2}

#         assigned_teacher_index = None
#         for priority, score_multiplier in priority_scores.items():
#             preferred_teacher = preferences.get(str(priority))
#             if preferred_teacher in teacher_keys:
#                 teacher_index = teacher_keys.index(preferred_teacher)
#                 if individual[teacher_index, j] == 1:
#                     assigned_teacher_index = teacher_index
#                     score += score_multiplier * 10  # Tăng điểm dựa trên ưu tiên
#                     break

#         # Nếu không có giảng viên nào được phân công theo ưu tiên, chọn ngẫu nhiên giảng viên có tải trọng thấp nhất
#         if assigned_teacher_index is None:
#             min_workload_teacher = min(teacher_workloads, key=teacher_workloads.get)
#             min_teacher_index = teacher_keys.index(min_workload_teacher)
#             individual[min_teacher_index, j] = 1
#             teacher_workloads[min_workload_teacher] += 1
      
    return score - penalty


# Thuật toán Cuckoo Search
def cuckoo_search(teachers, aspirations, pop_size=20, max_iter=20, pa=0.25, beta=1.5):
      num_teachers = len(teachers)
      num_aspirations = len(aspirations)
      teacher_keys = list(teachers.keys())

      # Khởi tạo quần thể
      population = init_population(pop_size, num_teachers, num_aspirations, aspirations, teacher_keys)
      fitness = np.array([evaluate(ind, teachers, aspirations) for ind in population])

      best_individual = population[np.argmax(fitness)]
      best_fitness = np.max(fitness)
      teacher_keys = list(teachers.keys())
      aspiration_keys = list(aspirations.keys())

      # Khởi tạo ma trận teacher_subject_matrix
      num_teachers = len(teacher_keys)
      num_aspirations = len(aspiration_keys)
            
      for iteration in range(max_iter):
            new_population = np.empty_like(population)
            for idx, individual in enumerate(population):
                  step_size = levy_flight(beta)
                  step_direction = np.random.randint(0, 2, (num_teachers, num_aspirations))
                  new_individual = (individual + step_size * step_direction).astype(int)
                  new_individual = np.clip(new_individual, 0, 1)

            # # Đảm bảo ràng buộc sau khi cập nhật new_individual
            # for j in range(num_aspirations):  # Duyệt qua từng lớp
            #       # Lấy danh sách các giảng viên đang được gán cho lớp j
            #       aspiration_key = aspiration_keys[j]
            #       assigned_teachers = np.where(new_individual[:, j] == 1)[0]
                
            #       if len(assigned_teachers) > 1:  # Nhiều hơn 1 giảng viên
            #             valid_teachers = []
            #             for teacher in assigned_teachers:
            #                         priority = aspirations[aspiration_key].get("nguyen_vong", {})
            #                         # Kiểm tra kiểu dữ liệu của teacher và priority["1"]
            #                         if isinstance(teacher, (int, np.int64)):  # Kiểm tra kiểu dữ liệu của teacher
            #                               teacher = str(teacher)  # Chuyển teacher thành chuỗi nếu là số nguyên
            #                         if "1" in priority and teacher in map(str, priority["1"]):  # Áp dụng map để ép kiểu các giảng viên thành chuỗi
            #                               valid_teachers.append((teacher, 1))  # Nguyện vọng 1
            #                         elif "2" in priority and teacher in map(str, priority["2"]):  # Áp dụng map cho nguyện vọng 2
            #                               valid_teachers.append((teacher, 2))  # Nguyện vọng 2
            #                         elif "3" in priority and teacher in map(str, priority["3"]):  # Áp dụng map cho nguyện vọng 3
            #                               valid_teachers.append((teacher, 3))  # Nguyện vọng 3

            #             if valid_teachers:
            #                   # Chọn giảng viên ưu tiên theo nguyện vọng và thời gian giảng dạy
            #                   chosen_teacher = min(valid_teachers, key=lambda t: (t[1], teachers[teacher_keys[int(t[0])]]["time_gl"]))
            #             else:
            #                   # Nếu không có giảng viên hợp lệ, chọn ngẫu nhiên 1 giảng viên ban đầu
            #                   chosen_teacher = np.random.choice(assigned_teachers)

            #             new_individual[chosen_teacher, j] = 1

            new_population[idx] = new_individual

            # Tính toán fitness cho quần thể mới
            new_fitness = np.array([evaluate(ind, teachers, aspirations) for ind in new_population])

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
                  population[idx] = np.random.randint(0, 2, (num_teachers, num_aspirations))
                  fitness[idx] = evaluate(population[idx], teachers, aspirations)
            
            new_fitness = np.array([evaluate(ind, teachers, aspirations) for ind in population])
            better_idx = new_fitness > fitness
            population[better_idx] = new_population[better_idx]
            fitness[better_idx] = new_fitness[better_idx]
                        # Cập nhật cá thể tốt nhất
            if np.max(fitness) > best_fitness:
                  best_individual = population[np.argmax(fitness)]
                  best_fitness = np.max(fitness)

            print(f"Iteration {iteration + 1}/{max_iter}: Best Fitness = {best_fitness}")
            

      return best_individual, best_fitness

if __name__ == "__main__":
      # Lấy dữ liệu từ file Excel
      teachers = getdata1.get_list_teacher('NCM1.xlsx')
      aspirations = getdata1.get_list_nguyen_vong('NCM1.xlsx')
      total_time_gh = sum(teacher["time_gh"] for teacher in teachers.values())
      total_time_gio = sum(aspiration["gio"] for aspiration in aspirations.values())


      # In ra kết quả
      print("Tổng time_gh của giáo viên:", total_time_gh)
      print("Tổng total_time_gh của đồ án:", total_time_gio)
      with open('aspirations_try_last.json', 'w', encoding='utf-8') as aspirations_file:
            json.dump(aspirations, aspirations_file, ensure_ascii=False, indent=4)

      with open('teachers_try_last.json', 'w', encoding='utf-8') as teachers123_file:
            json.dump(teachers, teachers123_file, ensure_ascii=False, indent=4)

      # Chạy thuật toán Cuckoo Search
      best_solution, best_score = cuckoo_search(teachers, aspirations)

      print("Best Score:", best_score)

      # Danh sách khóa
      teacher_keys = list(teachers.keys())
      aspiration_keys = list(aspirations.keys())

      # In thông tin phân công lớp cho giảng viên
      teacher_assignments = {}
      aspirations_no_teacher = []  # Danh sách lớp không có giảng viên
      unassigned_teachers = []  # Danh sách giáo viên không được phân công
      teacher_workload_ratios = {}  # Tỉ lệ giờ được phân trên giờ thực tế

      # Phân công lớp cho giảng viên
      for j, aspiration_key in enumerate(aspiration_keys):
            assigned = False
            for i, teacher_key in enumerate(teacher_keys):
                  if best_solution[i, j] == 1:
                        if teacher_key not in teacher_assignments:
                              teacher_assignments[teacher_key] = []
                        teacher_assignments[teacher_key].append({
                              "aspiration_key": aspiration_key,
                        })
                        assigned = True
                        break
            if not assigned:
                  aspirations_no_teacher.append({
                        "aspiration_key": aspiration_key,
                  })

      # Kiểm tra giáo viên không được phân công và tính tỉ lệ
      for i, teacher_key in enumerate(teacher_keys):
            assigned_aspirations = []
            total_assigned_hours = 0

            for j, aspiration_key in enumerate(aspiration_keys):
                  if best_solution[i, j] == 1:  # Nếu giáo viên này được phân công lớp này
                        assigned_aspirations.append(aspiration_key)
                        total_assigned_hours += aspirations[aspiration_key]["gio"]  # Cộng gio

            # Nếu giáo viên không được phân công lớp nào
            if not assigned_aspirations:
                  unassigned_teachers.append(teacher_key)
            else:
                  # Lấy giờ thực tế tối đa từ dữ liệu giáo viên
                  actual_hours = teachers[teacher_key]["time_gh"]
                  workload_ratio = total_assigned_hours / actual_hours if actual_hours > 0 else 0

                  teacher_workload_ratios[teacher_key] = {
                        "assigned_hours": round(total_assigned_hours, 2),  # Tổng số giờ dạy
                        "time_gh": actual_hours,  # Giờ tối đa
                        "workload_ratio": round(workload_ratio, 2),  # Tỉ lệ giờ dạy
                        "assigned_aspirations": assigned_aspirations  # Danh sách các lớp được phân
                  }

      # Kết quả
      with open('unassigned_teachers.json', 'w', encoding='utf-8') as unassigned_teachers_file:
            json.dump(unassigned_teachers, unassigned_teachers_file, ensure_ascii=False, indent=4)

      with open('aspirations_no_teacher.json', 'w', encoding='utf-8') as aspirations_no_teacher_file:
            json.dump(aspirations_no_teacher, aspirations_no_teacher_file, ensure_ascii=False, indent=4)

      with open('teacher_assignments.json', 'w', encoding='utf-8') as teacher_assignments_file:
            json.dump(teacher_assignments, teacher_assignments_file, ensure_ascii=False, indent=4)

      with open('teacher_workload_ratios.json', 'w', encoding='utf-8') as teacher_workload_ratios_file:
            json.dump(teacher_workload_ratios, teacher_workload_ratios_file, ensure_ascii=False, indent=4)







