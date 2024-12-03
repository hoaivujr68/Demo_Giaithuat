import json
import random
import numpy as np
from pprint import pprint
import sys

sys.path.append(r"D:\Demo_Giaithuat")
import getdata1
from timer import *

# Cấu hình thuật toán Harmony Search
HMS = 100  # Harmony memory size
HMCR = 0.9  # Harmony memory consideration rate
PAR = 0.3  # Pitch adjustment rate
MAX_ITER = 1000  # Số lần lặp tối đa


def initialize_harmony_memory(teachers, aspirations, memory_size):
    harmony_memory = []
    locked_assignments = {}  # Giữ các phân công cố định từ giang_vien

    # Gán trực tiếp các aspirations có giang_vien
    for aspiration_key, aspiration_data in aspirations.items():
        if aspiration_data["giang_vien"]:
            locked_assignments[aspiration_key] = aspiration_data["giang_vien"]

    for _ in range(memory_size):
        solution = {}
        for aspiration_key, aspiration_data in aspirations.items():
            if aspiration_key in locked_assignments:
                # Khóa cứng phân công nếu đã có giang_vien
                solution[aspiration_key] = locked_assignments[aspiration_key]
            else:
                # Phân công ngẫu nhiên từ danh sách giáo viên khả dụng
                valid_teachers = [
                    teacher_key for teacher_key, teacher_data in teachers.items()
                ]
                if valid_teachers:
                    solution[aspiration_key] = random.choice(valid_teachers)
                else:
                    solution[aspiration_key] = None  # Không thể gán

        harmony_memory.append(solution)
    return harmony_memory


def evaluate_solution(solution, teachers, aspirations):
    total_score = 0
    teacher_workload = {
        teacher_key: 0 for teacher_key in teachers.keys()
    }  # Tổng giờ làm việc
    teacher_assignments = {
        teacher_key: 0 for teacher_key in teachers.keys()
    }  # Số nguyện vọng được phân

    # Duyệt qua các nguyện vọng và tính điểm
    for aspiration_key, teacher_key in solution.items():
        if teacher_key:
            aspiration = aspirations[aspiration_key]
            teacher = teachers[teacher_key]

            # Tăng giờ làm việc và số nguyện vọng được phân công
            teacher_workload[teacher_key] += aspiration["gio"]
            teacher_assignments[teacher_key] += 1

            # Phạt nếu vượt quá giờ
            if teacher_workload[teacher_key] > 1.4 * teacher["time_gh"]:
                total_score -= 10  # Điểm phạt nếu vượt giờ
            else:
                total_score += 1  # Điểm thưởng nếu phân công hợp lệ

    return total_score


# Hàm cập nhật hòa âm
def update_harmony(harmony_memory, teachers, aspirations, new_solution):
    # Xóa các phần tử cũ nếu giải pháp mới tốt hơn
    worst_solution = min(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, aspirations)
    )
    worst_score = evaluate_solution(worst_solution, teachers, aspirations)
    new_score = evaluate_solution(new_solution, teachers, aspirations)

    if new_score > worst_score:
        harmony_memory.remove(worst_solution)
        harmony_memory.append(new_solution)
    return harmony_memory


def harmony_search(
    teachers, aspirations, memory_size=HMS, max_iterations=MAX_ITER, hmcr=HMCR, par=PAR
):
    harmony_memory = initialize_harmony_memory(teachers, aspirations, memory_size)
    teacher_workload = {
        teacher_key: 0 for teacher_key in teachers.keys()
    }  # Theo dõi tổng giờ đã phân công cho mỗi giáo viên
    teacher_assignments = {
        teacher_key: 0 for teacher_key in teachers.keys()
    }  # Theo dõi số nguyện vọng đã phân công

    for _ in range(max_iterations):
        new_solution = {}

        for aspiration_key, aspiration_data in aspirations.items():
            if aspiration_data["giang_vien"]:
                # Gán cứng phân công nếu có giang_vien và tổng giờ không vượt ngưỡng 1.4 * time_gh
                assigned_teacher = aspiration_data["giang_vien"]
                if (
                    teacher_workload[assigned_teacher] + aspiration_data["gio"]
                    < 1.4 * teachers[assigned_teacher]["time_gh"]
                    and teacher_assignments[assigned_teacher] < 30
                ):
                    new_solution[aspiration_key] = assigned_teacher
                    teacher_workload[assigned_teacher] += aspiration_data["gio"]
                    teacher_assignments[assigned_teacher] += 1
                else:
                    new_solution[aspiration_key] = None  # Không thể gán nếu vượt ngưỡng
            else:
                random_solution = random.choice(harmony_memory)
                selected_teacher = random_solution[aspiration_key]
                if (
                    selected_teacher
                    and teacher_workload[selected_teacher] + aspiration_data["gio"]
                    < 1.4 * teachers[selected_teacher]["time_gh"]
                    and teacher_assignments[selected_teacher] < 30
                ):
                    new_solution[aspiration_key] = selected_teacher
                    teacher_workload[selected_teacher] += aspiration_data["gio"]
                    teacher_assignments[selected_teacher] += 1
                else:
                    new_solution[aspiration_key] = None  # Không thể gán nếu vượt ngưỡng

        harmony_memory = update_harmony(
            harmony_memory, teachers, aspirations, new_solution
        )

    best_solution = max(
        harmony_memory, key=lambda sol: evaluate_solution(sol, teachers, aspirations)
    )
    best_score = evaluate_solution(best_solution, teachers, aspirations)

    return best_solution, best_score


if __name__ == "__main__":
    # Lấy dữ liệu từ file Excel
    start_timer()
    teachers = getdata1.get_list_teacher("NCM2.xlsx")
    aspirations = getdata1.get_list_nguyen_vong("NCM2.xlsx")
    best_solution, best_score = harmony_search(teachers, aspirations)
    print("OK. (" + get_timer().__str__() + "s)")
    total_time_gh = sum(teacher["time_gh"] for teacher in teachers.values())
    total_time_gio = sum(aspiration["gio"] for aspiration in aspirations.values())

    # In ra tổng thời gian và thông tin tổng quát
    print("Tổng time_gh của giáo viên:", total_time_gh)
    print("Tổng total_time_gio của đồ án:", total_time_gio)
    print("Tổng số giáo viên:", len(teachers))
    print("Tổng số lớp:", len(aspirations))

    # Ghi dữ liệu vào file JSON
    with open("aspirations_try_last.json", "w", encoding="utf-8") as aspirations_file:
        json.dump(aspirations, aspirations_file, ensure_ascii=False, indent=4)

    with open("teachers_try_last.json", "w", encoding="utf-8") as teachers_file:
        json.dump(teachers, teachers_file, ensure_ascii=False, indent=4)

    # Chạy thuật toán Harmony Search (hoặc thuật toán của bạn)
    print("Best Score:", best_score)

    # Danh sách khóa
    teacher_keys = list(teachers.keys())
    aspiration_keys = list(aspirations.keys())

    # Phân công lớp cho giảng viên
    teacher_assignments = {}
    aspirations_no_teacher = []  # Lớp không được phân công
    teacher_workload_ratios = {}  # Tỉ lệ giờ dạy

    # Phân công ban đầu dựa trên kết quả từ thuật toán
    for aspiration_key in aspiration_keys:
        assigned = False

        # Lấy mã giảng viên từ best_solution
        if aspiration_key in best_solution and best_solution[aspiration_key]:
            teacher_key = best_solution[aspiration_key]

            if teacher_key not in teacher_assignments:
                teacher_assignments[teacher_key] = []

            # Thêm thông tin phân công vào teacher_assignments
            teacher_assignments[teacher_key].append(
                {
                    "aspiration_key": aspiration_key,
                    "student_name": aspirations[aspiration_key]["name"],
                    "topic": aspirations[aspiration_key]["huong_de_tai"],
                    "hours_assigned": aspirations[aspiration_key]["gio"],
                }
            )
            assigned = True

        # Nếu không tìm thấy giảng viên
        if not assigned:
            aspirations_no_teacher.append(
                {
                    "aspiration_key": aspiration_key,
                    "student_name": aspirations[aspiration_key]["name"],
                    "topic": aspirations[aspiration_key]["huong_de_tai"],
                    "required_hours": aspirations[aspiration_key]["gio"],
                }
            )

    # Xử lý các lớp không được phân công
    while aspirations_no_teacher:
        newly_assigned = []  # Danh sách lớp mới được phân công trong vòng lặp này
        for aspiration in aspirations_no_teacher:
            aspiration_key = aspiration["aspiration_key"]
            aspiration_data = aspirations[aspiration_key]

            # Tìm giáo viên phù hợp
            valid_teachers = [
                teacher_key
                for teacher_key, teacher_data in teachers.items()
                if teacher_key not in teacher_assignments
                or len(teacher_assignments[teacher_key])
                < 30  # Điều kiện số nguyện vọng < 30
                and sum(
                    item["hours_assigned"]
                    for item in teacher_assignments.get(teacher_key, [])
                )
                + aspiration_data["gio"]
                <= 1.4 * teacher_data["time_gh"]  # Điều kiện giờ dạy
            ]

            if valid_teachers:
                selected_teacher = random.choice(valid_teachers)
            #     selected_teacher = min(
            #     valid_teachers,
            #     key=lambda teacher_key: (
            #         sum(
            #             item["hours_assigned"]
            #             for item in teacher_assignments.get(teacher_key, [])
            #         )
            #         / teachers[teacher_key]["time_gh"]
            #     )
            # )

                if selected_teacher not in teacher_assignments:
                    teacher_assignments[selected_teacher] = []

                # Phân công
                teacher_assignments[selected_teacher].append(
                    {
                        "aspiration_key": aspiration_key,
                        "student_name": aspiration_data["name"],
                        "topic": aspiration_data["huong_de_tai"],
                        "hours_assigned": aspiration_data["gio"],
                    }
                )

                newly_assigned.append(aspiration)  # Đánh dấu nguyện vọng đã phân công

        # Loại bỏ các nguyện vọng đã được phân công khỏi aspirations_no_teacher
        aspirations_no_teacher = [
            asp for asp in aspirations_no_teacher if asp not in newly_assigned
        ]

    # Kiểm tra kết quả
    if aspirations_no_teacher:
        print("Một số nguyện vọng không thể phân công do không có giáo viên phù hợp:")
        for aspiration in aspirations_no_teacher:
            print(aspiration)
    else:
        print("Tất cả nguyện vọng đã được phân công thành công!")

    # Kiểm tra giáo viên không được phân công và tính tỉ lệ
    unassigned_teachers = []  # Giáo viên không được phân công
    for teacher_key in teacher_keys:
        assigned_aspirations = []
        total_assigned_hours = 0

        # Tìm các lớp đã phân công cho giáo viên này
        if teacher_key in teacher_assignments:
            for assignment in teacher_assignments[teacher_key]:
                total_assigned_hours += assignment["hours_assigned"]
                assigned_aspirations.append(assignment["aspiration_key"])

        # Nếu giáo viên không được phân công lớp nào
        if not assigned_aspirations:
            unassigned_teachers.append(teacher_key)
        else:
            # Tính tỷ lệ giờ làm việc
            actual_hours = teachers[teacher_key]["time_gh"]
            workload_ratio = (
                total_assigned_hours / actual_hours if actual_hours > 0 else 0
            )

            teacher_workload_ratios[teacher_key] = {
                "assigned_hours": round(total_assigned_hours, 2),  # Tổng số giờ dạy
                "time_gh": actual_hours,  # Giờ tối đa
                "workload_ratio": round(workload_ratio, 2),  # Tỉ lệ giờ dạy
                "assigned_aspirations": assigned_aspirations,  # Danh sách các lớp được phân
            }

    # Ghi kết quả vào file JSON
    with open(
        "unassigned_teachers.json", "w", encoding="utf-8"
    ) as unassigned_teachers_file:
        json.dump(
            unassigned_teachers, unassigned_teachers_file, ensure_ascii=False, indent=4
        )

    with open(
        "aspirations_no_teacher.json", "w", encoding="utf-8"
    ) as aspirations_no_teacher_file:
        json.dump(
            aspirations_no_teacher,
            aspirations_no_teacher_file,
            ensure_ascii=False,
            indent=4,
        )

    with open(
        "teacher_assignments.json", "w", encoding="utf-8"
    ) as teacher_assignments_file:
        json.dump(
            teacher_assignments, teacher_assignments_file, ensure_ascii=False, indent=4
        )

    with open(
        "teacher_workload_ratios.json", "w", encoding="utf-8"
    ) as teacher_workload_ratios_file:
        json.dump(
            teacher_workload_ratios,
            teacher_workload_ratios_file,
            ensure_ascii=False,
            indent=4,
        )

    # In thêm thông tin chi tiết
    print("Số lớp không được phân công:", len(aspirations_no_teacher))
    print("Số giáo viên không được phân công:", len(unassigned_teachers))
    
    print(f"{'Giảng viên':<10} {'Assigned Hours':<15} {'Time GH':<10} {'Workload Ratio':<15} {'Total Aspirations':<20}")
    print("-" * 70)

    for teacher_key, data in teacher_workload_ratios.items():
        assigned_hours = data["assigned_hours"]
        time_gh = data["time_gh"]
        workload_ratio = data["workload_ratio"]
        aspirations_count = len(data["assigned_aspirations"])
        
        print(f"{teacher_key:<10} {assigned_hours:<15} {time_gh:<10} {workload_ratio:<15} {aspirations_count:<20}")
