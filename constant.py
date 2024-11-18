# kc hệ số chương trình/hệ đào tạo đối với LT/BT, TH/TN
class CT:
    CT_CHUAN = {
        'NAME': 'CT CHUẨN',
        'KC': {
            'LT': 1.5,
            'BT': 1.5,
            'TH': 1,
            'TN': 1,
            'LT+BT': 3,
        },
    }
    ELITECH = {
        'NAME': 'ELITECH',
        'KC': {
            'LT': 1.8,
            'BT': 1.8,
            'TH': 1.5,
            'TN': 1.5,
            'LT+BT': 3.6,
        },
    }
    SIE = {
        'NAME': 'SIE',
        'KC': {
            'LT': 2,
            'BT': 2,
            'TH': 1.5,
            'TN': 1.5,
            'LT+BT': 4,
        },
    }
    ELITECH_ICT = {
        'NAME': 'ICT',
        'KC': {
            'LT': 2,
            'BT': 2,
            'TH': 1.5,
            'TN': 1.5,
            'LT+BT': 4,
        },
    }


CT_OBJ = {
    'CT CHUẨN': CT.CT_CHUAN,
    'ELITECH': CT.ELITECH,
    'SIE': CT.SIE,
    'ELITECH_ICT': CT.ELITECH_ICT,
}

# hệ số tăng giờ theo quy mô lớp
QUY_MO_LOP = {
    (0, 60): 0,
    (61, 120): 0.2,
    (121, 180): 0.4,
    (181, 240): 0.6,
    (241, 300): 0.8,
    (301, 999): 1,
}


def get_kc_kl(so_tiet, ma_ql, loai_lop, sl_max):
    kc = CT_OBJ[ma_ql]['KC'].get(loai_lop)
    kl = [v for k, v in QUY_MO_LOP.items() if k[0] <= sl_max <= k[1]][0]
    return so_tiet * (kc + kl)
