import math
from pprint import pprint
import re
from numpy import isnan
import pandas as pd
from math import isnan
import sys

sys.path.append('..')
from constant import *

list_teacher = {}
list_nhom_cm = {}

total_time_giang_day = 0
total_time_nguyen_vong = 0

def get_list_teacher(sheet):
    df = pd.read_excel(sheet, sheet_name=['Nhóm CM', 'Phân bổ GD',])
    list_hp = []
    global list_teacher
    for index, row in df['Nhóm CM'].iterrows():
        if row.iloc[0] is None or 'Mã Học phần' in row.iloc[0]:
            continue
        mahp = row.iloc[0]
        nhom_cm = row.iloc[1]
        if nhom_cm is None or mahp is None:
            continue
        list_nhom_cm[nhom_cm] = [i.strip() for i in mahp.split(',')]
        list_hp.append((nhom_cm, mahp))
    for index, row in df['Phân bổ GD'].iterrows():
        if row.iloc[0] is None or math.isnan(row.iloc[0]):
            continue
        teacher_id = row.iloc[1]
        time_gd = row.iloc[2]
        time_da = row.iloc[3]
        nhom_cm = row.iloc[4]
        list_ma_hp = []
        if type(nhom_cm) != str:
            nhom_cm = []
        else:
            nhom_cm = nhom_cm.split(';')
        for i in nhom_cm:
            for j in list_hp:
                if i == j[0]:
                    for ma_hp in j[1].split(','):
                        list_ma_hp.append(ma_hp.strip())

        global total_time_giang_day
        global total_time_nguyen_vong
        global phan_bo_gd

        if total_time_nguyen_vong != 0 and total_time_giang_day != 0:
            phan_bo_gd = total_time_giang_day / (total_time_nguyen_vong + total_time_giang_day)

        list_teacher[teacher_id] = {
            'time_gl': time_gd, # giờ giảng dạy trên lớp
            'time_gh': time_da, # giờ hướng dẫn đồ án
            'teachable_subjects': list_ma_hp
        }
    return list_teacher


def get_list_nguyen_vong(sheet):
    df = pd.read_excel(sheet, sheet_name=['Nguyện vọng'])
    thong_tin_da = {}
    list_nguyen_vong = {}

    for index, row in df['Nguyện vọng'].iterrows():
        if row.iloc[1] is None:
            continue
        mssv = row.iloc[0]
        name = row.iloc[1]
        group_name = row.iloc[2]
        huong_de_tai = row.iloc[3]
        course_id = row.iloc[4]
        section_type = row.iloc[7]
        nguyen_vong = {
            '1': row.iloc[11],
            '2': row.iloc[12],
            '3': row.iloc[13],
        }
        accept = row.iloc[6]
        teacher_code = row.iloc[14]
        gio = row.iloc[15]

        list_nguyen_vong[mssv] = {
            'mssv': mssv,
            'name': name,
            'group_name': group_name,
            'section_type': section_type,
            'huong_de_tai': huong_de_tai,
            'course_id': course_id,
            'nguyen_vong': nguyen_vong,
            'giang_vien': None if accept == 0 else teacher_code,
            'gio': gio,
        }

    global total_time_nguyen_vong
    total_time_nguyen_vong = sum([list_nguyen_vong[i]['gio'] for i in list_nguyen_vong])

    return list_nguyen_vong

def parse_timetable(timetable):
    # Skip if the timetable is unstructured
    if "liên hệ với giáo viên" in timetable.lower():
        return []

    # Split the timetable by ";"
    sessions = timetable.split(";")
    result = []

    for session in sessions:
        # Initialize fields
        thu, bat_dau, ket_thuc, kip, tuan_hoc = None, None, None, None, []

        # Extract session (Sáng/Chiều)
        if "Chiều" in session:
            kip = "Chiều"
        elif "Sáng" in session:
            kip = "Sáng"

        # Extract day of the week (T2 -> 2, T3 -> 3, ..., CN -> 8)
        thu_match = re.search(r"T[2-7]|CN", session)
        if thu_match:
            thu = 8 if thu_match.group() == "CN" else int(thu_match.group()[1])

        # Extract periods (bat_dau, ket_thuc)
        tiet_match = re.search(r"Tiết (\d+)-(\d+)", session)
        if tiet_match:
            bat_dau, ket_thuc = int(tiet_match.group(1)), int(tiet_match.group(2))

        # Extract weeks (Tuần: ...)
        week_match = re.search(r"Tuần: ([\d,-]+)", session)
        if week_match:
            week_ranges = week_match.group(1).split(',')
            for w in week_ranges:
                if '-' in w:
                    start, end = map(int, w.split('-'))
                    tuan_hoc.extend(range(start, end + 1))
                else:
                    tuan_hoc.append(int(w))

        # Append parsed data to the result list
        result.append({
            "thu": thu,
            "bat_dau": bat_dau,
            "ket_thuc": ket_thuc,
            "kip": kip,
            "tuan_hoc": tuan_hoc
        })

    return result

def get_time_table(sheet):
    import pandas as pd
    from numpy import isnan

    df = pd.read_excel(sheet, sheet_name=['Sheet1'])
    list_time_table = {}

    for index, row in df['Sheet1'].iterrows():
        if row.iloc[0] is None or 'Kỳ' in str(row.iloc[0]):
            continue
        ma_lop = row.iloc[2]
        ma_hp = row.iloc[4]
        ten_hp = row.iloc[5]
        timetable = row.iloc[9]
        ma_ql = row.iloc[16]
        gio_gd = row.iloc[17]

        # Parse timetable into multiple sessions
        sessions = parse_timetable(timetable)

        # Combine all days to create a unique key
        days = "".join([str(session['thu']) for session in sessions if session['thu'] is not None])
        ma_lop_kem_ngay = f"{ma_lop}_{days}"

        # Initialize the structure if this key is not yet in the dictionary
        if ma_lop_kem_ngay not in list_time_table:
            list_time_table[ma_lop_kem_ngay] = {
                "subject": ma_hp,
                "name": ten_hp,
                "ma_lop": ma_lop,
                "day": [],
                "period": [],
                "week": [],
                "quy_doi_gio": gio_gd,
            }

        # Process each session
        for session in sessions:
            thu = session['thu']
            bat_dau = session['bat_dau']
            ket_thuc = session['ket_thuc']
            kip = session['kip']
            tuan_hoc = session['tuan_hoc']

            if thu is None or bat_dau is None or ket_thuc is None or kip is None or len(tuan_hoc) == 0:
                continue

            # Adjust period for afternoon sessions
            if kip == 'Chiều':
                bat_dau += 6
                ket_thuc += 6

            # Create period list
            period = list(range(bat_dau, ket_thuc + 1))

            # Update list_time_table
            existing_entry = list_time_table[ma_lop_kem_ngay]
            if thu not in existing_entry['day']:
                existing_entry['day'].append(thu)
            existing_entry['period'].append(period)
            existing_entry['week'].extend(tuan_hoc)

        # Deduplicate and sort week
        list_time_table[ma_lop_kem_ngay]['week'] = sorted(set(list_time_table[ma_lop_kem_ngay]['week']))

    return list_time_table

if __name__ == '__main__':
    pprint(get_list_teacher('NCM1.xlsx'))
    # pprint(get_list_nguyen_vong('SV1.xlsx'))
    pprint(get_time_table('TKB1.xlsx'))
