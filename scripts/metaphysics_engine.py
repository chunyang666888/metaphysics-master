#!/usr/bin/env python3
"""
Metaphysics Master Deterministic Engine v3.0 (Pure Python Stdlib)
8 High-Precision Deterministic Modules (python3 -S zero external dependencies):
  1. almanac / zeri : Solar-longitude solar terms, GanZhi pillars, Moon General, Jianchu, clashes
  2. daliuren       : Da Liu Ren (Heaven/Earth plates, 4 Lessons, 9 Principles w/ Meng-Zhong-Ji & Fuyin Duzhuan,
                      3 Transmissions + Xun Dungan + 6 Relations + 12 Generals + Shensha)
  3. ziwei          : Zi Wei Dou Shu (12 Palaces, 5-Element Bureau, 14 Major Stars + 6 Auspicious + 6 Malefics + Lucun,
                      Full 10-Stem 4 Transformations, 10-Year Daxian, Classical Pattern Detection, Sanfang Sizheng)
  4. meihua         : Meihua Yishu (time/number casting, 64 hexagrams, Ti/Yong, seasonal strength)
  5. liuyao         : Wenwang Najia Liuyao (Jingfang 8 Palaces, Najia, 6 Relations/Spirits, Moving/Changed w/
                      Huitou/Advance/Retreat/Tomb/Extinction, Day Tomb, Sanhe, Fanyin/Fuyin, Fushen)
  6. fengshui       : XuanKong Flying Stars (24 Mountains, 9 Periods, Heshi, Sanban, Fuyin/Fanyin) + Bazhai + Annual Sha
  7. xiaoliuren     : Daoist Xiao Liu Ren (3-palace progression & element interaction)
  8. wuyun          : Huangdi Neijing Five Circuits & Six Qi (五运六气)
"""

import argparse
import datetime
import hashlib
import json
import math

# ============================================================================
# 1. CORE GANZHI & ASTRONOMICAL SOLAR LONGITUDE ENGINE
# ============================================================================

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
BRANCH_ELEMENT = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

ELEMENT_GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
ELEMENT_CONQ = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

BRANCH_CLASH = {
    "子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
BRANCH_COMBINE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
    "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午",
}
BRANCH_PUNISH = {
    "子": "卯", "卯": "子", "寅": "巳", "巳": "申", "申": "寅",
    "丑": "戌", "戌": "未", "未": "丑", "辰": "辰", "午": "午", "酉": "酉", "亥": "亥",
}
# Five-Element 12 Changsheng key stages (长生, 墓, 绝) for Liuyao (水土同宫长生在申)
ELEMENT_CHANGSHENG = {"水": "申", "土": "申", "木": "亥", "火": "寅", "金": "巳"}
ELEMENT_TOMB = {"水": "辰", "土": "辰", "木": "未", "火": "戌", "金": "丑"}
ELEMENT_JUE = {"水": "巳", "土": "巳", "木": "申", "火": "亥", "金": "寅"}

SANHE_GROUPS = [
    ({"申", "子", "辰"}, "水局"),
    ({"亥", "卯", "未"}, "木局"),
    ({"寅", "午", "戌"}, "火局"),
    ({"巳", "酉", "丑"}, "金局"),
]

JIANCHU_12 = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]
JIANCHU_NOTES = {
    "建": "平(宜出行/上任，忌动土)", "除": "吉(宜扫除旧弊、解约、治病)",
    "满": "吉(宜开业、祈福、丰收)", "平": "平(日常平稳事)",
    "定": "吉(宜签约、订盟、稳定事)", "执": "平吉(宜建构、执行)",
    "破": "大凶(月破日，诸事不宜，唯宜拆除)", "危": "凶慎(高危慎行)",
    "成": "大吉(开业、签约、成事最佳)", "收": "平吉(宜收款、入仓)",
    "开": "大吉(宜启动、搬家、开业、出行)", "闭": "凶(闭塞不通，唯宜收尾埋葬)",
}

MOON_GENERALS_BY_BAND = [
    ("戌", "河魁"), ("酉", "从魁"), ("申", "传送"), ("未", "小吉"),
    ("午", "胜光"), ("巳", "太乙"), ("辰", "天罡"), ("卯", "太冲"),
    ("寅", "功曹"), ("丑", "大吉"), ("子", "神后"), ("亥", "登明"),
]


def julian_day(dt: datetime.datetime) -> float:
    utc_dt = dt - datetime.timedelta(hours=8)
    y, m = utc_dt.year, utc_dt.month
    d = utc_dt.day + (utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def solar_longitude(dt: datetime.datetime) -> float:
    jd = julian_day(dt)
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360.0
    m = (357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360.0
    m_rad = math.radians(m)
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2 * m_rad)
        + 0.000289 * math.sin(3 * m_rad)
    )
    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    return (true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))) % 360.0


def get_xunkong(day_stem: str, day_branch: str) -> list:
    s_idx = STEMS.index(day_stem)
    b_idx = BRANCHES.index(day_branch)
    if (s_idx % 2) != (b_idx % 2):
        raise ValueError(f"无效日柱 {day_stem}{day_branch}：天干地支阴阳不配")
    xun_start = (b_idx - s_idx) % 12
    return [BRANCHES[(xun_start - 2) % 12], BRANCHES[(xun_start - 1) % 12]]


def get_xun_dungan(day_stem: str, day_branch: str) -> dict:
    """Return mapping branch -> Dungan stem within the current 10-day Xun (empty string for Xunkong)."""
    s_idx = STEMS.index(day_stem)
    b_idx = BRANCHES.index(day_branch)
    xun_start = (b_idx - s_idx) % 12
    mapping = {b: "" for b in BRANCHES}
    for i in range(10):
        mapping[BRANCHES[(xun_start + i) % 12]] = STEMS[i]
    return mapping


def get_ganzhi_pillars(dt: datetime.datetime) -> dict:
    lon = solar_longitude(dt)
    gz_year = dt.year
    if dt.month <= 2 and 270.0 <= lon < 315.0:
        gz_year -= 1

    y_stem_idx = (gz_year - 4) % 10
    y_branch_idx = (gz_year - 4) % 12
    year_gz = STEMS[y_stem_idx] + BRANCHES[y_branch_idx]

    shifted = (lon - 315.0) % 360.0
    m_offset = int(shifted // 30.0)
    m_branch_idx = (2 + m_offset) % 12
    m_stem_idx = ((y_stem_idx % 5) * 2 + 2 + m_offset) % 10
    month_gz = STEMS[m_stem_idx] + BRANCHES[m_branch_idx]

    eff_date = dt.date()
    if dt.hour >= 23:
        eff_date = eff_date + datetime.timedelta(days=1)
    delta_days = (eff_date - datetime.date(2000, 1, 1)).days
    day_idx60 = (54 + delta_days) % 60
    d_stem_idx = day_idx60 % 10
    d_branch_idx = day_idx60 % 12
    day_gz = STEMS[d_stem_idx] + BRANCHES[d_branch_idx]

    h_branch_idx = ((dt.hour + 1) // 2) % 12
    h_stem_idx = ((d_stem_idx % 5) * 2 + h_branch_idx) % 10
    hour_gz = STEMS[h_stem_idx] + BRANCHES[h_branch_idx]

    xunkong = get_xunkong(STEMS[d_stem_idx], BRANCHES[d_branch_idx])
    jianchu = JIANCHU_12[(d_branch_idx - m_branch_idx) % 12]
    mg_br, mg_name = MOON_GENERALS_BY_BAND[int(lon // 30.0)]

    return {
        "datetime": dt.strftime("%Y-%m-%d %H:%M"),
        "solar_longitude_deg": round(lon, 2),
        "year_gz": year_gz,
        "month_gz": month_gz,
        "day_gz": day_gz,
        "hour_gz": hour_gz,
        "month_branch": BRANCHES[m_branch_idx],
        "day_stem": STEMS[d_stem_idx],
        "day_branch": BRANCHES[d_branch_idx],
        "hour_branch": BRANCHES[h_branch_idx],
        "moon_general": f"{mg_br}({mg_name})",
        "moon_general_branch": mg_br,
        "xunkong": xunkong,
        "jianchu": jianchu,
        "jianchu_note": JIANCHU_NOTES[jianchu],
        "is_month_breaker": BRANCH_CLASH[BRANCHES[m_branch_idx]] == BRANCHES[d_branch_idx],
        "is_year_breaker": BRANCH_CLASH[BRANCHES[y_branch_idx]] == BRANCHES[d_branch_idx],
    }


def seasonal_strength(month_branch: str, element: str) -> str:
    season_elem = BRANCH_ELEMENT[month_branch]
    if element == season_elem:
        return "旺"
    if ELEMENT_GEN[season_elem] == element:
        return "相"
    if ELEMENT_GEN[element] == season_elem:
        return "休"
    if ELEMENT_CONQ[element] == season_elem:
        return "囚"
    return "死"


def element_relation(e_self: str, e_other: str) -> str:
    if e_self == e_other:
        return "体用比和(顺遂)"
    if ELEMENT_GEN[e_other] == e_self:
        return "用生体(大吉进益)"
    if ELEMENT_CONQ[e_self] == e_other:
        return "体克用(吉可成但费力)"
    if ELEMENT_GEN[e_self] == e_other:
        return "体生用(耗泄破费)"
    if ELEMENT_CONQ[e_other] == e_self:
        return "用克体(凶受制阻)"
    return "未知"


def get_six_relation(self_elem: str, target_elem: str) -> str:
    if target_elem == self_elem:
        return "兄弟"
    if ELEMENT_GEN[target_elem] == self_elem:
        return "父母"
    if ELEMENT_GEN[self_elem] == target_elem:
        return "子孙"
    if ELEMENT_CONQ[self_elem] == target_elem:
        return "妻财"
    if ELEMENT_CONQ[target_elem] == self_elem:
        return "官鬼"
    return "未知"


# ============================================================================
# 2. DA LIU REN ENGINE v3.0 (含三传遁干、涉害孟仲季、伏吟杜传)
# ============================================================================

DLR_STEM_LODGE = {
    "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未", "戊": "巳",
    "己": "未", "庚": "申", "辛": "戌", "壬": "亥", "癸": "丑",
}
DLR_STEM_COMBINE = {
    "甲": "己", "己": "甲", "乙": "庚", "庚": "乙", "丙": "辛",
    "辛": "丙", "丁": "壬", "壬": "丁", "戊": "癸", "癸": "戊",
}
DLR_YIMA = {
    "申": "寅", "子": "寅", "辰": "寅", "寅": "申", "午": "申", "戌": "申",
    "巳": "亥", "酉": "亥", "丑": "亥", "亥": "巳", "卯": "巳", "未": "巳",
}
DLR_DAY_LU = {
    "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
    "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子",
}
DLR_GUIREN = {
    "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
    "乙": ("子", "申"), "己": ("子", "申"),
    "丙": ("亥", "酉"), "丁": ("亥", "酉"),
    "壬": ("巳", "卯"), "癸": ("巳", "卯"),
    "辛": ("午", "寅"),
}
DLR_GENERALS = ["贵人", "腾蛇", "朱雀", "六合", "勾陈", "青龙", "天空", "白虎", "太常", "玄武", "太阴", "天后"]
DLR_FORWARD_EARTH = {"亥", "子", "丑", "寅", "卯", "辰"}
MENG_BRANCHES = {"寅", "申", "巳", "亥"}
ZHONG_BRANCHES = {"子", "午", "卯", "酉"}


def dlr_elem(sym: str) -> str:
    return STEM_ELEMENT[sym] if sym in STEM_ELEMENT else BRANCH_ELEMENT[sym]


def dlr_is_yang(sym: str) -> bool:
    return (STEMS.index(sym) % 2 == 0) if sym in STEMS else (BRANCHES.index(sym) % 2 == 0)


def calc_daliuren(time_str: str = None, day_gz: str = None, hour_branch: str = None, moon_general: str = None, period: str = None) -> dict:
    meta_dt = None
    if time_str:
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        p = get_ganzhi_pillars(dt)
        day_gz = day_gz or p["day_gz"]
        hour_branch = hour_branch or p["hour_branch"]
        moon_general = moon_general or p["moon_general_branch"]
        period = period or ("day" if 6 <= dt.hour < 18 else "night")
        meta_dt = p["datetime"]
    else:
        if not (day_gz and hour_branch and moon_general):
            raise ValueError("大六壬需提供 --time 或同时提供 --day-gz, --hour-branch, --moon-general")
        period = period or ("day" if hour_branch in ("卯", "辰", "巳", "午", "未", "申") else "night")

    day_stem, day_branch = day_gz[0], day_gz[1]
    xunkong = get_xunkong(day_stem, day_branch)
    dungan_map = get_xun_dungan(day_stem, day_branch)

    offset = (BRANCHES.index(moon_general) - BRANCHES.index(hour_branch)) % 12
    earth_to_heaven = {b: BRANCHES[(BRANCHES.index(b) + offset) % 12] for b in BRANCHES}
    heaven_to_earth = {h: e for e, h in earth_to_heaven.items()}

    s_lodge = DLR_STEM_LODGE[day_stem]
    k1_top = earth_to_heaven[s_lodge]
    k2_top = earth_to_heaven[k1_top]
    k3_top = earth_to_heaven[day_branch]
    k4_top = earth_to_heaven[k3_top]
    lessons = [
        ("一课(干阳)", day_stem, k1_top),
        ("二课(干阴)", k1_top, k2_top),
        ("三课(支阳)", day_branch, k3_top),
        ("四课(支阴)", k3_top, k4_top),
    ]

    zei, ke, lesson_details = [], [], []
    for lname, bot, top in lessons:
        eb, et = dlr_elem(bot), dlr_elem(top)
        if ELEMENT_CONQ[eb] == et:
            rel = "贼(下克上)"
            zei.append((bot, top))
        elif ELEMENT_CONQ[et] == eb:
            rel = "克(上克下)"
            ke.append((bot, top))
        else:
            rel = "无克"
        lesson_details.append({"lesson": lname, "bottom": bot, "top": top, "relation": rel})

    def dedup_by_top(pairs):
        seen, out = set(), []
        for b, t in pairs:
            if t not in seen:
                seen.add(t)
                out.append((b, t))
        return out

    zei_u, ke_u = dedup_by_top(zei), dedup_by_top(ke)
    day_yang = dlr_is_yang(day_stem)
    principle, needs_review, review_note = "", False, None

    if offset == 0:
        principle = "伏吟"
        if zei_u:
            c1 = zei_u[0][1]
        elif ke_u:
            c1 = ke_u[0][1]
        else:
            c1 = k1_top if day_yang else k3_top
        c2 = BRANCH_PUNISH[c1]
        if c2 == c1:  # 自刑杜传
            c2 = k3_top if c1 == k1_top else k1_top
        c3 = BRANCH_PUNISH[c2]
        if c3 == c2 or c3 == c1:  # 自刑或互刑取冲
            c3 = BRANCH_CLASH[c2]
        chuan = [c1, c2, c3]
    elif offset == 6 and not zei_u and not ke_u:
        principle = "返吟(无克取驿马)"
        chuan = [DLR_YIMA[day_branch], k3_top, k1_top]
    elif zei_u or ke_u:
        cands = zei_u if zei_u else ke_u
        is_zei = bool(zei_u)
        if len(cands) == 1:
            principle = "贼克(重审)" if is_zei else "贼克(元首)"
            c1 = cands[0][1]
        else:
            biyong = [c for c in cands if dlr_is_yang(c[1]) == day_yang]
            if len(biyong) == 1:
                principle = "比用(知一)"
                c1 = biyong[0][1]
            else:
                pool = biyong if len(biyong) > 1 else cands
                # Compute Meng-Zhong-Ji rank (孟=2, 仲=1, 季=0) & Shehai depth
                scored = []
                for b, t in pool:
                    start_e = heaven_to_earth[t]
                    t_elem = dlr_elem(t)
                    depth = 0
                    idx = BRANCHES.index(start_e)
                    for step in range(12):
                        eb = BRANCHES[(idx + step) % 12]
                        if eb == t and step > 0:
                            break
                        if ELEMENT_CONQ[BRANCH_ELEMENT[eb]] == t_elem:
                            depth += 1
                    mzj = 2 if start_e in MENG_BRANCHES else (1 if start_e in ZHONG_BRANCHES else 0)
                    scored.append((depth, mzj, t, start_e))
                scored.sort(key=lambda x: (-x[0], -x[1]))
                if scored[0][0] == scored[1][0]:
                    if scored[0][1] == 2 and scored[1][1] < 2:
                        principle = "涉害(见机·取孟)"
                    elif scored[0][1] == 1 and scored[1][1] < 1:
                        principle = "涉害(察微·取仲)"
                    else:
                        principle = "涉害(缀瑕)"
                        needs_review = True
                        review_note = f"涉害深浅与孟仲季俱同({[(x[2], x[0], x[3]) for x in scored]})，按流派需复核"
                else:
                    principle = "涉害"
                c1 = scored[0][2]
        if offset == 6:
            principle = f"返吟·{principle}"
        c2 = earth_to_heaven[c1]
        c3 = earth_to_heaven[c2]
        chuan = [c1, c2, c3]
    else:
        d_elem = STEM_ELEMENT[day_stem]
        top_set = list(dict.fromkeys([k2_top, k3_top, k4_top]))
        haoshi = [t for t in top_set if ELEMENT_CONQ[BRANCH_ELEMENT[t]] == d_elem]
        tanshe = [t for t in top_set if ELEMENT_CONQ[d_elem] == BRANCH_ELEMENT[t]]
        if haoshi or tanshe:
            pool = haoshi if haoshi else tanshe
            principle = "遥克(蒿矢)" if haoshi else "遥克(弹射)"
            by = [t for t in pool if dlr_is_yang(t) == day_yang]
            c1 = by[0] if by else pool[0]
            chuan = [c1, earth_to_heaven[c1], earth_to_heaven[earth_to_heaven[c1]]]
        elif s_lodge == day_branch:
            principle = "八专"
            c1 = BRANCHES[(BRANCHES.index(k1_top) + 2) % 12] if day_yang else BRANCHES[(BRANCHES.index(k4_top) - 2) % 12]
            chuan = [c1, k1_top, k1_top]
        elif len({(s_lodge, k1_top), (k1_top, k2_top), (day_branch, k3_top), (k3_top, k4_top)}) < 4:
            principle = "别责"
            c1 = earth_to_heaven[DLR_STEM_LODGE[DLR_STEM_COMBINE[day_stem]]] if day_yang else BRANCHES[(BRANCHES.index(day_branch) + 4) % 12]
            chuan = [c1, k1_top, k1_top]
        else:
            principle = "昴星(虎视)" if day_yang else "昴星(冬蛇掩目)"
            chuan = [earth_to_heaven["酉"], k3_top, k1_top] if day_yang else [heaven_to_earth["酉"], k1_top, k3_top]

    gui_heaven = DLR_GUIREN[day_stem][0] if period == "day" else DLR_GUIREN[day_stem][1]
    gui_earth = heaven_to_earth[gui_heaven]
    g_dir = 1 if gui_earth in DLR_FORWARD_EARTH else -1
    gui_h_idx = BRANCHES.index(gui_heaven)
    heaven_to_general = {BRANCHES[(gui_h_idx + g_dir * i) % 12]: g for i, g in enumerate(DLR_GENERALS)}

    d_elem = STEM_ELEMENT[day_stem]
    transmissions = []
    for label, br in zip(["初传", "中传", "末传"], chuan):
        transmissions.append({
            "stage": label,
            "branch": br,
            "dungan": dungan_map[br] or "空",
            "element": BRANCH_ELEMENT[br],
            "six_relation": get_six_relation(d_elem, BRANCH_ELEMENT[br]),
            "general": heaven_to_general[br],
            "is_xunkong": br in xunkong,
        })

    return {
        "system": "大六壬",
        "datetime": meta_dt,
        "day_gz": day_gz,
        "hour_branch": hour_branch,
        "moon_general": moon_general,
        "period": "昼占" if period == "day" else "夜占",
        "principle": principle,
        "needs_review": needs_review,
        "review_note": review_note,
        "xunkong": xunkong,
        "shensha": {"日禄": DLR_DAY_LU[day_stem], "驿马": DLR_YIMA[day_branch], "贵人乘神": f"{gui_heaven}(落{gui_earth})"},
        "four_lessons": lesson_details,
        "three_transmissions": transmissions,
    }


# ============================================================================
# 3. ZI WEI DOU SHU ENGINE v3.0 (14主星 + 六吉六煞禄存 + 完整四化 + 大限 + 格局)
# ============================================================================

ZW_PALACE_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "交友", "官禄", "田宅", "福德", "父母"]
NAYIN_30_ELEMENTS = [
    "金", "火", "木", "土", "金", "火", "水", "土", "金", "木",
    "水", "土", "火", "木", "水", "金", "火", "木", "土", "金",
    "火", "水", "土", "金", "木", "水", "土", "火", "木", "水",
]
ELEM_TO_BUREAU = {"水": ("水二局", 2), "木": ("木三局", 3), "金": ("金四局", 4), "土": ("土五局", 5), "火": ("火六局", 6)}

ZW_SIHUA = {
    "甲": {"化禄": "廉贞", "化权": "破军", "化科": "武曲", "化忌": "太阳"},
    "乙": {"化禄": "天机", "化权": "天梁", "化科": "紫微", "化忌": "太阴"},
    "丙": {"化禄": "天同", "化权": "天机", "化科": "文昌", "化忌": "廉贞"},
    "丁": {"化禄": "太阴", "化权": "天同", "化科": "天机", "化忌": "巨门"},
    "戊": {"化禄": "贪狼", "化权": "太阴", "化科": "右弼", "化忌": "天机"},
    "己": {"化禄": "武曲", "化权": "贪狼", "化科": "天梁", "化忌": "文曲"},
    "庚": {"化禄": "太阳", "化权": "武曲", "化科": "太阴", "化忌": "天同"},
    "辛": {"化禄": "巨门", "化权": "太阳", "化科": "文曲", "化忌": "文昌"},
    "壬": {"化禄": "天梁", "化权": "紫微", "化科": "左辅", "化忌": "武曲"},
    "癸": {"化禄": "破军", "化权": "巨门", "化科": "太阴", "化忌": "贪狼"},
}
ZW_LUCUN = {"甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5, "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 0}
ZW_KUIYUE = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),
    "乙": (0, 8), "己": (0, 8),
    "丙": (11, 9), "丁": (11, 9),
    "壬": (3, 5), "癸": (3, 5),
    "辛": (6, 2),
}
ZW_HUOLING_BASE = {
    "寅": (1, 3), "午": (1, 3), "戌": (1, 3),
    "申": (2, 10), "子": (2, 10), "辰": (2, 10),
    "巳": (3, 10), "酉": (3, 10), "丑": (3, 10),
    "亥": (9, 10), "卯": (9, 10), "未": (9, 10),
}


def get_nayin_bureau(stem_idx: int, branch_idx: int) -> tuple:
    for k in range(60):
        if k % 10 == stem_idx and k % 12 == branch_idx:
            return ELEM_TO_BUREAU[NAYIN_30_ELEMENTS[k // 2]]
    raise ValueError("Invalid stem/branch pair for Nayin")


def calc_ziwei(lunar_month: int, lunar_day: int, year_gz: str, hour_branch: str, gender: str = "m") -> dict:
    if not (1 <= lunar_month <= 12 and 1 <= lunar_day <= 30):
        raise ValueError("农历月须为1-12，农历日须为1-30")
    y_stem, y_branch = year_gz[0], year_gz[1]
    y_stem_idx = STEMS.index(y_stem)
    h_idx = BRANCHES.index(hour_branch)
    is_male = gender.lower() in ("m", "male", "男")

    ming_idx = (2 + (lunar_month - 1) - h_idx) % 12
    shen_idx = (2 + (lunar_month - 1) + h_idx) % 12

    yin_stem_start = (y_stem_idx % 5) * 2 + 2
    palace_stems = {((2 + i) % 12): STEMS[(yin_stem_start + i) % 10] for i in range(12)}
    m_stem_idx = STEMS.index(palace_stems[ming_idx])
    bureau_name, bureau_num = get_nayin_bureau(m_stem_idx, ming_idx)

    rem = lunar_day % bureau_num
    if rem == 0:
        ziwei_idx = (2 + (lunar_day // bureau_num) - 1) % 12
    else:
        add = bureau_num - rem
        q = (lunar_day + add) // bureau_num
        ziwei_idx = (2 + q - 1 - add) % 12 if (add % 2 == 1) else (2 + q - 1 + add) % 12
    tianfu_idx = (4 - ziwei_idx) % 12

    sihua_map = ZW_SIHUA[y_stem]
    star_to_sihua = {star: tag for tag, star in sihua_map.items()}

    def tag_star(s):
        return f"{s}[{star_to_sihua[s]}]" if s in star_to_sihua else s

    major_by_b = {i: [] for i in range(12)}
    aux_by_b = {i: [] for i in range(12)}
    sha_by_b = {i: [] for i in range(12)}

    for sname, off in [("紫微", 0), ("天机", -1), ("太阳", -3), ("武曲", -4), ("天同", -5), ("廉贞", -8)]:
        major_by_b[(ziwei_idx + off) % 12].append(tag_star(sname))
    for sname, off in [("天府", 0), ("太阴", 1), ("贪狼", 2), ("巨门", 3), ("天相", 4), ("天梁", 5), ("七杀", 6), ("破军", 10)]:
        major_by_b[(tianfu_idx + off) % 12].append(tag_star(sname))

    # 6 Auspicious + Lucun
    aux_by_b[(4 + (lunar_month - 1)) % 12].append(tag_star("左辅"))
    aux_by_b[(10 - (lunar_month - 1)) % 12].append(tag_star("右弼"))
    aux_by_b[(10 - h_idx) % 12].append(tag_star("文昌"))
    aux_by_b[(4 + h_idx) % 12].append(tag_star("文曲"))
    kui_idx, yue_idx = ZW_KUIYUE[y_stem]
    aux_by_b[kui_idx].append("天魁")
    aux_by_b[yue_idx].append("天钺")
    lucun_idx = ZW_LUCUN[y_stem]
    aux_by_b[lucun_idx].append("禄存")

    # 6 Malefics
    sha_by_b[(lucun_idx + 1) % 12].append("擎羊")
    sha_by_b[(lucun_idx - 1) % 12].append("陀罗")
    huo_base, ling_base = ZW_HUOLING_BASE[y_branch]
    sha_by_b[(huo_base + h_idx) % 12].append("火星")
    sha_by_b[(ling_base + h_idx) % 12].append("铃星")
    sha_by_b[(11 - h_idx) % 12].append("地空")
    sha_by_b[(11 + h_idx) % 12].append("地劫")

    # Daxian (10-year major luck): Yang Male / Yin Female -> forward (+1), Yin Male / Yang Female -> reverse (-1)
    is_yang_year = (y_stem_idx % 2 == 0)
    dx_dir = 1 if (is_yang_year == is_male) else -1
    daxian_by_b = {}
    for k in range(12):
        b = (ming_idx + dx_dir * k) % 12
        start_age = bureau_num + k * 10
        daxian_by_b[b] = f"{start_age}-{start_age + 9}岁"

    palaces = []
    branch_to_pname = {}
    for step, pname in enumerate(ZW_PALACE_NAMES):
        b_idx = (ming_idx - step) % 12
        branch_to_pname[b_idx] = pname
        palaces.append({
            "palace": pname,
            "is_shengong": b_idx == shen_idx,
            "ganzhi": palace_stems[b_idx] + BRANCHES[b_idx],
            "daxian": daxian_by_b[b_idx],
            "major_stars": major_by_b[b_idx] or ["(空宫借对宫)"],
            "auspicious_stars": aux_by_b[b_idx],
            "malefic_stars": sha_by_b[b_idx],
        })

    # Pattern detection on Ming Sanfang Sizheng
    sanfang_indices = [ming_idx, (ming_idx + 6) % 12, (ming_idx - 4) % 12, (ming_idx + 4) % 12]
    sf_stars_raw = set()
    sf_sihua = set()
    for idx in sanfang_indices:
        for s in major_by_b[idx] + aux_by_b[idx] + sha_by_b[idx]:
            base = s.split("[")[0]
            sf_stars_raw.add(base)
            if "[" in s:
                sf_sihua.add(s.split("[")[1].rstrip("]"))

    patterns = []
    if {"七杀", "破军", "贪狼"}.issubset(sf_stars_raw):
        patterns.append("杀破狼格(开创变动强)")
    if {"天机", "太阴", "天同", "天梁"}.issubset(sf_stars_raw):
        patterns.append("机月同梁格(稳健专业/公职幕僚)")
    if {"化禄", "化权", "化科"}.issubset(sf_sihua):
        patterns.append("科权禄三会/三奇嘉会格")
    if "贪狼" in sf_stars_raw and ("火星" in sf_stars_raw or "铃星" in sf_stars_raw):
        patterns.append("火贪/铃贪格(爆发横发机遇)")
    ming_raw = {s.split("[")[0] for s in major_by_b[ming_idx]}
    if "七杀" in ming_raw and ming_idx in (2, 8, 0, 6):
        patterns.append("七杀朝斗/仰斗格")
    if "破军" in ming_raw and ming_idx in (0, 6):
        patterns.append("英星入庙格")
    if "太阳" in ming_raw and ming_idx == 6:
        patterns.append("日丽中天格")
    if not ming_raw and ming_idx == 7 and "太阳" in {s.split("[")[0] for s in major_by_b[3]} and "太阴" in {s.split("[")[0] for s in major_by_b[11]}:
        patterns.append("明珠出海格")

    return {
        "system": "紫微斗数v3.0(十四主星+六吉六煞禄存+四化+大限)",
        "input_lunar": f"{year_gz}年 农历{lunar_month}月{lunar_day}日 {hour_branch}时 ({'男' if is_male else '女'})",
        "bureau": bureau_name,
        "minggong": f"{palace_stems[ming_idx]}{BRANCHES[ming_idx]}",
        "shengong": f"{branch_to_pname[shen_idx]}({palace_stems[shen_idx]}{BRANCHES[shen_idx]})",
        "daxian_direction": "顺行" if dx_dir == 1 else "逆行",
        "sihua": sihua_map,
        "detected_patterns": patterns,
        "sanfang_sizheng_ming": {
            "命宫": major_by_b[ming_idx] + aux_by_b[ming_idx] + sha_by_b[ming_idx],
            "迁移宫": major_by_b[(ming_idx + 6) % 12] + aux_by_b[(ming_idx + 6) % 12] + sha_by_b[(ming_idx + 6) % 12],
            "财帛宫": major_by_b[(ming_idx - 4) % 12] + aux_by_b[(ming_idx - 4) % 12] + sha_by_b[(ming_idx - 4) % 12],
            "官禄宫": major_by_b[(ming_idx + 4) % 12] + aux_by_b[(ming_idx + 4) % 12] + sha_by_b[(ming_idx + 4) % 12],
        },
        "twelve_palaces": palaces,
    }


# ============================================================================
# 4. WUYUN LIUQI ENGINE (黄帝内经·五运六气)
# ============================================================================

WUYUN_STEM = {
    "甲": ("土运太过", "雨湿流行，肾水受邪"), "己": ("土运不及", "风气乃行，脾土偏弱"),
    "乙": ("金运不及", "炎火乃行，肺金偏弱"), "庚": ("金运太过", "燥气流行，肝木受邪"),
    "丙": ("水运太过", "寒气流行，邪害心火"), "辛": ("水运不及", "湿气乃行，肾水偏弱"),
    "丁": ("木运不及", "燥气乃行，肝木偏弱"), "壬": ("木运太过", "风气流行，脾土受邪"),
    "戊": ("火运太过", "暑热流行，肺金受邪"), "癸": ("火运不及", "寒气乃行，心火偏弱"),
}
LIUQI_ORDER = ["厥阴风木", "少阴君火", "太阴湿土", "少阳相火", "阳明燥金", "太阳寒水"]
SITIAN_BY_BRANCH = {"子": 1, "午": 1, "丑": 2, "未": 2, "寅": 3, "申": 3, "卯": 4, "酉": 4, "辰": 5, "戌": 5, "巳": 0, "亥": 0}


def calc_wuyun(year: int) -> dict:
    ys, yb = STEMS[(year - 4) % 10], BRANCHES[(year - 4) % 12]
    dayun, dayun_note = WUYUN_STEM[ys]
    sitian_idx = SITIAN_BY_BRANCH[yb]
    zaiquan_idx = (sitian_idx + 3) % 6
    step_names = ["初之气(大寒-春分)", "二之气(春分-小满)", "三之气(小满-大暑/司天)", "四之气(大暑-秋分)", "五之气(秋分-小雪)", "终之气(小雪-大寒/在泉)"]
    host_order = ["厥阴风木", "少阴君火", "少阳相火", "太阴湿土", "阳明燥金", "太阳寒水"]
    steps = [{"period": step_names[i], "host_qi": host_order[i], "guest_qi": LIUQI_ORDER[(sitian_idx - 2 + i) % 6]} for i in range(6)]
    return {"system": "黄帝内经·五运六气", "year": year, "year_gz": ys + yb, "central_circuit": dayun, "circuit_note": dayun_note, "sitian_H1": LIUQI_ORDER[sitian_idx], "zaiquan_H2": LIUQI_ORDER[zaiquan_idx], "six_steps": steps}


# ============================================================================
# 5. BAGUA, 64 HEXAGRAMS, MEIHUA & LIUYAO v3.0 (含化墓化绝/日墓/三合/反伏吟)
# ============================================================================

TRIGRAMS_BY_XIANTIAN = {
    1: ("乾", "天", "金", (1, 1, 1)), 2: ("兑", "泽", "金", (1, 1, 0)),
    3: ("离", "火", "火", (1, 0, 1)), 4: ("震", "雷", "木", (1, 0, 0)),
    5: ("巽", "风", "木", (0, 1, 1)), 6: ("坎", "水", "水", (0, 1, 0)),
    7: ("艮", "山", "土", (0, 0, 1)), 8: ("坤", "地", "土", (0, 0, 0)),
}
BITS_TO_TRIGRAM = {v[3]: (k, v[0], v[1], v[2]) for k, v in TRIGRAMS_BY_XIANTIAN.items()}

HEXAGRAM_NAMES = {
    ("乾", "乾"): "乾为天", ("乾", "坤"): "天地否", ("乾", "震"): "天雷无妄", ("乾", "巽"): "天风姤",
    ("乾", "坎"): "天水讼", ("乾", "离"): "天火同人", ("乾", "艮"): "天山遁", ("乾", "兑"): "天泽履",
    ("坤", "乾"): "地天泰", ("坤", "坤"): "坤为地", ("坤", "震"): "地雷复", ("坤", "巽"): "地风升",
    ("坤", "坎"): "地水师", ("坤", "离"): "地火明夷", ("坤", "艮"): "地山谦", ("坤", "兑"): "地泽临",
    ("震", "乾"): "雷天大壮", ("震", "坤"): "雷地豫", ("震", "震"): "震为雷", ("震", "巽"): "雷风恒",
    ("震", "坎"): "雷水解", ("震", "离"): "雷火丰", ("震", "艮"): "雷山小过", ("震", "兑"): "雷泽归妹",
    ("巽", "乾"): "风天小畜", ("巽", "坤"): "风地观", ("巽", "震"): "风雷益", ("巽", "巽"): "巽为风",
    ("巽", "坎"): "风水涣", ("巽", "离"): "风火家人", ("巽", "艮"): "风山渐", ("巽", "兑"): "风泽中孚",
    ("坎", "乾"): "水天需", ("坎", "坤"): "水地比", ("坎", "震"): "水雷屯", ("坎", "巽"): "水风井",
    ("坎", "坎"): "坎为水", ("坎", "离"): "水火既济", ("坎", "艮"): "水山蹇", ("坎", "兑"): "水泽节",
    ("离", "乾"): "火天大有", ("离", "坤"): "火地晋", ("离", "震"): "火雷噬嗑", ("离", "巽"): "火风鼎",
    ("离", "坎"): "火水未济", ("离", "离"): "离为火", ("离", "艮"): "火山旅", ("离", "兑"): "火泽睽",
    ("艮", "乾"): "山天大畜", ("艮", "坤"): "山地剥", ("艮", "震"): "山雷颐", ("艮", "巽"): "山风蛊",
    ("艮", "坎"): "山水蒙", ("艮", "离"): "山火贲", ("艮", "艮"): "艮为山", ("艮", "兑"): "山泽损",
    ("兑", "乾"): "泽天夬", ("兑", "坤"): "泽地萃", ("兑", "震"): "泽雷随", ("兑", "巽"): "泽风大过",
    ("兑", "坎"): "泽水困", ("兑", "离"): "泽火革", ("兑", "艮"): "泽山咸", ("兑", "兑"): "兑为泽",
}


def hex_info_from_bits(bits6: tuple) -> dict:
    lower, upper = BITS_TO_TRIGRAM[bits6[0:3]], BITS_TO_TRIGRAM[bits6[3:6]]
    return {
        "name": HEXAGRAM_NAMES[(upper[1], lower[1])],
        "upper": {"num": upper[0], "name": upper[1], "nature": upper[2], "element": upper[3]},
        "lower": {"num": lower[0], "name": lower[1], "nature": lower[2], "element": lower[3]},
        "bits_bottom_to_top": list(bits6),
    }


def calc_meihua(time_str: str = None, nums: list = None) -> dict:
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M") if time_str else datetime.datetime.now()
    pillars = get_ganzhi_pillars(dt)
    if nums:
        if len(nums) == 2:
            n1, n2 = nums
            upper_num, lower_num, moving = (n1 % 8) or 8, (n2 % 8) or 8, ((n1 + n2) % 6) or 6
            method = f"两数起卦({n1}, {n2})"
        elif len(nums) >= 3:
            n1, n2, n3 = nums[:3]
            upper_num, lower_num, moving = (n1 % 8) or 8, (n2 % 8) or 8, (n3 % 6) or 6
            method = f"三数起卦({n1}, {n2}, {n3})"
        else:
            raise ValueError("数字起卦需提供2或3个正整数")
    else:
        y_num, h_num = BRANCHES.index(pillars["year_gz"][1]) + 1, BRANCHES.index(pillars["hour_gz"][1]) + 1
        s_top = y_num + dt.month + dt.day
        s_all = s_top + h_num
        upper_num, lower_num, moving = (s_top % 8) or 8, (s_all % 8) or 8, (s_all % 6) or 6
        method = f"公历时间起卦(年支{y_num}+月{dt.month}+日{dt.day}+时支{h_num})"

    main_bits = TRIGRAMS_BY_XIANTIAN[lower_num][3] + TRIGRAMS_BY_XIANTIAN[upper_num][3]
    hu_bits = main_bits[1:4] + main_bits[2:5]
    c_list = list(main_bits)
    c_list[moving - 1] = 1 - c_list[moving - 1]
    main_hex, hu_hex, changed_hex = hex_info_from_bits(main_bits), hex_info_from_bits(hu_bits), hex_info_from_bits(tuple(c_list))

    if moving <= 3:
        ti_pos, yong_pos, ti_tri, yong_tri, changed_yong = "上卦", "下卦", main_hex["upper"], main_hex["lower"], changed_hex["lower"]
    else:
        ti_pos, yong_pos, ti_tri, yong_tri, changed_yong = "下卦", "上卦", main_hex["lower"], main_hex["upper"], changed_hex["upper"]

    mb = pillars["month_branch"]
    return {
        "system": "梅花易数", "method": method,
        "pillars": {k: pillars[k] for k in ["datetime", "year_gz", "month_gz", "day_gz", "hour_gz"]},
        "moving_line": moving, "main_hexagram": main_hex["name"], "mutual_hexagram": hu_hex["name"], "changed_hexagram": changed_hex["name"],
        "ti_trigram": {**ti_tri, "position": ti_pos, "seasonal_strength": seasonal_strength(mb, ti_tri["element"])},
        "yong_trigram": {**yong_tri, "position": yong_pos, "seasonal_strength": seasonal_strength(mb, yong_tri["element"])},
        "stage_analysis": {
            "near_main": element_relation(ti_tri["element"], yong_tri["element"]),
            "mid_mutual_upper": f"互上{hu_hex['upper']['name']}({hu_hex['upper']['element']}): {element_relation(ti_tri['element'], hu_hex['upper']['element'])}",
            "mid_mutual_lower": f"互下{hu_hex['lower']['name']}({hu_hex['lower']['element']}): {element_relation(ti_tri['element'], hu_hex['lower']['element'])}",
            "far_changed": f"变用{changed_yong['name']}({changed_yong['element']}): {element_relation(ti_tri['element'], changed_yong['element'])}",
        },
        "guashu_sum": upper_num + lower_num,
    }


NAJIA_BRANCHES = {
    "乾": (["子", "寅", "辰"], ["午", "申", "戌"]), "坎": (["寅", "辰", "午"], ["申", "戌", "子"]),
    "艮": (["辰", "午", "申"], ["戌", "子", "寅"]), "震": (["子", "寅", "辰"], ["午", "申", "戌"]),
    "巽": (["丑", "亥", "酉"], ["未", "巳", "卯"]), "离": (["卯", "丑", "亥"], ["酉", "未", "巳"]),
    "坤": (["未", "巳", "卯"], ["丑", "亥", "酉"]), "兑": (["巳", "卯", "丑"], ["亥", "酉", "未"]),
}
SIX_SPIRITS_ORDER = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]
DAY_STEM_SPIRIT_START = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}
ADVANCE_PAIRS = {("亥", "子"), ("寅", "卯"), ("巳", "午"), ("申", "酉"), ("丑", "辰"), ("辰", "未"), ("未", "戌"), ("戌", "丑")}
RETREAT_PAIRS = {("子", "亥"), ("卯", "寅"), ("午", "巳"), ("酉", "申"), ("辰", "丑"), ("未", "辰"), ("戌", "未"), ("丑", "戌")}
SIX_CLASH_HEX = {"乾为天", "坤为地", "震为雷", "巽为风", "坎为水", "离为火", "艮为山", "兑为泽", "天雷无妄", "雷天大壮"}
SIX_HARMONY_HEX = {"天地否", "地天泰", "雷地豫", "地雷复", "水泽节", "泽水困", "火山旅", "山火贲"}


def build_jingfang_table() -> dict:
    table = {}
    for _, (pname, _, pelem, pbits) in TRIGRAMS_BY_XIANTIAN.items():
        cur = list(pbits + pbits)
        table[tuple(cur)] = (pname, pelem, 6, 3, "本宫")
        for step in range(1, 6):
            cur[step - 1] = 1 - cur[step - 1]
            table[tuple(cur)] = (pname, pelem, step, ((step + 2) % 6) + 1, f"{step}世")
        cur[3] = 1 - cur[3]
        table[tuple(cur)] = (pname, pelem, 4, 1, "游魂")
        cur[0:3] = list(pbits)
        table[tuple(cur)] = (pname, pelem, 3, 6, "归魂")
    return table


JINGFANG_TABLE = build_jingfang_table()


def calc_liuyao(lines: list = None, date_str: str = None, seed_text: str = None, month_branch: str = None, day_gz: str = None) -> dict:
    if day_gz and month_branch:
        d_stem, d_branch = day_gz[0], day_gz[1]
        xk = set(get_xunkong(d_stem, d_branch))
        pillars_out = {"datetime": "手动干支口径", "month_gz": f"{month_branch}月", "day_gz": day_gz, "xunkong": sorted(xk)}
        mb, db = month_branch, d_branch
    else:
        dt = (datetime.datetime.strptime(date_str, "%Y-%m-%d") if len(date_str) == 10 else datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")) if date_str else datetime.datetime.now()
        p = get_ganzhi_pillars(dt)
        d_stem, mb, db, xk = p["day_stem"], p["month_branch"], p["day_branch"], set(p["xunkong"])
        pillars_out = {k: p[k] for k in ["datetime", "year_gz", "month_gz", "day_gz", "xunkong"]}

    if lines is None:
        h = hashlib.sha256(f"{seed_text or 'auto'}|{pillars_out.get('datetime','')}".encode("utf-8")).digest()
        coin_map = [6, 7, 7, 7, 8, 8, 8, 9]
        lines = [coin_map[h[i] % 8] for i in range(6)]
        cast_mode = "确定性自动起卦(基于问题与时间种子)"
    else:
        if len(lines) != 6 or any(v not in (6, 7, 8, 9) for v in lines):
            raise ValueError("六爻数值必须是6个位于{6,7,8,9}的整数(初爻到上爻)")
        cast_mode = "手动六爻输入(初爻至上爻)"

    main_bits = tuple(1 if v in (7, 9) else 0 for v in lines)
    changed_bits = tuple((0 if v == 9 else (1 if v == 6 else (1 if v == 7 else 0))) for v in lines)
    main_hex, changed_hex = hex_info_from_bits(main_bits), hex_info_from_bits(changed_bits)
    palace_name, palace_elem, shi_pos, ying_pos, gen = JINGFANG_TABLE[main_bits]

    main_br = NAJIA_BRANCHES[main_hex["lower"]["name"]][0] + NAJIA_BRANCHES[main_hex["upper"]["name"]][1]
    chg_br = NAJIA_BRANCHES[changed_hex["lower"]["name"]][0] + NAJIA_BRANCHES[changed_hex["upper"]["name"]][1]
    sp_start = DAY_STEM_SPIRIT_START[d_stem]

    yao_rows, present_rels, active_branches = [], set(), set()
    for i in range(6):
        pos, val = i + 1, lines[i]
        is_m, br = val in (6, 9), main_br[i]
        elem = BRANCH_ELEMENT[br]
        rel = get_six_relation(palace_elem, elem)
        present_rels.add(rel)
        if is_m:
            active_branches.add(br)
        tags = []
        if pos == shi_pos:
            tags.append("世")
        if pos == ying_pos:
            tags.append("应")
        if br in xk:
            tags.append("旬空")
        if BRANCH_CLASH[mb] == br:
            tags.append("月破")
        if BRANCH_CLASH[db] == br:
            tags.append("日冲(暗动)" if seasonal_strength(mb, elem) in ("旺", "相") else "日冲(日破)")
        if BRANCH_COMBINE[mb] == br:
            tags.append("月合")
        if BRANCH_COMBINE[db] == br:
            tags.append("日合")
        if ELEMENT_TOMB[elem] == db:
            tags.append("入日墓")

        change_info = None
        if is_m:
            cb = chg_br[i]
            ce = BRANCH_ELEMENT[cb]
            active_branches.add(cb)
            cn = []
            if (br, cb) in ADVANCE_PAIRS:
                cn.append("化进神")
            elif (br, cb) in RETREAT_PAIRS:
                cn.append("化退神")
            if ELEMENT_GEN[ce] == elem:
                cn.append("回头生")
            elif ELEMENT_CONQ[ce] == elem:
                cn.append("回头克")
            elif ELEMENT_GEN[elem] == ce:
                cn.append("化泄")
            elif ELEMENT_CONQ[elem] == ce:
                cn.append("化耗")
            else:
                cn.append("化比和")
            if ELEMENT_TOMB[elem] == cb:
                cn.append("化墓")
            if ELEMENT_JUE[elem] == cb:
                cn.append("化绝")
            if ELEMENT_CHANGSHENG[elem] == cb:
                cn.append("化长生")
            change_info = {"changed_branch": cb, "changed_element": ce, "changed_relation": get_six_relation(palace_elem, ce), "interaction": cn}

        yao_rows.append({
            "position": pos, "raw_value": val, "yin_yang": "阳" if val in (7, 9) else "阴", "moving": is_m,
            "six_spirit": SIX_SPIRITS_ORDER[(sp_start + i) % 6], "six_relation": rel,
            "branch": br, "element": elem, "seasonal_strength": seasonal_strength(mb, elem), "tags": tags, "change": change_info,
        })

    fushen = []
    missing = {"父母", "兄弟", "子孙", "妻财", "官鬼"} - present_rels
    if missing:
        pure_br = NAJIA_BRANCHES[palace_name][0] + NAJIA_BRANCHES[palace_name][1]
        for i in range(6):
            fb = pure_br[i]
            fe = BRANCH_ELEMENT[fb]
            fr = get_six_relation(palace_elem, fe)
            if fr in missing:
                fly = yao_rows[i]
                fle = fly["element"]
                ff = "飞生伏(易出伏)" if ELEMENT_GEN[fle] == fe else ("飞克伏(受压难出)" if ELEMENT_CONQ[fle] == fe else ("伏泄于飞" if ELEMENT_GEN[fe] == fle else ("伏克飞(出暴)" if ELEMENT_CONQ[fe] == fle else "飞伏比和")))
                fushen.append({"position": i + 1, "fushen_relation": fr, "fushen_branch": fb, "fushen_element": fe, "feishen": f"{fly['six_relation']}{fly['branch']}{fly['element']}", "fly_hide_relation": ff})

    special = []
    if main_hex["name"] in SIX_CLASH_HEX:
        special.append("本卦六冲")
    if main_hex["name"] in SIX_HARMONY_HEX:
        special.append("本卦六合")
    has_moving = any(r["moving"] for r in yao_rows)
    if has_moving:
        if changed_hex["name"] in SIX_CLASH_HEX:
            special.append("变卦六冲")
        if changed_hex["name"] in SIX_HARMONY_HEX:
            special.append("变卦六合")
        if all(BRANCH_CLASH[main_br[i]] == chg_br[i] for i in range(6)):
            special.append("卦变反吟")
        if all(main_br[i] == chg_br[i] for i in range(6)):
            special.append("卦变伏吟")

    # Sanhe detection across moving/changed branches + month/day
    sanhe_hits = []
    pool_sanhe = active_branches | {mb, db}
    for grp, label in SANHE_GROUPS:
        if grp.issubset(active_branches):
            sanhe_hits.append(f"卦内动变三合{label}")
        elif len(grp & active_branches) >= 2 and grp.issubset(pool_sanhe):
            sanhe_hits.append(f"动爻会日月三合{label}")

    return {
        "system": "文王纳甲六爻v3.0", "cast_mode": cast_mode, "input_lines_bottom_to_top": lines,
        "pillars": pillars_out, "main_hexagram": main_hex["name"],
        "changed_hexagram": changed_hex["name"] if has_moving else "静卦无变",
        "palace": f"{palace_name}宫({palace_elem}) · {gen}", "shi_ying": {"shi": shi_pos, "ying": ying_pos},
        "special_structure": special + sanhe_hits, "lines_bottom_to_top": yao_rows, "fushen": fushen,
    }


# ============================================================================
# 6. FENGSHUI v3.0 (含合十/三般卦/伏反吟) + XIAOLIUREN + ZERI
# ============================================================================

MOUNTAINS_24 = [
    ("子", 0.0, 1, "天", -1), ("癸", 15.0, 1, "人", -1),
    ("丑", 30.0, 8, "地", -1), ("艮", 45.0, 8, "天", +1), ("寅", 60.0, 8, "人", +1),
    ("甲", 75.0, 3, "地", +1), ("卯", 90.0, 3, "天", -1), ("乙", 105.0, 3, "人", -1),
    ("辰", 120.0, 4, "地", -1), ("巽", 135.0, 4, "天", +1), ("巳", 150.0, 4, "人", +1),
    ("丙", 165.0, 9, "地", +1), ("午", 180.0, 9, "天", -1), ("丁", 195.0, 9, "人", -1),
    ("未", 210.0, 2, "地", -1), ("坤", 225.0, 2, "天", +1), ("申", 240.0, 2, "人", +1),
    ("庚", 255.0, 7, "地", +1), ("酉", 270.0, 7, "天", -1), ("辛", 285.0, 7, "人", -1),
    ("戌", 300.0, 6, "地", -1), ("乾", 315.0, 6, "天", +1), ("亥", 330.0, 6, "人", +1),
    ("壬", 345.0, 1, "地", +1),
]
PALACE_DIR = {1: "正北(坎)", 2: "西南(坤)", 3: "正东(震)", 4: "东南(巽)", 5: "中宫", 6: "西北(乾)", 7: "正西(兑)", 8: "东北(艮)", 9: "正南(离)"}
PALACE_YUAN_POLARITY = {(p, yl): pol for _, _, p, yl, pol in MOUNTAINS_24}
BAZHAI_YOUNIAN = {
    1: {4: "生气", 3: "天医", 9: "延年", 1: "伏位", 2: "绝命", 8: "五鬼", 6: "六煞", 7: "祸害"},
    2: {8: "生气", 7: "天医", 6: "延年", 2: "伏位", 1: "绝命", 4: "五鬼", 9: "六煞", 3: "祸害"},
    3: {9: "生气", 1: "天医", 4: "延年", 3: "伏位", 7: "绝命", 6: "五鬼", 8: "六煞", 2: "祸害"},
    4: {1: "生气", 9: "天医", 3: "延年", 4: "伏位", 6: "绝命", 2: "五鬼", 7: "六煞", 8: "祸害"},
    6: {7: "生气", 8: "天医", 2: "延年", 6: "伏位", 9: "绝命", 3: "五鬼", 1: "六煞", 4: "祸害"},
    7: {6: "生气", 2: "天医", 8: "延年", 7: "伏位", 3: "绝命", 9: "五鬼", 4: "六煞", 1: "祸害"},
    8: {2: "生气", 6: "天医", 7: "延年", 8: "伏位", 4: "绝命", 1: "五鬼", 3: "六煞", 9: "祸害"},
    9: {3: "生气", 4: "天医", 1: "延年", 9: "伏位", 8: "绝命", 7: "五鬼", 2: "六煞", 6: "祸害"},
}


def fly_loshu(center_star: int, direction: int) -> dict:
    return {p: ((center_star - 1 + direction * i) % 9) + 1 for i, p in enumerate([5, 6, 7, 8, 9, 1, 2, 3, 4])}


def calc_minggua(birth_year: int, gender: str) -> dict:
    s = sum(int(c) for c in str(birth_year))
    while s > 9:
        s = sum(int(c) for c in str(s))
    if gender.lower() in ("m", "male", "男"):
        g = ((11 - s) % 9) or 9
        g = 2 if g == 5 else g
    else:
        g = ((4 + s) % 9) or 9
        g = 8 if g == 5 else g
    return {
        "birth_year": birth_year, "gender": gender, "minggua_num": g,
        "minggua_palace": PALACE_DIR[g], "group": "东四命" if g in (1, 3, 4, 9) else "西四命",
        "younian_sectors": {PALACE_DIR[p]: star for p, star in BAZHAI_YOUNIAN[g].items()},
    }


def calc_fengshui(facing_deg: float, build_year: int, annual_year: int, birth_year: int = None, gender: str = "m") -> dict:
    facing_m = MOUNTAINS_24[int(((facing_deg % 360.0 + 7.5) % 360.0) // 15.0)]
    sitting_deg = (facing_deg + 180.0) % 360.0
    sitting_m = MOUNTAINS_24[int(((sitting_deg + 7.5) % 360.0) // 15.0)]
    period = ((build_year - 1864) // 20) % 9 + 1
    base_pan = fly_loshu(period, +1)
    sit_star, face_star = base_pan[sitting_m[2]], base_pan[facing_m[2]]
    mountain_pan = fly_loshu(sit_star, PALACE_YUAN_POLARITY.get((sit_star, sitting_m[3]), sitting_m[4]))
    facing_pan = fly_loshu(face_star, PALACE_YUAN_POLARITY.get((face_star, facing_m[3]), facing_m[4]))

    sp, fp = sitting_m[2], facing_m[2]
    if mountain_pan[sp] == period and facing_pan[fp] == period:
        pattern = "旺山旺向(丁财两旺最佳格)"
    elif mountain_pan[fp] == period and facing_pan[sp] == period:
        pattern = "上山下水(丁财受损，需外局反弓/水势化解)"
    elif mountain_pan[fp] == period and facing_pan[fp] == period:
        pattern = "双星会向(利财旺向，向首宜见水兼山)"
    elif mountain_pan[sp] == period and facing_pan[sp] == period:
        pattern = "双星会坐(利丁旺山，坐后宜实兼见水)"
    else:
        pattern = "常规盘局(需逐宫察当旺星与煞星组合)"

    special_patterns = []
    if all(base_pan[p] + mountain_pan[p] == 10 for p in range(1, 10)):
        special_patterns.append("全局山运合十")
    if all(base_pan[p] + facing_pan[p] == 10 for p in range(1, 10)):
        special_patterns.append("全局向运合十")
    fumu_sets = ({1, 4, 7}, {2, 5, 8}, {3, 6, 9})
    if all({base_pan[p], mountain_pan[p], facing_pan[p]} in fumu_sets for p in range(1, 10)):
        special_patterns.append("父母三般卦(全局通气大吉)")
    if all(mountain_pan[p] == p for p in range(1, 10)) or all(facing_pan[p] == p for p in range(1, 10)):
        special_patterns.append("伏吟局(沉滞不宜)")
    if all(mountain_pan[p] + p == 10 for p in range(1, 10)) or all(facing_pan[p] + p == 10 for p in range(1, 10)):
        special_patterns.append("反吟局(反复动荡)")

    annual_center = ((3 - (annual_year - 2024) - 1) % 9) + 1
    annual_pan = fly_loshu(annual_center, +1)
    y_branch = BRANCHES[(annual_year - 4) % 12]
    sansha_map = {
        "申": "正南(巳午未)", "子": "正南(巳午未)", "辰": "正南(巳午未)",
        "寅": "正北(亥子丑)", "午": "正北(亥子丑)", "戌": "正北(亥子丑)",
        "巳": "正东(寅卯辰)", "酉": "正东(寅卯辰)", "丑": "正东(寅卯辰)",
        "亥": "正西(申酉戌)", "卯": "正西(申酉戌)", "未": "正西(申酉戌)",
    }
    res = {
        "system": "三元玄空飞星v3.0 + 八宅明镜",
        "sitting_facing": f"坐{sitting_m[0]}({sitting_deg:.1f}°)向{facing_m[0]}({facing_deg:.1f}°)",
        "yuan_long": f"坐{sitting_m[3]}元龙 / 向{facing_m[3]}元龙",
        "period": f"{period}运 (建造/入住年份 {build_year})",
        "pattern": pattern,
        "special_patterns": special_patterns,
        "palaces": {PALACE_DIR[p]: {"运星": base_pan[p], "山星": mountain_pan[p], "向星": facing_pan[p], "流年星": annual_pan[p]} for p in range(1, 10)},
        "annual_sha": {
            "annual_year": annual_year, "year_branch": y_branch, "annual_center_star": annual_center,
            "five_yellow_wuhuang": [PALACE_DIR[p] for p, s in annual_pan.items() if s == 5][0],
            "two_black_erhei": [PALACE_DIR[p] for p, s in annual_pan.items() if s == 2][0],
            "sansha_direction": sansha_map[y_branch], "suipo_branch": BRANCH_CLASH[y_branch],
        },
    }
    if birth_year is not None:
        res["bazhai_minggua"] = calc_minggua(birth_year, gender)
    return res


XLR_PALACES = [
    ("大安", "木", "吉", "稳重安泰、宜守不宜激进、慢成。"),
    ("留连", "土", "凶", "拖延纠缠、暗昧反复、事难速成。"),
    ("速喜", "火", "大吉", "喜讯速至、明朗直截、快成。"),
    ("赤口", "金", "凶", "口舌是非、官非惊恐、破耗争执。"),
    ("小吉", "水", "吉", "贵人相助、和合顺利、稳妥有成。"),
    ("空亡", "土", "凶", "落空虚耗、事难成(避灾反吉)。"),
]


def calc_xiaoliuren(n1: int, n2: int, n3: int) -> dict:
    i1 = (n1 - 1) % 6
    i2 = (i1 + n2 - 1) % 6
    i3 = (i2 + n3 - 1) % 6
    p1, p2, p3 = XLR_PALACES[i1], XLR_PALACES[i2], XLR_PALACES[i3]
    return {
        "system": "道传小六壬", "inputs": [n1, n2, n3],
        "stage_1_initial": {"palace": p1[0], "element": p1[1], "tendency": p1[2]},
        "stage_2_process": {"palace": p2[0], "element": p2[1], "tendency": p2[2]},
        "stage_3_outcome": {"palace": p3[0], "element": p3[1], "tendency": p3[2], "meaning": p3[3]},
        "process_to_outcome_relation": element_relation(p2[1], p3[1]),
    }


def calc_zeri(start_date: str, days: int, birth_branch: str = None) -> dict:
    d0 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    good_days, excluded_count = [], 0
    for offset in range(days):
        dt = d0 + datetime.timedelta(days=offset, hours=12)
        p = get_ganzhi_pillars(dt)
        bad = p["is_month_breaker"] or p["is_year_breaker"] or (birth_branch and BRANCH_CLASH.get(birth_branch) == p["day_branch"]) or p["jianchu"] in ("破", "闭", "危")
        if bad:
            excluded_count += 1
        elif p["jianchu"] in ("成", "开", "定", "满", "除", "执"):
            good_days.append({"date": dt.strftime("%Y-%m-%d"), "day_gz": p["day_gz"], "month_gz": p["month_gz"], "jianchu": p["jianchu"], "note": p["jianchu_note"]})
    return {"system": "协纪辨方择日扫描", "range": f"{start_date} 起共 {days} 天", "birth_branch": birth_branch or "未提供", "recommended_days": good_days, "excluded_count": excluded_count}


def main():
    parser = argparse.ArgumentParser(description="Metaphysics Master Deterministic Engine v3.0")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_alm = sub.add_parser("almanac")
    p_alm.add_argument("--date", required=True)

    p_dlr = sub.add_parser("daliuren")
    p_dlr.add_argument("--time")
    p_dlr.add_argument("--day-gz")
    p_dlr.add_argument("--hour-branch")
    p_dlr.add_argument("--moon-general")
    p_dlr.add_argument("--period", choices=["day", "night"])

    p_zw = sub.add_parser("ziwei")
    p_zw.add_argument("--lunar-month", type=int, required=True)
    p_zw.add_argument("--lunar-day", type=int, required=True)
    p_zw.add_argument("--year-gz", required=True)
    p_zw.add_argument("--hour-branch", required=True)
    p_zw.add_argument("--gender", default="m")

    p_wy = sub.add_parser("wuyun")
    p_wy.add_argument("--year", type=int, required=True)

    p_mh = sub.add_parser("meihua")
    p_mh.add_argument("--time")
    p_mh.add_argument("--nums", nargs="+", type=int)

    p_ly = sub.add_parser("liuyao")
    p_ly.add_argument("--lines")
    p_ly.add_argument("--auto", action="store_true")
    p_ly.add_argument("--seed", default="")
    p_ly.add_argument("--date")
    p_ly.add_argument("--month-branch")
    p_ly.add_argument("--day-gz")

    p_fs = sub.add_parser("fengshui")
    p_fs.add_argument("--facing", type=float, required=True)
    p_fs.add_argument("--build-year", type=int, required=True)
    p_fs.add_argument("--annual", type=int, default=2026)
    p_fs.add_argument("--birth-year", type=int)
    p_fs.add_argument("--gender", default="m")

    p_xlr = sub.add_parser("xiaoliuren")
    p_xlr.add_argument("--nums", nargs=3, type=int, required=True)

    p_zr = sub.add_parser("zeri")
    p_zr.add_argument("--start", required=True)
    p_zr.add_argument("--days", type=int, default=14)
    p_zr.add_argument("--birth-branch")

    args = parser.parse_args()
    if args.cmd == "almanac":
        dt = datetime.datetime.strptime(args.date, "%Y-%m-%d") if len(args.date) == 10 else datetime.datetime.strptime(args.date, "%Y-%m-%d %H:%M")
        out = get_ganzhi_pillars(dt)
    elif args.cmd == "daliuren":
        out = calc_daliuren(args.time, args.day_gz, args.hour_branch, args.moon_general, args.period)
    elif args.cmd == "ziwei":
        out = calc_ziwei(args.lunar_month, args.lunar_day, args.year_gz, args.hour_branch, args.gender)
    elif args.cmd == "wuyun":
        out = calc_wuyun(args.year)
    elif args.cmd == "meihua":
        out = calc_meihua(args.time, args.nums)
    elif args.cmd == "liuyao":
        lines = [int(x.strip()) for x in args.lines.split(",")] if args.lines else None
        out = calc_liuyao(lines, args.date, args.seed, args.month_branch, args.day_gz)
    elif args.cmd == "fengshui":
        out = calc_fengshui(args.facing, args.build_year, args.annual, args.birth_year, args.gender)
    elif args.cmd == "xiaoliuren":
        out = calc_xiaoliuren(*args.nums)
    elif args.cmd == "zeri":
        out = calc_zeri(args.start, args.days, args.birth_branch)
    else:
        raise ValueError(f"Unknown command: {args.cmd}")

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
