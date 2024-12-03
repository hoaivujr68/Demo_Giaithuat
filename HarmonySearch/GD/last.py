import json
import random
import numpy as np
from pprint import pprint
import sys
import json
sys.path.append(r"D:\Demo_Giaithuat")
import getdata1
from timer import *

HMS = 100  # Harmony memory size
HMCR = 0.9  # Harmony memory consideration rate
PAR = 0.3  # Pitch adjustment rate
MAX_ITER = 1000  # Số lần lặp tối đa

# Hàm khởi tạo bộ nhớ hòa âm
def initialize_harmony_memory(teachers, classes, memory_size):
    harmony_memory = []

    for _ in range(memory_size):
        solution = {}
        teacher_workload = {teacher: 0 for teacher in teachers.keys()}

        for class_key, class_info in classes.items():
            valid_teachers = [
                teacher_key
                for teacher_key, teacher_data in teachers.items()
                if class_info["subject"] in teacher_data["teachable_subjects"]
                and teacher_workload[teacher_key] + class_info["quy_doi_gio"]
                <= 1.7 * teacher_data["time_gl"]
            ]

            if valid_teachers:
                assigned_teacher = random.choice(valid_teachers)
                solution[class_key] = assigned_teacher
                teacher_workload[assigned_teacher] += class_info["quy_doi_gio"]
            else:
                solution[class_key] = None  # Không thể gán nếu không hợp lệ

        harmony_memory.append(solution)
    return harmony_memory

def schedules_overlap(period1, period2):
    """
    Kiểm tra xem hai khoảng thời gian (period) có trùng nhau không.
    """
    # Chuyển các khoảng thời gian thành tập hợp các tiết học
    set1 = set(period1)
    set2 = set(period2)

    # Kiểm tra xem có phần tử nào giao nhau không
    return not set1.isdisjoint(set2)

def evaluate_solution(solution, teachers, classes):
    total_score = 0
    teacher_workload = {teacher: 0 for teacher in teachers.keys()}
    assigned_teachers = set()  # Giữ danh sách các giảng viên đã được phân công

    # Lưu lịch dạy của mỗi giảng viên để kiểm tra trùng lặp
    teacher_schedules = {teacher: [] for teacher in teachers.keys()}

    for class_key, teacher_key in solution.items():
        if teacher_key:
            class_info = classes[class_key]
            teacher_data = teachers[teacher_key]

            # Tăng giờ giảng của giảng viên
            teacher_workload[teacher_key] += class_info["quy_doi_gio"]
            assigned_teachers.add(teacher_key)  # Đánh dấu giảng viên đã được phân công

            # Kiểm tra trùng lặp thời gian
            for idx, day in enumerate(class_info["day"]):
                period = class_info["period"][idx]  # Mảng tiết học tương ứng với ngày

                # Kiểm tra nếu lớp này có tiết học trùng với các lớp khác của giảng viên
                for scheduled_day, scheduled_period in teacher_schedules[teacher_key]:
                    if day == scheduled_day and schedules_overlap(scheduled_period, period):
                        total_score -= 20  # Phạt nếu lịch trùng
                        break

                teacher_schedules[teacher_key].append((day, period))  # Thêm lịch dạy mới

            # Phạt nếu vượt giờ
            if teacher_workload[teacher_key] > 1.7 * teacher_data["time_gl"]:
                total_score -= 10  # Phạt
                
            # elif teacher_workload[teacher_key] < 1 * teacher_data["time_gl"]:
            #     total_score -= 10  # Phạt
            else:
                total_score += 1  # Thưởng nếu phân công hợp lệ

    # Kiểm tra nếu tất cả giảng viên đều được phân công ít nhất một lớp
    unassigned_teachers = set(teachers.keys()) - assigned_teachers
    if unassigned_teachers:
        total_score -= (
            len(unassigned_teachers) * 5
        )  # Phạt mỗi giảng viên không được phân công

    return total_score


# Hàm cập nhật bộ nhớ hòa âm
def update_harmony(harmony_memory, teachers, classes, new_solution):
    worst_solution = min(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, classes)
    )
    worst_score = evaluate_solution(worst_solution, teachers, classes)
    new_score = evaluate_solution(new_solution, teachers, classes)

    if new_score > worst_score:
        harmony_memory.remove(worst_solution)
        harmony_memory.append(new_solution)
    return harmony_memory

def harmony_search(
    teachers, classes, memory_size=HMS, max_iterations=MAX_ITER, hmcr=HMCR, par=PAR
):
    # Sắp xếp giáo viên theo `time_gl` tăng dần (ưu tiên giáo viên có thời gian giảng dạy thấp hơn)
    sorted_teachers = sorted(teachers.items(), key=lambda x: x[1]["time_gl"])

    # Khởi tạo bộ nhớ hòa âm
    harmony_memory = initialize_harmony_memory(teachers, classes, memory_size)

    for _ in range(max_iterations):
        new_solution = {}
        teacher_workload = {teacher: 0 for teacher in teachers.keys()}
        teacher_schedules = {teacher: [] for teacher in teachers.keys()}  # Lưu lịch dạy của giáo viên

        for class_key, class_info in classes.items():
            # Chọn ngẫu nhiên một giải pháp từ bộ nhớ hòa âm
            random_solution = random.choice(harmony_memory)
            selected_teacher = random_solution[class_key]

            if is_valid_assignment(
                selected_teacher, class_info, teachers, teacher_workload, teacher_schedules
            ):
                # Phân công giáo viên nếu hợp lệ
                assign_teacher_to_class(
                    selected_teacher, class_key, class_info, new_solution,
                    teacher_workload, teacher_schedules
                )
            else:
                # Tìm giáo viên hợp lệ từ danh sách sắp xếp
                valid_teachers = find_valid_teachers(
                    class_info, sorted_teachers, teachers, teacher_workload, teacher_schedules
                )

                if valid_teachers:
                    assigned_teacher = valid_teachers[0]
                    assign_teacher_to_class(
                        assigned_teacher, class_key, class_info, new_solution,
                        teacher_workload, teacher_schedules
                    )
                else:
                    # Không thể gán lớp này
                    new_solution[class_key] = None

        # Cập nhật bộ nhớ hòa âm với giải pháp mới
        harmony_memory = update_harmony(harmony_memory, teachers, classes, new_solution)

    # Tìm giải pháp tốt nhất
    best_solution = max(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, classes)
    )
    best_score = evaluate_solution(best_solution, teachers, classes)
    unassigned_classes = [
        class_id
        for class_id in classes
        if class_id not in best_solution or best_solution[class_id] is None
    ]
    teacher_schedules = rebuild_teacher_schedules(best_solution, classes)
    best_solution = reassign_unassigned_classes(unassigned_classes, best_solution, teacher_schedules)
    
    return best_solution, best_score

def rebuild_teacher_schedules(solution, classes):
    """
    Xây dựng lại lịch dạy của giáo viên từ một giải pháp.
    """
    teacher_schedules = {teacher: [] for teacher in solution.values() if teacher}
    for class_id, teacher in solution.items():
        if teacher:
            class_info = classes[class_id]
            for day, period in zip(class_info["day"], class_info["period"]):
                teacher_schedules[teacher].append((day, period))
    return teacher_schedules


# Kiểm tra điều kiện phân công giáo viên
def is_valid_assignment(teacher, class_info, teachers, teacher_workload, teacher_schedules):
    if not teacher:
        return False

    # Điều kiện kiểm tra môn học và giờ quy đổi
    if (
        class_info["subject"] not in teachers[teacher]["teachable_subjects"]
        or teacher_workload[teacher] + class_info["quy_doi_gio"] > 1.7 * teachers[teacher]["time_gl"]
    ):
        return False

    # Kiểm tra trùng lặp lịch học
    for idx, day in enumerate(class_info["day"]):
        period = class_info["period"][idx]
        for scheduled_day, scheduled_period in teacher_schedules[teacher]:
            if day == scheduled_day and schedules_overlap(scheduled_period, period):
                return False

    return True


# Tìm danh sách giáo viên hợp lệ
def find_valid_teachers(class_info, sorted_teachers, teachers, teacher_workload, teacher_schedules):
    valid_teachers = [
        teacher_key
        for teacher_key, teacher_data in sorted_teachers
        if (
            class_info["subject"] in teacher_data["teachable_subjects"]
            and teacher_workload[teacher_key] + class_info["quy_doi_gio"] <= 1.7 * teacher_data["time_gl"]
            and not has_schedule_conflict(class_info, teacher_key, teacher_schedules)
        )
    ]
    return valid_teachers


def has_schedule_conflict(class_info, teacher, teacher_schedules):
    """
    Kiểm tra xem một lớp có bị trùng giờ với lịch dạy của giáo viên không.
    """
    for idx, day in enumerate(class_info["day"]):
        period = class_info["period"][idx]

        # Duyệt qua các ngày và tiết đã được phân cho giáo viên
        for scheduled_day, scheduled_period in teacher_schedules[teacher]:
            if day == scheduled_day and schedules_overlap(scheduled_period, period):
                return True  # Có trùng lịch
    return False  # Không có trùng lịch

# Gán giáo viên cho lớp học và cập nhật dữ liệu
def assign_teacher_to_class(teacher, class_key, class_info, new_solution, teacher_workload, teacher_schedules):
    new_solution[class_key] = teacher
    teacher_workload[teacher] += class_info["quy_doi_gio"]
    for idx, day in enumerate(class_info["day"]):
        period = class_info["period"][idx]
        teacher_schedules[teacher].append((day, period))

def reassign_unassigned_classes(unassigned_classes, solution, teacher_schedules):
    # Tiếp tục phân công cho đến khi không còn lớp chưa được phân công
    while unassigned_classes:
        for unassigned_class in unassigned_classes[:]:
            class_data = classes[unassigned_class]

            # Tìm giáo viên phù hợp dựa trên các điều kiện
            valid_teachers = [
                teacher_key
                for teacher_key, teacher_data in teachers.items()
                if unassigned_class in classes  # Lớp này tồn tại
                and not has_schedule_conflict(class_data, teacher_key, teacher_schedules)
                and (
                    (teacher_key not in solution.values() and class_data["quy_doi_gio"] <= 1.7 * teacher_data["time_gl"])
                    or sum(
                        classes[class_id]["quy_doi_gio"]
                        for class_id, assigned_teacher in solution.items()
                        if assigned_teacher == teacher_key
                    ) + class_data["quy_doi_gio"] <= 1.7 * teacher_data["time_gl"]
                )
            ]

            if valid_teachers:
                # Chọn giáo viên phù hợp nhất dựa trên tỷ lệ công việc thấp nhất
                selected_teacher = min(
                    valid_teachers,
                    key=lambda teacher_key: (
                        sum(
                            classes[class_id]["quy_doi_gio"]
                            for class_id, assigned_teacher in solution.items()
                            if assigned_teacher == teacher_key
                        )
                        / teachers[teacher_key]["time_gl"]
                    )
                )

                # Kiểm tra lại lịch của giáo viên được chọn trước khi phân công lớp
                if not has_schedule_conflict(class_data, selected_teacher, teacher_schedules):
                    # Gán giáo viên cho lớp
                    solution[unassigned_class] = selected_teacher
                    teacher_schedules[selected_teacher].extend(
                        zip(class_data["day"], class_data["period"])
                    )
                    unassigned_classes.remove(unassigned_class)
                    break  # Lặp lại để kiểm tra và phân công cho các lớp còn lại

        # Nếu không có lớp nào có thể phân công, thoát khỏi vòng lặp
        if len(unassigned_classes) == len([unassigned_class for unassigned_class in unassigned_classes if unassigned_class not in solution]):
            break
    return solution

# def reassign_classes_for_unassigned_teachers(solution, teacher_no_class, teachers, classes):
#     # Tạo dictionary lưu tỷ lệ công việc của mỗi giáo viên
#     teacher_workload_ratio = {
#       teacher_id: sum(
#             classes[class_id]["quy_doi_gio"] 
#             for class_id, assigned_teacher in solution.items() 
#             if assigned_teacher == teacher_id
#       ) / teachers[teacher_id]["time_gl"]
#       for teacher_id in teachers
#       }

#     for unassigned_teacher in teacher_no_class[:]:  # Lặp qua bản sao
#     # Tìm các lớp đã được phân mà giáo viên này có thể dạy
#         suitable_classes = [
#             class_id
#             for class_id, assigned_teacher in solution.items()
#             if assigned_teacher is not None
#             and unassigned_teacher in teachers  # Giáo viên này tồn tại
#             and classes[class_id]["subject"] in teachers[unassigned_teacher]["teachable_subjects"]
#             and classes[class_id]["quy_doi_gio"] <= 1.7 * teachers[unassigned_teacher]["time_gl"]
#         ]

#         # Nếu có lớp phù hợp, chọn lớp có giảng viên với tỷ lệ công việc cao nhất
#         if suitable_classes:
#             # Lấy lớp với giáo viên hiện tại có workload ratio cao nhất
#             selected_class = max(
#                 suitable_classes,
#                 key=lambda cls: teacher_workload_ratio[solution[cls]]
#             )
#             # Lấy giáo viên đang được phân lớp đó
#             current_teacher = solution[selected_class]
#             if current_teacher is not None and current_teacher != unassigned_teacher:
#                 # Cập nhật workload ratio của giáo viên cũ
#                 teacher_workload_ratio[current_teacher] -= classes[selected_class]["quy_doi_gio"] / teachers[current_teacher]["time_gl"]
#                 # Xóa lớp khỏi giáo viên cũ trong solution
#                 solution[selected_class] = None 
#             # Cập nhật lại phân công
#             solution[selected_class] = unassigned_teacher

#             # Xóa giáo viên khỏi danh sách không có lớp
#             teacher_no_class.remove(unassigned_teacher)
   
#     return solution


if __name__ == "__main__":
    start_timer()
    teachers = getdata1.get_list_teacher("NCM2.xlsx")
    classes = getdata1.get_time_table("TKB1.xlsx")
    total_time_gh = sum(teacher["time_gl"] for teacher in teachers.values())
    total_time_gio = sum(classes["quy_doi_gio"] for classes in classes.values())
    # In ra tổng thời gian và thông tin tổng quát
    print("Tổng time_gh của giáo viên:", total_time_gh)
    print("Tổng total_time_gio của class:", total_time_gio)
    print("Tổng số giáo viên:", len(teachers))
    print("Tổng số lớp:", len(classes))
        # Ghi dữ liệu vào file JSON
    with open("teachers_data.json", "w", encoding="utf-8") as teachers_file:
        json.dump(teachers, teachers_file, ensure_ascii=False, indent=4)

    with open("classes_data.json", "w", encoding="utf-8") as classes_file:
        json.dump(classes, classes_file, ensure_ascii=False, indent=4)

    best_solution, best_score = harmony_search(teachers, classes)
    
    print("OK. (" + get_timer().__str__() + "s)")
    # Kiểm tra nếu lời giải trả về hợp lệ
    if not best_solution:
        print("Không tìm thấy lời giải hợp lệ!")
        exit()
    unassigned_classes = [
        class_id
        for class_id in classes
        if class_id not in best_solution or best_solution[class_id] is None
    ]
    # Tính toán thời gian thực tế của giảng viên
    list_over_gl = []
    for teacher_id, teacher_info in teachers.items():
        time_thuc_te = sum(
            classes[class_id]["quy_doi_gio"]
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        )
        time_max = teacher_info["time_gl"]
        if time_thuc_te > 1.7 * time_max:
            list_over_gl.append((teacher_id, round(time_thuc_te, 2), time_max))

    print("Số giảng viên bị quá GL:", len(list_over_gl))
    for teacher in list_over_gl:
        print(
            f"Giảng viên {teacher[0]}: {teacher[1]}/{teacher[2]} ({round(teacher[1] / teacher[2] * 100, 2)}%)"
        )

    print("Số giảng viên không bị quá GL:", len(teachers) - len(list_over_gl))
    teacher_no_class = [
        teacher_id
        for teacher_id in teachers
        if teacher_id not in best_solution.values()
    ]
    # best_solution = reassign_classes_for_unassigned_teachers(best_solution, teacher_no_class, teachers, classes)
    # teacher_no_class = [
    #     teacher_id
    #     for teacher_id in teachers
    #     if teacher_id not in best_solution.values()
    # ]
    print("Số giảng viên không có lớp:", len(teacher_no_class))
    if teacher_no_class:
        print("Danh sách giảng viên không có lớp:", teacher_no_class)

        # Thông tin về các lớp không được phân công
  
    # best_solution = reassign_unassigned_classes(unassigned_classes, best_solution, teachers, classes)
    # unassigned_classes = [
    #     class_id
    #     for class_id in classes
    #     if class_id not in best_solution or best_solution[class_id] is None
    # ]
    print("Số lớp không được phân công:", len(unassigned_classes))
    if unassigned_classes:
        print("Danh sách lớp không được phân công:", unassigned_classes)

    print("\n--- Thông tin chi tiết giảng dạy của từng giảng viên ---")
# In tiêu đề bảng
    print(f"{'Giảng viên':<15} {'Assigned Hours':<15} {'Time GL':<10} {'Workload Ratio':<15} {'Duplicate Classes':<20}")
    print("-" * 75)
    
    for teacher_id, teacher_info in teachers.items():
        print(f"\nGiảng viên {teacher_id}:")
        
        # Lọc các lớp mà giảng viên được phân công
        teaching_schedule = [
            (class_id, classes[class_id])
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        ]
        
        if teaching_schedule:
            total_quy_doi_gio = 0  # Tổng quy đổi giờ của các lớp được phân công
            num_classes = len(teaching_schedule)  # Số lượng lớp được phân công
            
            for class_id, class_info in teaching_schedule:
                total_quy_doi_gio += class_info.get('quy_doi_gio', 0)  # Cộng dồn quy đổi giờ
                
                # In thông tin về các lớp được phân công
                print(
                    f"  - Lớp: {class_id}, Môn: {class_info['subject']}, "
                    f"Thứ: {class_info['day']}, Tiết: {class_info['period']}, "
                    f"Quy đổi giờ: {class_info['quy_doi_gio']}"
                )
            
            # In thêm tổng quy đổi giờ, thời gian giảng viên và số lớp
            time_gl = teacher_info.get('time_gl', 0)  # Giả sử time_gl là thuộc tính của teacher_info
            if time_gl > 0:
                ratio = total_quy_doi_gio / time_gl  # Tính tỷ lệ
            else:
                ratio = 0  # Tránh chia cho 0 nếu time_gl là 0
            
            print(f"  - Tổng thời gian giảng dạy: {total_quy_doi_gio} giờ")
            print(f"  - Thời gian giảng viên: {time_gl} giờ")
            print(f"  - Số lớp được phân công: {num_classes}")
            print(f"  - Tỷ lệ thời gian được phân công/ thời gian giảng viên: {ratio:.2f}")
            
        else:
            print("  Không có lớp nào được phân công.")     
    
    for teacher_id, teacher_info in teachers.items():
        print(f"\nGiảng viên {teacher_id}:")
        teaching_schedule = [
            (class_id, classes[class_id])
            for class_id, assigned_teacher in best_solution.items()
            if assigned_teacher == teacher_id
        ]

        # Kiểm tra lớp trùng giờ
        schedule_by_day = {}
        for class_id, class_info in teaching_schedule:
            for day, periods in zip(class_info['day'], class_info['period']):
                if day not in schedule_by_day:
                    schedule_by_day[day] = []
                schedule_by_day[day].append((class_id, class_info, periods))  # Lưu cả periods vào dict

    # Kiểm tra xung đột lịch trong từng ngày
        for day, classes_in_day in schedule_by_day.items():
            checked_pairs = set()
            for i, (class_id_1, class_info_1, periods_1) in enumerate(classes_in_day):
                for j in range(i + 1, len(classes_in_day)):  # So sánh chỉ số j > i
                    class_id_2, class_info_2, periods_2 = classes_in_day[j]

                    # Kiểm tra nếu cặp này đã được kiểm tra
                    if (class_id_1, class_id_2) in checked_pairs or (class_id_2, class_id_1) in checked_pairs:
                        continue

                    # Kiểm tra giao nhau giữa các tiết học
                    if set(periods_1) & set(periods_2):  # Có giao nhau
                        print(
                            f"  - *** Cảnh báo: Trùng giờ tại Thứ {day}:" 
                            f"\n    + Lớp: {class_id_1}, Môn: {class_info_1['subject']}, Tiết: {periods_1}"
                            f"\n    + Lớp: {class_id_2}, Môn: {class_info_2['subject']}, Tiết: {periods_2}"
                        )
                    # Đánh dấu cặp lớp đã kiểm tra
                    checked_pairs.add((class_id_1, class_id_2))


    # assignments = {}
    # for class_id, teacher_id in best_solution.items():
    #     class_info = classes[class_id]
    #     teacher_info = teachers[teacher_id]

    #     if teacher_id not in assignments:
    #         assignments[teacher_id] = {
    #             "teacher_id": teacher_id,
    #             "assigned_classes": []
    #         }

    #     assignments[teacher_id]["assigned_classes"].append({
    #         "class_id": class_id,
    #         "subject": class_info["subject"],
    #         "day": class_info["day"],
    #         "period": class_info["period"]
    #     })

    # # Ghi dữ liệu vào file JSON
    # with open("result.json", "w", encoding="utf-8") as file:
    #     json.dump(assignments, file, ensure_ascii=False, indent=4)
