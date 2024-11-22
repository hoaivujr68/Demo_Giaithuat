from niapy.algorithms.basic import CuckooSearch
from niapy.task import Task
from niapy.problems import Problem
import numpy as np
import data_kb1

# Định nghĩa bài toán phân công giảng dạy
class TeachingAssignmentProblem(Problem):
    def __init__(self, teachers, classes):
        self.teachers = teachers
        self.classes = classes
        super().__init__(dimension=len(teachers) * len(classes), lower=0, upper=1, type_var=int)

    def _evaluate(self, solution):
      penalty = 0
      fitness = 0
      assignment = np.array(solution).reshape(len(self.teachers), len(self.classes))

      # Kiểm tra cấu trúc dữ liệu
      print("Classes:", self.classes)
      print("Assignment Shape:", assignment.shape)

      # Tính toán giờ dạy thực tế cho từng giảng viên
      for i, teacher in enumerate(self.teachers):
            total_hours = sum(assignment[i, j] * self.classes[j]["quy_doi_gio"] for j in range(len(self.classes)))
            
            # Phạt: Giảng viên dạy quá giờ quy định
            if total_hours > self.teachers[i]["time_gl"]:
                  penalty += (total_hours - self.teachers[i]["time_gl"]) ** 2

      # Ràng buộc: Một lớp chỉ có một giảng viên
      for j in range(len(self.classes)):
            total_teachers = sum(assignment[i, j] for i in range(len(self.teachers)))
            if total_teachers != 1:
                  penalty += abs(1 - total_teachers) ** 2

      # Ràng buộc: Giảng viên chỉ dạy được các lớp trong chuyên môn
      for i in range(len(self.teachers)):
            for j in range(len(self.classes)):
                  if self.classes[j]["subject"] not in self.teachers[i]["teachable_subjects"]:
                        penalty += assignment[i, j] * 100

      # Hàm mục tiêu: Tối đa hóa sự phân công hợp lý
      fitness = -penalty  # Tối thiểu hóa điểm phạt

      return fitness

# Chuẩn bị dữ liệu
teachers = data_kb1.get_list_teacher("SV1.xlsx")
classes = data_kb1.get_time_table("TKB_600.xlsx")

# Định nghĩa bài toán
problem = TeachingAssignmentProblem(teachers, classes)

# Cấu hình thuật toán Cuckoo Search
task = Task(problem=problem, max_iters=1000)
algo = CuckooSearch(population_size=50, pa=0.25)

# Chạy thuật toán
best = algo.run(task)
assignment_solution = np.array(best[0]).reshape(len(teachers), len(classes))

# Hiển thị kết quả
for i, teacher in enumerate(teachers):
    assigned_classes = [j for j in range(len(classes)) if assignment_solution[i, j] == 1]
    print(f"Teacher {teacher['name']} assigned classes: {assigned_classes}")
