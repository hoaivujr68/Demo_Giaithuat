import numpy as np
from niapy.task import Task
from niapy.algorithms.basic import CuckooSearch
from niapy.problems.problem import Problem
import data_kb1
from timer import *
import json

class TeachingAssignmentProblem(Problem):
        def __init__(self, teachers, classes):
            self.teachers = teachers
            self.classes = classes
            self.num_teachers = len(teachers)
            self.num_classes = len(classes)
            super().__init__(dimension=self.num_classes, lower=0, upper=self.num_teachers - 1, dtype=int)

    #   def _evaluate(self, solution):
    #         """
    #         Hàm đánh giá một tổ hợp phân công giảng viên (solution).
    #         :param solution: Mảng 1D với mỗi phần tử là giảng viên được phân cho một lớp.
    #         :return: Giá trị hàm mục tiêu.
    #         """
    #         assignments = {teacher: [] for teacher in self.teachers}  # Danh sách lớp của mỗi giảng viên
    #         class_assigned = {class_id: None for class_id in self.classes}  # Theo dõi lớp đã được phân công chưa
    #         violations = 0

    #         # Gán lớp vào giảng viên
    #         for class_idx, teacher_idx in enumerate(solution):
    #               teacher_id = list(self.teachers.keys())[int(teacher_idx)]
    #               class_id = list(self.classes.keys())[class_idx]

    #               class_assigned[class_id] = teacher_id  # Đánh dấu lớp đã có giảng viên

    #               # Kiểm tra ràng buộc: giảng viên phải dạy được môn học
    #               if self.classes[class_id]["subject"] not in self.teachers[teacher_id]["teachable_subjects"]:
    #                     violations += 1
    #                     continue

    #               # Kiểm tra ràng buộc: giảng viên không dạy nhiều lớp trùng thời điểm
    #               time_conflict = False
    #               for assigned_class in assignments[teacher_id]:
    #                     if (self.classes[class_id]["day"] == self.classes[assigned_class]["day"] and
    #                           set(self.classes[class_id]["period"]).intersection(set(self.classes[assigned_class]["period"])) and
    #                           set(self.classes[class_id]["week"]).intersection(set(self.classes[assigned_class]["week"]))):
    #                           time_conflict = True
    #                           break
    #               if time_conflict:
    #                     violations += 1
    #                     continue

    #               # Thêm lớp vào danh sách giảng viên
    #               assignments[teacher_id].append(class_id)

    #         for teacher_id, assigned_classes in assignments.items():
    #               if len(assigned_classes) == 0:  # Nếu giảng viên không dạy lớp nào
    #                     violations += 8
    #         # Tính tổng giờ giảng của từng giảng viên và kiểm tra giới hạn
    #         for teacher_id, class_list in assignments.items():
    #               total_hours = sum(self.classes[class_id]["quy_doi_gio"] for class_id in class_list)
    #               if total_hours > 2 * self.teachers[teacher_id]["time_gl"]:  # Giới hạn thời gian giảng dạy
    #                     violations += 3

    #         # Tối đa hóa số lớp được dạy, giảm thiểu vi phạm
    #         total_classes_assigned = sum(len(class_list) for class_list in assignments.values())
    #         score = total_classes_assigned - violations * 10  # Mỗi vi phạm bị phạt nặng
    #         # score = violations # Mỗi vi phạm bị phạt nặng

    #         return -score  # NiaPy cần giá trị nhỏ nhất, nên trả về âm của điểm
    
        # def _evaluate(self, solution):
        #     """
        #     Hàm đánh giá một tổ hợp phân công giảng viên (solution).
        #     :param solution: Mảng 1D với mỗi phần tử là giảng viên được phân cho một lớp.
        #     :return: Giá trị hàm mục tiêu (giá trị âm để tối ưu hóa với NiaPy).
        #     """
        #     assignments = {teacher: [] for teacher in self.teachers}  # Danh sách lớp của mỗi giảng viên
        #     violations = 0

        #     # Phân công lớp học cho giảng viên
        #     for class_idx, teacher_idx in enumerate(solution):
        #         teacher_id = list(self.teachers.keys())[int(teacher_idx)]
        #         class_id = list(self.classes.keys())[class_idx]

        #         # Kiểm tra ràng buộc: giảng viên phải dạy được môn học
        #         if self.classes[class_id]["subject"] not in self.teachers[teacher_id]["teachable_subjects"]:
        #             violations += 5  # Hình phạt cao cho vi phạm
        #             continue

        #         # Kiểm tra ràng buộc: giảng viên không dạy nhiều lớp trùng thời điểm
        #         time_conflict = False
        #         for assigned_class in assignments[teacher_id]:
        #             if (self.classes[class_id]["day"] == self.classes[assigned_class]["day"] and
        #                 set(self.classes[class_id]["period"]).intersection(set(self.classes[assigned_class]["period"])) and
        #                 set(self.classes[class_id]["week"]).intersection(set(self.classes[assigned_class]["week"]))):
        #                 time_conflict = True
        #                 break
        #         if time_conflict:
        #             violations += 3  # Hình phạt cho vi phạm thời gian trùng lặp
        #             continue

        #         # Thêm lớp vào danh sách giảng viên
        #         assignments[teacher_id].append(class_id)

        #     # Kiểm tra các ràng buộc bổ sung
        #     for teacher_id, assigned_classes in assignments.items():
        #         # Ràng buộc: Giảng viên phải dạy ít nhất 1 lớp
        #         if len(assigned_classes) == 0:
        #             violations += 8  # Hình phạt nặng nếu giảng viên không dạy lớp nào

        #         # Ràng buộc: Tổng giờ giảng của giảng viên không vượt quá giới hạn
        #         total_hours = sum(self.classes[class_id]["quy_doi_gio"] for class_id in assigned_classes)
        #         max_allowed_hours = 2 * self.teachers[teacher_id]["time_gl"]  # Giới hạn giờ dạy
        #         if total_hours > max_allowed_hours:
        #             violations += int((total_hours - max_allowed_hours) / 5)  # Hình phạt tỷ lệ với mức độ vi phạm

        #     # Cân bằng số lớp giữa các giảng viên
        #     total_classes_assigned = sum(len(class_list) for class_list in assignments.values())
        #     avg_classes = total_classes_assigned / len(assignments)

        #     # Hình phạt cho sự không cân bằng giữa các giảng viên (giảm độ chênh lệch)
        #     imbalance_penalty = sum(abs(len(class_list) - avg_classes) for class_list in assignments.values())
        #     imbalance_penalty /= len(assignments)  # Tính trung bình chênh lệch giữa các giảng viên

        #     # Điểm đánh giá cuối cùng
        #     score = total_classes_assigned - (violations * 10) - imbalance_penalty

        #     return -score  # Trả về âm điểm để tối ưu hóa trong NiaPy

        def _evaluate(self, solution):
            """
            Hàm đánh giá một tổ hợp phân công giảng viên (solution).
            :param solution: Mảng 1D với mỗi phần tử là giảng viên được phân cho một lớp.
            :return: Giá trị hàm mục tiêu (giá trị âm để tối ưu hóa với NiaPy).
            """
            assignments = {teacher: [] for teacher in self.teachers}  # Danh sách lớp của mỗi giảng viên
            violations = 0

            # Phân công lớp học cho giảng viên
            for class_idx, teacher_idx in enumerate(solution):
                teacher_id = list(self.teachers.keys())[int(teacher_idx)]
                class_id = list(self.classes.keys())[class_idx]

                # Kiểm tra ràng buộc: giảng viên phải dạy được môn học
                if self.classes[class_id]["subject"] not in self.teachers[teacher_id]["teachable_subjects"]:
                    violations += 5  # Hình phạt cao cho vi phạm
                    continue

                # Kiểm tra ràng buộc: giảng viên không dạy nhiều lớp trùng thời điểm
                time_conflict = False
                for assigned_class in assignments[teacher_id]:
                    if (self.classes[class_id]["day"] == self.classes[assigned_class]["day"] and
                        set(self.classes[class_id]["period"]).intersection(set(self.classes[assigned_class]["period"])) and
                        set(self.classes[class_id]["week"]).intersection(set(self.classes[assigned_class]["week"]))):
                        time_conflict = True
                        break
                if time_conflict:
                    violations += 3  # Hình phạt cho vi phạm thời gian trùng lặp
                    continue

                # Thêm lớp vào danh sách giảng viên
                assignments[teacher_id].append(class_id)

            # Kiểm tra các ràng buộc bổ sung
            for teacher_id, assigned_classes in assignments.items():
                # Ràng buộc: Giảng viên phải dạy ít nhất 1 lớp
                if len(assigned_classes) == 0:
                    violations += 8  # Hình phạt nặng nếu giảng viên không dạy lớp nào

                # Ràng buộc: Tổng giờ giảng của giảng viên không vượt quá giới hạn
                total_hours = sum(self.classes[class_id]["quy_doi_gio"] for class_id in assigned_classes)
                max_allowed_hours = 1.5 * self.teachers[teacher_id]["time_gl"]  # Giới hạn giờ dạy
                if total_hours > max_allowed_hours:
                    violations += int((total_hours - max_allowed_hours) / 5)  # Hình phạt tỷ lệ với mức độ vi phạm

            # Kiểm tra xem tất cả giảng viên đều được phân công ít nhất một lớp
            unassigned_teachers = [teacher_id for teacher_id, assigned_classes in assignments.items() if len(assigned_classes) == 0]
            if unassigned_teachers:
                violations += len(unassigned_teachers) * 10  # Hình phạt nếu có giảng viên chưa được phân công

            # Cân bằng số lớp giữa các giảng viên
            total_classes_assigned = sum(len(class_list) for class_list in assignments.values())
            avg_classes = total_classes_assigned / len(assignments)

            # Hình phạt cho sự không cân bằng giữa các giảng viên (giảm độ chênh lệch)
            imbalance_penalty = sum(abs(len(class_list) - avg_classes) for class_list in assignments.values())
            imbalance_penalty /= len(assignments)  # Tính trung bình chênh lệch giữa các giảng viên

            # Điểm đánh giá cuối cùng
            score = total_classes_assigned - (violations * 10) - imbalance_penalty

            return -score  # Trả về âm điểm để tối ưu hóa trong NiaPy



def load_data(sv_sheet, tkb_sheet):
    teachers = data_kb1.get_list_teacher(sv_sheet)
    classes = data_kb1.get_time_table(tkb_sheet)
    with open('classes_niapy.json', 'w', encoding='utf-8') as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)

    with open('teachers_niapy.json', 'w', encoding='utf-8') as teachers123_file:
        json.dump(teachers, teachers123_file, ensure_ascii=False, indent=4)
    return teachers, classes

def main():
    print("Đang đọc dữ liệu...", end="")
    start_timer()
    teachers, classes = load_data('SV1.xlsx', 'TKB_600.xlsx')
    print(f"OK. {len(teachers)} giảng viên, {len(classes)} lớp. ({get_timer()}s)")

    print("Khởi tạo bài toán phân công giảng dạy...")
    problem = TeachingAssignmentProblem(teachers, classes)

    print("Chạy thuật toán Cuckoo Search...")
    start_timer()
    task = Task(problem=problem, max_evals=50000)
      # Giới hạn số lần đánh giá hàm mục tiêu
    algo = CuckooSearch(n=300, pa=0.4)  # Sử dụng 25 tổ chim
    best_solution, best_score = algo.run(task)

    print(f"OK. Tốt nhất: {best_score} ({get_timer()}s)")

    # Phân công giảng viên vào các lớp
    teacher_tables = {teacher: [] for teacher in teachers}
    for class_idx, teacher_idx in enumerate(best_solution):
        teacher_id = list(teachers.keys())[int(teacher_idx)]
        class_id = list(classes.keys())[class_idx]
        teacher_tables[teacher_id].append(class_id)

    # Tính toán thông tin bổ sung
    print("\nTính toán thông tin phân công...")
    classes_no_teacher = []
    teacher_no_class = []
    list_over_gl = []

    for class_id in classes:
        if not any(class_id in class_list for class_list in teacher_tables.values()):
            classes_no_teacher.append(class_id)

    for teacher_id in teachers:
        assigned_classes = teacher_tables[teacher_id]
        if not assigned_classes:
            teacher_no_class.append(teacher_id)

        # Tính tổng giờ thực tế
        time_thuc_te = sum([classes[class_id]['quy_doi_gio'] for class_id in assigned_classes])
        time_max = teachers[teacher_id]['time_gl']
        if time_thuc_te > time_max:
            list_over_gl.append((teacher_id, round(time_thuc_te, 2), time_max))

    # Hiển thị kết quả
    print("\nKết quả phân công:")
    for teacher_id, class_list in teacher_tables.items():
        print(f"Giảng viên {teacher_id}: {class_list}")

    print("\nThông tin chi tiết:")
    print('Tổng thời gian chạy: ', get_total_time())
    print('Số giảng viên bị quá GL: ', len(list_over_gl))
    for i in list_over_gl:
        print("Giảng viên %s: %s/%s (%s%%)" % (i[0], i[1], i[2], round(i[1] / i[2] * 100, 2)))

    print('Số giảng viên không bị quá GL: ', len(teachers) - len(list_over_gl))
    print('Số giảng viên không có lớp: ', len(teacher_no_class))
    if len(teacher_no_class) > 0:
        print('Danh sách giảng viên không có lớp: ', teacher_no_class)

    print('Số lớp không có giảng viên: ', len(classes_no_teacher))
    if len(classes_no_teacher) > 0:
        print('Danh sách lớp không có giảng viên: ', classes_no_teacher)


if __name__ == "__main__":
    main()
