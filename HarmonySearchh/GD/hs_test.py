import random
import numpy as np
from pyharmonysearch import harmony_search, ObjectiveFunctionInterface
import sys
sys.path.append(r"D:\Demo_Giaithuat")
from multiprocessing import cpu_count
# Khởi tạo dữ liệu (tương tự từ đoạn code của bạn)
import data_kb1
teachers = data_kb1.get_list_teacher('SV1.xlsx')
classes = data_kb1.get_time_table('TKB_600.xlsx')

# Định nghĩa hàm kiểm tra ràng buộc
def is_valid_solution(solution, teachers, classes):
    if isinstance(solution, int):
        solution = [solution]
    # Chuyển đổi giải pháp liên tục thành nhị phân
    print(f"Solution: {solution}")
    print(f"Solution length: {len(solution)}")

    x = {(i, j): 1 if solution[idx] >= 0.5 else 0
         for idx, (i, j) in enumerate((i, j) for i in teachers for j in classes)}
    
    # Kiểm tra các ràng buộc
    for i in teachers:
        # Ràng buộc thời gian giảng dạy
        total_time = sum(x[i, j] * classes[j]["quy_doi_gio"] for j in classes)
        if total_time > teachers[i]["time_gl"]:
            return False

    for j in classes:
        # Mỗi lớp chỉ có một giảng viên
        if sum(x[i, j] for i in teachers) > 1:
            return False

    for i in teachers:
        for j in classes:
            # Giảng viên chỉ dạy môn phù hợp
            if x[i, j] == 1 and classes[j]["subject"] not in teachers[i]["teachable_subjects"]:
                return False

    return True

# Hàm ánh xạ giải pháp liên tục thành nhị phân
def map_solution_to_binary(solution, teachers, classes):
    if isinstance(solution, int):
        solution = [solution]
    x = {(i, j): 1 if solution[idx] >= 0.5 else 0
         for idx, (i, j) in enumerate((i, j) for i in teachers for j in classes)}
    return x

class TeachingAssignmentObjective(ObjectiveFunctionInterface):
    def __init__(self, teachers, classes):
        self.teachers = teachers
        self.classes = classes
        self.num_variables = len(teachers) * len(classes)  # Tổng số biến nhị phân

    def get_value(self, solution):
        """
        Trả về giá trị hàm mục tiêu.
        """
        return self.get_fitness(solution)

    def get_fitness(self, solution):
        """
        Tính giá trị hàm mục tiêu.
        """
        # Kiểm tra tính hợp lệ của giải pháp
        if not is_valid_solution(solution, self.teachers, self.classes):
            return -1e6  # Trả về giá trị âm lớn nếu không hợp lệ
        
        # Tính toán hàm mục tiêu (tổng số lớp được phân công)
        x = map_solution_to_binary(solution, self.teachers, self.classes)
        fitness = sum(x[i, j] for i in self.teachers for j in self.classes)
        return fitness

    def get_index(self, idx):
        """
        Trả về giá trị của biến tại index idx.
        """
        return idx

    def get_upper_bound(self):
        """
        Trả về giá trị lớn nhất của các biến.
        """
        return 1  # Với bài toán nhị phân

    def is_variable(self, idx):
        """
        Kiểm tra một chỉ số có phải là biến hợp lệ hay không.
        """
        return 0 <= idx < self.num_variables

    def is_discrete(self):
        """
        Trả về True nếu bài toán là rời rạc.
        """
        return True

    def get_num_parameters(self):
        """
        Trả về tổng số biến trong bài toán.
        """
        return self.num_variables

    def get_random_seed(self):
        """
        Trả về giá trị random seed nếu cần.
        """
        return 42  # Nếu sử dụng random seed

    def get_max_imp(self):
        """
        Trả về số lần cải thiện tối đa.
        """
        return 1000  # Số lần tối đa (bạn có thể tùy chỉnh)

    def get_hmcr(self):
        """
        Trả về giá trị Harmony Memory Consideration Rate (HMCR).
        """
        return 0.95  # Giá trị mặc định

    def get_par(self):
        """
        Trả về giá trị Pitch Adjusting Rate (PAR).
        """
        return 0.3  # Giá trị mặc định

    def get_hms(self):
        """
        Trả về kích thước của Harmony Memory Size (HMS).
        """
        return 50  # Số giải pháp trong bộ nhớ Harmony

    def get_mpai(self):
        """
        Trả về giá trị Multi-Pitch Adjusting Index (MPAI).
        """
        return 1.0  # Giá trị mặc định

    def get_mpap(self):
        """
        Trả về giá trị Multi-Pitch Adjusting Probability (MPAP).
        """
        return 0.1  # Giá trị mặc định

    def maximize(self):
        """
        Trả về True nếu bài toán là maximize.
        """
        return True  # Bài toán tối đa hóa
    
    def use_random_seed(self):
        """
        Định nghĩa phương thức use_random_seed. Trả về False để không sử dụng random seed cố định.
        """
        return False
          
if __name__ == '__main__':
    # Khởi tạo Harmony Search
    objective_function = TeachingAssignmentObjective(teachers, classes)

    num_processes = 50  # Số lượng giải pháp trong Harmony Memory
    num_iterations = 500  # Số lần lặp
    solution = [random.random() for _ in range(len(teachers) * len(classes))]
    results = harmony_search(objective_function, num_processes, num_iterations, solution)

    # Tìm lời giải
    solution = results.run()

    # Hiển thị kết quả
    x_binary = map_solution_to_binary(solution, teachers, classes)
    print("Kết quả phân công:")
    for i in teachers:
        print(f"Giảng viên {i}:")
        for j in classes:
            if x_binary[i, j] == 1:
                print(f"  - Lớp {j}: {classes[j]['subject']}, Thời gian: {classes[j]['day']} - Tiết {classes[j]['period']}")
    
