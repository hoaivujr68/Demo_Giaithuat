import math
from pprint import pprint

import pandas as pd
from math import isnan
import sys

sys.path.append('..')
from constant import *

list_teacher = {}
list_nhom_cm = {}

total_time_giang_day = 0
total_time_nguyen_vong = 0
phan_bo_gd = 0.54


def get_list_teacher(sheet):
    df = pd.read_excel(sheet, sheet_name=['Phân bổ GD', 'Nhóm CM', 'Nguyện vọng', 'Thông tin DA'])
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
        time_all = row.iloc[2]
        nhom_cm = row.iloc[8]
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
            'time_gl': round(time_all * phan_bo_gd, 2), # giờ giảng dạy trên lớp
            'time_gh': round(time_all * (1 - phan_bo_gd), 2), # giờ hướng dẫn đồ án
            'teachable_subjects': list_ma_hp
        }
    return list_teacher


def get_list_nguyen_vong(sheet):
    df = pd.read_excel(sheet, sheet_name=['Nguyện vọng', 'Thông tin DA'])
    thong_tin_da = {}
    list_nguyen_vong = {}
    hoc_ky = None
    for index, row in df['Thông tin DA'].iterrows():
        if row.iloc[0] is None or 'courseid' in row.iloc[0]:
            continue
        course_id = row.iloc[0]
        group_name = row.iloc[1]
        section_type = row.iloc[2]
        gio = str(row.iloc[3]) + '/' + str(row.iloc[4] if not isnan(row.iloc[4]) else 0)
        so_tin_chi = int(row.iloc[5])
        gio_ky = {}
        if '/' in gio:
            temp = gio.split('/')
            gio_ky['chinh'] = float(temp[0])
            gio_ky['he'] = float(temp[1])
        else:
            gio_ky['chinh'] = float(gio)
            gio_ky['he'] = float(gio)
        if section_type == 'ĐAMH':
            gio_ky['chinh'] *= so_tin_chi
            gio_ky['he'] *= so_tin_chi
        thong_tin_da[(course_id, group_name)] = (gio_ky, section_type)

    for index, row in df['Nguyện vọng'].iterrows():
        if row.iloc[7] is None or 'Mã HP' in row.iloc[7]:
            continue
        mssv = row.iloc[1]
        name = row.iloc[2]
        email = row.iloc[3]
        birthday = row.iloc[4]
        group_name = row.iloc[5]
        huong_de_tai = row.iloc[6]
        course_id = row.iloc[7]
        hoc_ky_temp = str(row.iloc[8])
        nguyen_vong = {
            '1': row.iloc[16],
            '2': row.iloc[17],
            '3': row.iloc[18],
            'accept': 0 if ('Chờ xác nhận' in row.iloc[15]) else int(row.iloc[15][-1]),
        }
        if not hoc_ky:
            hoc_ky = 'he' if hoc_ky_temp.endswith('3') else 'chinh'
        if thong_tin_da.get((course_id, group_name)) is None:
            continue
        list_nguyen_vong[mssv] = {
            'mssv': mssv,
            'name': name,
            'email': email,
            'birthday': birthday,
            'group_name': group_name,
            'section_type': thong_tin_da[(course_id, group_name)][1],
            'huong_de_tai': huong_de_tai,
            'course_id': course_id,
            'nguyen_vong': nguyen_vong,
            'giang_vien': None if nguyen_vong['accept'] == 0 else nguyen_vong[str(nguyen_vong['accept'])],
            'gio': thong_tin_da[(course_id, group_name)][0][hoc_ky],
        }

    global total_time_nguyen_vong
    total_time_nguyen_vong = sum([list_nguyen_vong[i]['gio'] for i in list_nguyen_vong])

    return list_nguyen_vong


def get_time_table(sheet):
    df = pd.read_excel(sheet, sheet_name=['Sheet1'])
    list_time_table = {}
    for index, row in df['Sheet1'].iterrows():
        if row.iloc[0] is None or 'Kỳ' in str(row.iloc[0]):
            continue
        ma_lop = row.iloc[2]
        # ma_lop_kem = row.iloc[3]
        ma_hp = row.iloc[4]
        ten_hp = row.iloc[5]
        thu = int(row.iloc[10]) if not isnan(float(row.iloc[10])) else None
        bat_dau = int(row.iloc[12]) if not isnan(float(row.iloc[12])) else None
        ket_thuc = int(row.iloc[13]) if not isnan(float(row.iloc[13])) else None
        kip = row.iloc[14] if type(row.iloc[14]) == str else None
        tuan_hoc = row.iloc[15].split(',') if type(row.iloc[15]) == str else []
        tuan_hoc_temp = []
        for i in range(len(tuan_hoc)):
            if '-' in tuan_hoc[i]:
                temp = tuan_hoc[i].split('-')
                tuan_hoc_temp += [i for i in range(int(temp[0]), int(temp[1]) + 1)]
            else:
                tuan_hoc_temp.append(int(tuan_hoc[i]))
        tuan_hoc = tuan_hoc_temp
        sl_max = int(row.iloc[19]) if not isnan(float(row.iloc[19])) else None
        loai_lop = row.iloc[21]
        ma_ql = row.iloc[23]
        ma_lop_kem_ngay = str(ma_lop) + "_" + str(thu)
        if thu is None or bat_dau is None or ket_thuc is None or kip is None or len(tuan_hoc) == 0 or sl_max is None:
            continue
        if bat_dau is None or bat_dau > 12:
            continue
        if kip == 'Chiều':
            bat_dau += 6
            ket_thuc += 6
        period = [i for i in range(bat_dau, ket_thuc + 1)]
        if list_time_table.get(ma_lop_kem_ngay) is None:
            list_time_table[ma_lop_kem_ngay] = {
                "subject": ma_hp,
                "name": ten_hp,
                "ma_lop": ma_lop,
                'day': thu,
                'period': period,
                'week': tuan_hoc,
                'quy_doi_gio': get_kc_kl(len(period), ma_ql, loai_lop, sl_max),
                'sl_max': sl_max,
                'loai_lop': loai_lop,

            }
        elif list_time_table[ma_lop_kem_ngay]['week'] != tuan_hoc:
            list_time_table[ma_lop_kem_ngay]['week'] += tuan_hoc
        else:
            # các ma lớp gãy (ca sáng+chiều) sẽ hợp lại thành 1 lop
            new_period = list_time_table[ma_lop_kem_ngay]['period'] + period
            list_time_table[ma_lop_kem_ngay]['period'] = new_period
            list_time_table[ma_lop_kem_ngay]['quy_doi_gio'] = get_kc_kl(len(new_period), ma_ql, loai_lop, sl_max)
    global total_time_giang_day
    total_time_giang_day = sum([list_time_table[i]['quy_doi_gio'] for i in list_time_table])

    return list_time_table


if __name__ == '__main__':
    pprint(get_list_teacher('SV1.xlsx'))
    # pprint(get_list_nguyen_vong('SV1.xlsx'))
    pprint(get_time_table('TKB_600.xlsx'))
