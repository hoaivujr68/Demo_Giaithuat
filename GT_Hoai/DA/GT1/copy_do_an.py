import numpy as np
import random
from math import gamma
import json
import pandas as pd
from pprint import pprint
import sys
sys.path.append(r"D:\Demo_Giaithuat")
from timer import *
import data_kb1

def random_solution(teachers, aspirations):
      solution = {}
      teacher_load = {i: 0 for i in teachers}  # Đếm tổng giờ làm việc của từng giảng viên
      aspiration_count = {i: {} for i in teachers}  # Đếm nguyện vọng theo mã học phần cho mỗi giảng viên
      aspiration_total = {i: 0 for i in teachers}  # Tổng số nguyện vọng của mỗi giảng viên

      for j, aspiration in aspirations.items():
            course_id = aspiration["course_id"]
            assigned = False

            # Cập nhật danh sách giảng viên sắp xếp theo tỷ lệ `teacher_load / time_gh` sau mỗi lần phân công
            sorted_teachers = sorted(
                  teachers.keys(),
                  key=lambda x: teacher_load[x] / teachers[x]["time_gh"] if teachers[x]["time_gh"] > 0 else float('inf')
            )

            # Thử gán giảng viên từ danh sách nguyện vọng, ưu tiên giảng viên có tỷ lệ `teacher_load / time_gh` thấp
            for preferred_teacher in sorted_teachers:
                  if preferred_teacher not in aspiration["nguyen_vong"].values():
                        continue  # Bỏ qua nếu giảng viên không nằm trong nguyện vọng

                  # Kiểm tra nếu giảng viên thỏa mãn tất cả các ràng buộc
                  if (
                        teacher_load[preferred_teacher] + aspiration["gio"] <= teachers[preferred_teacher]["time_gh"]
                        and aspiration_total[preferred_teacher] < 30
                        and aspiration_count[preferred_teacher].get(course_id, 0) < 5
                  ):
                        # Gán giảng viên nếu thỏa mãn ràng buộc
                        solution[j] = preferred_teacher
                        teacher_load[preferred_teacher] += aspiration["gio"]
                        aspiration_total[preferred_teacher] += 1

                        # Cập nhật số lượng nguyện vọng theo mã học phần
                        if course_id not in aspiration_count[preferred_teacher]:
                              aspiration_count[preferred_teacher][course_id] = 0
                        aspiration_count[preferred_teacher][course_id] += 1
                        assigned = True
                        break

            # Nếu không thể gán theo nguyện vọng, chọn giảng viên khả dụng từ `sorted_teachers`
            if not assigned:
                  available_teachers = [
                        i for i in sorted_teachers
                        if (
                              teacher_load[i] + aspiration["gio"] <= teachers[i]["time_gh"]
                              and aspiration_total[i] < 30
                              and aspiration_count[i].get(course_id, 0) < 5
                        )
                  ]
                  if available_teachers:
                        teacher = available_teachers[0]  # Chọn giảng viên đầu tiên trong danh sách đã sắp xếp
                        solution[j] = teacher
                        teacher_load[teacher] += aspiration["gio"]
                        aspiration_total[teacher] += 1
                        
                        # Cập nhật nguyện vọng theo mã học phần
                        if course_id not in aspiration_count[teacher]:
                              aspiration_count[teacher][course_id] = 0
                        aspiration_count[teacher][course_id] += 1
                  else:
                        # Nếu không có giảng viên nào thỏa mãn, chọn ngẫu nhiên mà không kiểm tra
                        teacher = random.choice(list(teachers.keys()))
                        solution[j] = teacher

      # Đảm bảo tất cả giảng viên đều có ít nhất một nguyện vọng
      unassigned_teachers = [t for t in teachers if t not in solution.values()]
      for teacher in unassigned_teachers:
            # Chọn một sinh viên ngẫu nhiên chưa được gán hoặc có thể thêm vào giảng viên
            unassigned_students = [j for j in aspirations if j not in solution]
            if unassigned_students:
                  student = random.choice(unassigned_students)
            else:
                  student = random.choice(list(aspirations.keys()))
            solution[student] = teacher

      return solution



# Hàm mục tiêu
def objective_function(solution, teachers, aspirations):
      total_score = 0
      for j, i in solution.items():
            if i in teachers and "nguyen_vong" in aspirations[j]:
            # Kiểm tra nguyện vọng 1, 2, 3 và tính điểm
                  if i == aspirations[j]["nguyen_vong"]["1"]:
                        total_score += 4  # Nguyện vọng 1
                  elif i == aspirations[j]["nguyen_vong"]["2"]:
                        total_score += 3  # Nguyện vọng 2
                  elif i == aspirations[j]["nguyen_vong"]["3"]:
                        total_score += 2  # Nguyện vọng 3
      return total_score


def constraint(solution, teachers, aspirations):
      # Ràng buộc 1: Tính tổng thời gian hướng dẫn của mỗi giảng viên
      teacher_load = {i: 0 for i in teachers}
      aspiration_count = {i: {} for i in teachers}  # Đếm số nguyện vọng theo mã học phần cho mỗi giảng viên

      for j, i in solution.items():
            teacher_load[i] += aspirations[j]["gio"]

            # Đếm số nguyện vọng theo mã học phần
            course_id = aspirations[j]["course_id"]
            if course_id not in aspiration_count[i]:
                  aspiration_count[i][course_id] = 0
            aspiration_count[i][course_id] += 1

      # Ràng buộc 2: Giờ hướng dẫn của mỗi giảng viên không vượt quá giới hạn
      for i, load in teacher_load.items():
            if load > teachers[i]["time_gh"]:
                  return False

      # Ràng buộc số nguyện vọng theo học phần cho mỗi giảng viên
      for i in aspiration_count:
            for course_id, count in aspiration_count[i].items():
                  if count > 5:
                        return False

      # Ràng buộc 3: Mỗi giảng viên không thể hướng dẫn quá 30 nguyện vọng
      for i in teachers:
            total_aspirations = sum(1 for j in solution if solution[j] == i)
            if total_aspirations > 30:
                  return False

      # Ràng buộc bổ sung: Kiểm tra tất cả giảng viên đều có ít nhất một sinh viên
      assigned_teachers = set(solution.values())
      if len(assigned_teachers) < len(teachers):  # Nếu có giảng viên không được gán
            return False

      # Ràng buộc bổ sung: Đảm bảo tỷ lệ teacher_load / time_gh của giảng viên không chênh lệch quá 20%
      teacher_ratios = {
            i: teacher_load[i] / teachers[i]["time_gh"] for i in teachers if teachers[i]["time_gh"] > 0
      }
      min_ratio = min(teacher_ratios.values())
      max_ratio = max(teacher_ratios.values())

      # Kiểm tra biên độ chênh lệch 20%
      if max_ratio - min_ratio > 0.2:  # Nếu chênh lệch vượt quá 20%
            return False

      return True


# Áp dụng Levy Flight để sinh lời giải mới
def levy_flight(Lambda):
      sigma = (
            gamma(1 + Lambda)
            * np.sin(np.pi * Lambda / 2)
            / (gamma((1 + Lambda) / 2) * Lambda * 2 ** ((Lambda - 1) / 2))
      ) ** (1 / Lambda)
      u = np.random.normal(0, sigma, 1)
      v = np.random.normal(0, 1, 1)
      step = u / abs(v) ** (1 / Lambda)
      return step


# Hàm giải bài toán tối ưu xếp nguyện vọng bằng Cuckoo Search với Levy Flight
def solve(teachers, aspirations, n_nests=25, max_iter=100, Lambda=1.5):
      print("Đang giải bài toán tối ưu xếp nguyện vọng với Levy Flight...", end="")
      start_timer()

      # Khởi tạo tổ chim ban đầu (các giải pháp ngẫu nhiên)
      nests = [random_solution(teachers, aspirations) for _ in range(n_nests)]
      fitness = [objective_function(nest, teachers, aspirations) for nest in nests]

      # Tìm tổ chim tốt nhất
      best_solution = nests[np.argmax(fitness)]
      best_fitness = max(fitness)

      # Bắt đầu vòng lặp tối ưu
      for _ in range(max_iter):
            new_nests = []
            for nest in nests:
                  # Sao chép tổ hiện tại
                  new_solution = nest.copy()

                  step_size = levy_flight(Lambda)  
                  for j in aspirations:
                        # Xác suất thay đổi giảng viên tăng dần theo step_size
                        if random.random() < min(1, abs(step_size)):
                              # Thay đổi giảng viên dựa trên step_size
                              new_teacher = random.choice(list(teachers.keys()))
                              new_solution[j] = new_teacher

                  # Kiểm tra ràng buộc và tính fitness cho tổ mới
                  if constraint(new_solution, teachers, aspirations):
                        new_fitness = objective_function(new_solution, teachers, aspirations)

                        # Cập nhật tổ tốt nhất nếu tìm thấy tổ tốt hơn
                        if new_fitness > best_fitness:
                              best_solution = new_solution
                              best_fitness = new_fitness
                              new_nests.append(new_solution)
                  else:
                        new_nests.append(nest)

            nests = new_nests

      # Sau khi kết thúc quá trình tối ưu, trả về giải pháp tốt nhất
      print("OK. (" + get_timer().__str__() + "s)")
      print("Giá trị hàm mục tiêu: ", best_fitness)

      # Lưu kết quả phân bổ vào teachers_aspirations
      teachers_aspirations = {}
      for j, i in best_solution.items():
            if i not in teachers_aspirations:
                  teachers_aspirations[i] = {}
            teachers_aspirations[i][j] = aspirations[j]["course_id"]

      aspirations_no_teacher = [
            (j, aspirations[j]["course_id"]) for j in aspirations if j not in best_solution
      ]
      teachers_no_aspiration = [i for i in teachers if i not in best_solution.values()]

      return teachers_aspirations, aspirations_no_teacher, teachers_no_aspiration


# Lấy danh sách giảng viên và lưu ra file JSON
teachers = data_kb1.get_list_teacher("SV1.xlsx")
with open("teachers.json", "w", encoding="utf-8") as teachers_file:
    json.dump(teachers, teachers_file, ensure_ascii=False, indent=4)

# Lấy danh sách nguyện vọng và lưu ra file JSON
aspirations = data_kb1.get_list_nguyen_vong("SV1.xlsx")
with open("aspirations.json", "w", encoding="utf-8") as aspirations_file:
    json.dump(aspirations, aspirations_file, ensure_ascii=False, indent=4)

# Gọi hàm solve với Levy Flight
teachers_aspirations, aspirations_no_teacher, teachers_no_aspiration = solve(
    teachers, aspirations
)
print("Tổng thời gian chạy: " + get_total_time().__str__() + "s")

# Lưu kết quả phân bổ ra file JSON
with open("best_solution.json", "w", encoding="utf-8") as solution_file:
    json.dump(teachers_aspirations, solution_file, ensure_ascii=False, indent=4)

# Lưu các nguyện vọng không có giảng viên hướng dẫn ra file JSON
with open(
    "aspirations_no_teacher.json", "w", encoding="utf-8"
) as aspirations_no_teacher_file:
    json.dump(
        aspirations_no_teacher,
        aspirations_no_teacher_file,
        ensure_ascii=False,
        indent=4,
    )

# Lưu danh sách giảng viên không hướng dẫn nguyện vọng ra file JSON
with open(
    "teachers_no_aspiration.json", "w", encoding="utf-8"
) as teachers_no_aspiration_file:
    json.dump(
        teachers_no_aspiration,
        teachers_no_aspiration_file,
        ensure_ascii=False,
        indent=4,
    )

# In thông tin về giảng viên bị quá giờ hướng dẫn (GH) và giảng dạy (GD)
overtime_gh_teacher = []
overtime_gd_teacher = []

# Tính giờ hướng dẫn và giờ giảng dạy thực tế của mỗi giảng viên
for i in teachers:
    # Tổng thời gian hướng dẫn (GH) từ giải pháp phân bổ
    time_gh = sum(aspirations[j]["gio"] for j in teachers_aspirations.get(i, []))

    time_gh_damh = sum(
        aspirations[j]["gio"] if aspirations[j]["section_type"] == "ĐAMH" else 0
        for j in teachers_aspirations.get(i, [])
    )

    time_gh_datn = sum(
        aspirations[j]["gio"] if aspirations[j]["section_type"] == "ĐATN" else 0
        for j in teachers_aspirations.get(i, [])
    )

    time_gh_max = round(teachers[i]["time_gh"], 2)

    # Làm tròn thời gian để dễ hiển thị
    time_gh = round(time_gh, 2)

    # Tính phần trăm thời gian GH và GL so với giới hạn
    pt_time_gh = round((time_gh / time_gh_max) * 100, 2)
    pt_time_gh_datn = round((time_gh_datn / time_gh_max) * 100, 2)
    pt_time_gh_damh = round((time_gh_damh / time_gh_max) * 100, 2)

    print(
        "%s: GHt(DATN): %4s/%4s (%4s%%) || GHt(DAMH): %4s/%4s (%4s%%) || GHt: %4s/%4s (%4s%%)"
        % (
            i,
            time_gh_datn,
            time_gh_max,
            pt_time_gh_datn,
            time_gh_damh,
            time_gh_max,
            pt_time_gh_damh,
            time_gh,
            time_gh_max,
            pt_time_gh,
        )
    )

    # Kiểm tra nếu giảng viên bị quá GH hoặc quá GD
    if time_gh > time_gh_max:
        overtime_gh_teacher.append(i)

# In danh sách giảng viên bị quá GH
print("Số giảng viên bị quá GH: ", len(overtime_gh_teacher))
if len(overtime_gh_teacher) > 0:
    print("Danh sách giảng viên bị quá GH: ")
    pprint(overtime_gh_teacher)

# In thông tin tổng quát
print(
    "Số lượng nguyện vọng không có giảng viên hướng dẫn: ", len(aspirations_no_teacher)
)
print(
    "Số lượng giảng viên không hướng dẫn nguyện vọng nào: ", len(teachers_no_aspiration)
)
