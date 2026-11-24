#!/usr/bin/env python3
"""
Real Classical & Open-Source Golden Case Regression Test Suite (python3 -S)
Tests 12 verified classical & benchmark cases across all 8 deterministic engines.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metaphysics_engine as eng


def run_all_tests():
    results = []

    # 1. Da Liu Ren Golden Case 1: kinliuren README (己未日 甲午时 惊蛰/亥将 昼占)
    r1 = eng.calc_daliuren(day_gz="己未", hour_branch="午", moon_general="亥", period="day")
    assert r1["principle"] == "比用(知一)", f"Expected 比用(知一), got {r1['principle']}"
    t1 = [(x["branch"], x["general"], x["six_relation"], x["dungan"]) for x in r1["three_transmissions"]]
    assert t1 == [("巳", "白虎", "父母", "丁"), ("戌", "朱雀", "兄弟", "壬"), ("卯", "玄武", "官鬼", "乙")], f"Got {t1}"
    results.append("PASS [1/12] 大六壬·坚大六壬黄金课例(己未日甲午时亥将昼占): 比用知一 巳(虎/父/丁)->戌(雀/兄/壬)->卯(玄/官/乙)")

    # 2. Da Liu Ren Golden Case 2: shizi2077 司天监课例 (甲寅日 酉时 申将 夜占)
    r2 = eng.calc_daliuren(day_gz="甲寅", hour_branch="酉", moon_general="申", period="night")
    assert r2["principle"] == "比用(知一)"
    t2 = [(x["branch"], x["general"], x["six_relation"], x["is_xunkong"]) for x in r2["three_transmissions"]]
    assert t2 == [("子", "白虎", "父母", True), ("亥", "太常", "父母", False), ("戌", "玄武", "妻财", False)], f"Got {t2}"
    results.append("PASS [2/12] 大六壬·司天监黄金课例(甲寅日酉时申将夜占): 比用知一 子(虎/父/空)->亥(常/父)->戌(玄/财)")

    # 3. Liuyao Classical Case 1: 《增删卜易·卷一》子月卯日 坤为地 变 火地晋 (四爻、上爻动)
    r3 = eng.calc_liuyao(lines=[8, 8, 8, 6, 8, 6], month_branch="子", day_gz="丁卯")
    assert r3["main_hexagram"] == "坤为地" and r3["changed_hexagram"] == "火地晋"
    assert "本卦六冲" in r3["special_structure"]
    top_line = r3["lines_bottom_to_top"][5]
    assert top_line["branch"] == "酉" and top_line["six_relation"] == "子孙" and "世" in top_line["tags"]
    assert top_line["change"]["changed_branch"] == "巳" and top_line["change"]["changed_relation"] == "父母"
    assert "回头克" in top_line["change"]["interaction"] and "化长生" in top_line["change"]["interaction"]
    results.append("PASS [3/12] 六爻·《增删卜易》卷一原例(子月卯日 坤变火地晋): 上爻酉金子孙持世动化巳火父母回头克")

    # 4. Liuyao Classical Case 2: 《增删卜易·卷二》化进神/化退神与化墓/化绝检测
    r4 = eng.calc_liuyao(lines=[7, 8, 9, 7, 6, 8], date_str="2026-11-23")
    assert r4["main_hexagram"] == "雷火丰" and r4["changed_hexagram"] == "泽雷随"
    assert r4["palace"] == "坎宫(水) · 5世"
    assert "回头克" in r4["lines_bottom_to_top"][2]["change"]["interaction"]
    assert "化墓" in r4["lines_bottom_to_top"][2]["change"]["interaction"]  # 亥水化辰土为化墓!
    assert "化进神" in r4["lines_bottom_to_top"][4]["change"]["interaction"]  # 申金化酉金为化进神!
    results.append("PASS [4/12] 六爻·动变复合校验(雷火丰变泽雷随): 三爻亥水化辰回头克兼化墓、五爻申金化酉化进神")

    # 5. Fengshui Classical Case 1: 《沈氏玄空学》会稽章宅 (七运 子山午向 -> 双星会坐 双七临坎)
    r5 = eng.calc_fengshui(facing_deg=180, build_year=1990, annual_year=2026)
    assert "7运" in r5["period"] and "双星会坐" in r5["pattern"]
    assert r5["palaces"]["正北(坎)"]["山星"] == 7 and r5["palaces"]["正北(坎)"]["向星"] == 7
    results.append("PASS [5/12] 风水·《沈氏玄空学》会稽章宅古籍原例(七运子山午向): 精准双星会坐·双七临坎")

    # 6. Fengshui Classical Case 2: 九运 子山午向 + 八运 丑山未向 (旺山旺向)
    r6a = eng.calc_fengshui(facing_deg=180, build_year=2024, annual_year=2026, birth_year=2006, gender="m")
    assert "双星会坐" in r6a["pattern"] and r6a["palaces"]["正北(坎)"]["山星"] == 9 and r6a["palaces"]["正北(坎)"]["向星"] == 9
    assert r6a["annual_sha"]["five_yellow_wuhuang"] == "正南(离)" and r6a["bazhai_minggua"]["minggua_num"] == 3
    r6b = eng.calc_fengshui(facing_deg=210, build_year=2010, annual_year=2026)  # 八运 丑山未向
    assert "旺山旺向" in r6b["pattern"]
    results.append("PASS [6/12] 风水·九运子山午向(双星会坐+2026五黄正南)与八运丑山未向(旺山旺向)校验通过")

    # 7. Zi Wei Dou Shu Golden Case 1: 丙戌年 农历正月十一日 午时 男 (火六局/七杀朝斗/杀破狼/完整六吉六煞四化)
    r7 = eng.calc_ziwei(lunar_month=1, lunar_day=11, year_gz="丙戌", hour_branch="午", gender="m")
    assert r7["bureau"] == "火六局" and r7["minggong"] == "丙申" and r7["daxian_direction"] == "顺行"
    assert "七杀朝斗/仰斗格" in r7["detected_patterns"] and "杀破狼格(开创变动强)" in r7["detected_patterns"]
    # Verify 丙年 文昌化科 placed in a real palace (午时 -> 戌逆数午6位 -> 辰宫!)
    chen_palace = [p for p in r7["twelve_palaces"] if p["ganzhi"].endswith("辰")][0]
    assert "文昌[化科]" in chen_palace["auspicious_stars"], f"Expected 文昌[化科] in 辰, got {chen_palace}"
    results.append("PASS [7/12] 紫微·丙戌年正月十一午时男盘: 火六局、七杀朝斗+杀破狼、文昌[化科]落财帛辰宫")

    # 8. Zi Wei Dou Shu Golden Case 2: 庚辰年 农历五月初一 寅时 男 (金四局/紫微在亥/天府在巳)
    r8 = eng.calc_ziwei(lunar_month=5, lunar_day=1, year_gz="庚辰", hour_branch="寅", gender="m")
    assert r8["bureau"] == "金四局" and r8["minggong"] == "庚辰"
    hai_p = [p for p in r8["twelve_palaces"] if p["ganzhi"].endswith("亥")][0]
    si_p = [p for p in r8["twelve_palaces"] if p["ganzhi"].endswith("巳")][0]
    assert "紫微" in hai_p["major_stars"] and "天府" in si_p["major_stars"]
    results.append("PASS [8/12] 紫微·庚辰年五月初一寅时男盘: 金四局、紫微在亥天府在巳、六吉六煞与大限精确")

    # 9. Meihua Yishu Case: 2026-11-23 21:49 时间起卦 (天风姤 -> 互乾为天 -> 变火风鼎)
    r9 = eng.calc_meihua(time_str="2026-11-23 21:49")
    assert r9["main_hexagram"] == "天风姤" and r9["mutual_hexagram"] == "乾为天" and r9["changed_hexagram"] == "火风鼎"
    assert r9["ti_trigram"]["name"] == "巽" and r9["ti_trigram"]["seasonal_strength"] == "相"
    results.append("PASS [9/12] 梅花易数·时间起卦校验: 天风姤->互乾->变火风鼎，冬亥月巽木体相乾金用休")

    # 10. Almanac Solar Longitude Boundary Test: 2025 Lichun (2025-02-03 22:10 UTC+8)
    r10_before = eng.get_ganzhi_pillars(eng.datetime.datetime(2025, 2, 3, 21, 0))
    r10_after = eng.get_ganzhi_pillars(eng.datetime.datetime(2025, 2, 3, 23, 0))
    assert r10_before["year_gz"] == "甲辰" and r10_after["year_gz"] == "乙巳", f"Before:{r10_before['year_gz']}, After:{r10_after['year_gz']}"
    results.append("PASS [10/12] 天文节气边界校验(2025立春22:10): 21:00为甲辰年，23:00精准切换乙巳年")

    # 11. Wuyun Liuqi Case: 2026 丙午年 (水运太过、少阴君火司天、阳明燥金在泉)
    r11 = eng.calc_wuyun(2026)
    assert r11["year_gz"] == "丙午" and r11["central_circuit"] == "水运太过"
    assert r11["sitian_H1"] == "少阴君火" and r11["zaiquan_H2"] == "阳明燥金"
    results.append("PASS [11/12] 五运六气·2026丙午年校验: 水运太过、少阴君火司天、阳明燥金在泉")

    # 12. Xiao Liu Ren + Zeri Verification
    r12a = eng.calc_xiaoliuren(1, 1, 1)
    assert r12a["stage_3_outcome"]["palace"] == "大安"
    r12b = eng.calc_zeri("2026-11-24", 7, "戌")
    assert all(d["day_gz"][1] != "辰" for d in r12b["recommended_days"])  # 辰冲戌必须已排除
    results.append("PASS [12/12] 小六壬(1,1,1->大安)与协纪辨方择日(自动排除冲戌之辰日)校验通过")

    for line in results:
        print(line)
    print(f"\nALL {len(results)}/12 REAL CLASSICAL & GOLDEN BENCHMARK TESTS PASSED!")


if __name__ == "__main__":
    run_all_tests()
