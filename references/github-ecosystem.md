# GitHub 开源玄学 Skill 工程化最佳实践与架构参考（v2.0）

本技能系统吸收了 GitHub 开源玄学社区 12+ 头部仓库的工程范式，构建从历法原语到多派裁决的全栈防幻觉闭环。

## 一、吸收的头部开源仓库架构精华

1. **FANzR-arch/Numerologist_skills (2.2k stars)**：先追问再输出、确定性计算外包、先声明口径再做结论。
2. **Renhuai123/ziwei-doushu (19.3k stars)**：倪海厦《天纪》紫微斗数体系、经典格局知识库、斗数批六亲局限提示与天文+地理阳宅同参。
3. **voidforall/fengshui.skill (598 stars)**：计算交给代码解读交给模型、峦头为体理气为用、典籍出处核对分级。
4. **Brhiza/mingyu (598 stars)**：全栈术数工具包架构（三式绝学 + 周易占卜 + 紫微八字 + 五运六气 + 择日风水）。
5. **ChesterRa/mingpan (136 stars)**：明确节气月（八字/奇门/六壬）与农历月（紫微）双历法基准、统一子初换日口径、纯事实排盘与 AI 解读解耦。
6. **kentang2017/kinliuren (118 stars)**：大六壬天地盘、四课三传、十二天将与神煞架构。
7. **shubhaviatiningsih-byte/fortune-liuyao-skill (76 stars)**：先排盘再核盘后断事、条件性应期链（病处->解除->窗口）、防编造事实审计。
8. **Wolke/ziwei-doushu (23 stars)**：紫微斗数模块化 references 结构（十二宫/十四主星/辅煞/四化/格局/大限流年）。
9. **shizi2077/liu-ren-divination-skill**：大六壬月将铁律、日柱阴阳合法性校验、`needs_review` 复杂涉害边界机制。
10. **lizecheng2021-maker/metaphysics-synthesis-skill**：多术数独立发声再取共振交集、`RUNNABLE/PARTIAL/BLOCKED` 三级输入契约。
11. **xuemian168/bazi-skill & gaoxin492/bazi-skill**：计算层(Python)+结构层(JSON)+解读层(Agent) 解耦，五派会诊与源层级裁决。
12. **qiyan233/meihua-divination & muyen/meihua-yishu**：梅花易数卦义先行、用近互中变后的结构化断事骨架。

## 二、反幻觉出厂自检清单

- 凡排盘计算是否 100% 经由 `scripts/metaphysics_engine.py` 输出，零大模型心算？
- 报告中每一处干支、卦名、主星、四化、天将、飞星，是否与脚本 JSON 严格一致？
- 若出现参数缺失或脚本返回 `needs_review: true`，是否如实披露而非硬编？
- 是否遵守「节气月 vs 农历月」双基准，未把公历月日误作农历月日、未把农历月支误作大六壬月将？
- 是否直指核心病处与可执行对策，拒绝空洞安慰与迷信推销，且守住医疗/法律/高危财务安全边界？
