import random
import pandas as pd
import sys
sys.path.append(r"D:\Demo_Giaithuat")
import data_kb1

# Hàm tính điểm (objective function)
def objective_function(solution, classes, teachers):
      total_score = 0
      overtime_count = 0
      for i in teachers:
            time_allocated = sum([classes[j]['quy_doi_gio'] for j in classes if solution[i][j] == 1])
            if time_allocated > 2 * teachers[i]['time_gl']:
                  overtime_count += 1
            total_score += time_allocated
      return total_score, overtime_count

# Khởi tạo Harmony Memory
def initialize_harmony_memory(teachers, classes):
      harmony_memory = []
      for _ in range(100):  # Số lượng giải pháp trong Harmony Memory
            solution = {}
            for i in teachers:
                  solution[i] = {j: random.choice([0, 1]) for j in classes}  # Giảng viên có thể dạy hoặc không dạy lớp
            harmony_memory.append(solution)
      return harmony_memory

# Cập nhật Harmony Memory
def update_harmony_memory(harmony_memory, new_solution, objective_values):
      best_solution = min(harmony_memory, key=lambda x: objective_function(x, classes, teachers)[0])
      if objective_function(new_solution, classes, teachers)[0] < objective_function(best_solution, classes, teachers)[0]:
            harmony_memory.append(new_solution)
            if len(harmony_memory) > 100:  # Giới hạn số lượng giải pháp trong Harmony Memory
                  harmony_memory.pop(0)

# Giải thuật Harmony Search
def harmony_search(teachers, classes, max_iterations=100):
      harmony_memory = initialize_harmony_memory(teachers, classes)
      best_solution = None
      best_score = float('inf')
      
      teacher_subjects = {i: teachers[i]['teachable_subjects'] for i in teachers}
      
      for iteration in range(max_iterations):
            new_solution = {}
            for i in teachers:
                  new_solution[i] = {}
                  for j in classes:
                        # Kiểm tra xem giảng viên có thể dạy lớp này không
                        if j in teacher_subjects[i]:  # Giảng viên chỉ dạy lớp nếu lớp này thuộc môn học giảng viên có thể dạy
                              new_solution[i][j] = random.choice([0, 1])  # Giảng viên có thể dạy hoặc không dạy lớp
                        else:
                              new_solution[i][j] = 0 
                  
                  # Cập nhật Harmony Memory với giải pháp mới
            update_harmony_memory(harmony_memory, new_solution, objective_values=None)
            
            # Tính toán điểm của giải pháp hiện tại
            current_score, overtime_count = objective_function(new_solution, classes, teachers)
            
            # Lưu lại giải pháp tốt nhất
            if current_score > best_score:
                  best_solution = new_solution
                  best_score = current_score
                  
            
      classes_no_teacher = []
      teacher_no_class = []
      
      # Hiển thị thông tin về giảng viên và lớp học
      list_over_gl = []
      for i in teachers:
            time_thuc_te = sum([classes[j]['quy_doi_gio'] for j in classes if best_solution[i][j] == 1])
            time_max = teachers[i]['time_gl']
            if time_thuc_te > time_max:
                  list_over_gl.append((i, round(time_thuc_te, 2), time_max))
            if time_thuc_te == 0:
                  teacher_no_class.append(i)
            
      for j in classes:
            assigned = any([best_solution[i][j] == 1 for i in teachers])
            if not assigned:
                  classes_no_teacher.append(j)

      # Số giảng viên bị quá GL: + Danh sách
      print('Số giảng viên bị quá GL: ', len(list_over_gl))
      for i in list_over_gl:
            print(f"Giảng viên {i[0]}: {i[1]}/{i[2]}({round(i[1] / i[2] * 100, 2)}%)")

      # Số giảng viên không bị quá GL: + Danh sách
      print('Số giảng viên không bị quá GL: ', len(teachers) - len(list_over_gl))
      
      # Số giảng viên không có lớp: + Danh sách
      print('Số giảng viên không có lớp: ', len(teacher_no_class))
      if len(teacher_no_class) > 0:
            print('Danh sách giảng viên không có lớp: ', teacher_no_class)
      
      # Số lớp không có giảng viên: + Danh sách
      print('Số lớp không có giảng viên: ', len(classes_no_teacher))
      if len(classes_no_teacher) > 0:
            print('Danh sách lớp không có giảng viên: ', classes_no_teacher)
        
      return best_solution, best_score

teachers = data_kb1.get_list_teacher('SV1.xlsx')
classes = data_kb1.get_time_table('TKB_600.xlsx')

# Chạy giải thuật Harmony Search để phân công giảng dạy
best_solution, best_score = harmony_search(teachers, classes)

