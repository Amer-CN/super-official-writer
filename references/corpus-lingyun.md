# 蒸馏知识库速查（实战语料）

> 本文件为「超级公文写作 Skill」的实战知识库引用。
> 来源：抖音博主 **凌云笔杆子** 177 期 + **惠水组工** 20 期 + **材料改稿室** 79 期 + **大雨写材料** 82 期写作类视频，经口播转写→逐条蒸馏→结构化整理（2026-09）。
> 与 phrase-library.md（词句层）、templates.md（文体层）互补：本库是**方法+案例+金句的完整知识单元**，按 48 类组织。
> 层索引（v0.11，正文分层文件化；v0.12 增领域素材层、法定公文成稿范例层）：条目正文拆分至 `corpus/` 下 13 个分层文件（清单见下方「分层索引」，新增蒸馏=新增一个文件、不再改单体）；"书籍蒸馏·文种规范层"与"核稿病例层"补遗条目（B16-B19、C33-C48）分别在 book-wenzhong.md / book-hegao.md。
> 完整结构化数据（含全文）：lingyun/dataset/gongwen_writing_dataset.jsonl（961 条，含 v0.12 领域素材 53 条、v0.13 整理补齐 3 条；成文范例 5 篇成稿不入 dataset）。

## 检索规则

- **Step2 磨刀子**：明确文体后，先查 [corpus/INDEX.md](corpus/INDEX.md) 按分类定位条目与层文件，读取该类条目找方法。
- **Step4 敲键子**：起草中卡壳（标题不出彩/开头写不下去/小标题平），按场景查对应类。
- 优先级：templates.md（文体框架）> 本库（实战方法）> phrase-library.md（词句润色）。

按知识分类检索见 [corpus/INDEX.md](corpus/INDEX.md)（48 类自动生成）。

## 分层索引

- [corpus/lingyun-huishui.md](corpus/lingyun-huishui.md)——主层：凌云笔杆子 177 期+惠水组工 20 期实战方法，35 类速查（191 条）。
- [corpus/book-wenzhong.md](corpus/book-wenzhong.md)——书籍蒸馏·文种规范层（书 1+书 2）：15 法定文种+60 事务文种定义/结构/写法，选文种搭结构时查（64 条）。
- [corpus/book-hegao.md](corpus/book-hegao.md)——书籍蒸馏·核稿病例层（书 3）：57 个真实病例+核稿十查清单，写完自查/核稿时用（45 条）。
- [corpus/blogger-zhuodaoren.md](corpus/blogger-zhuodaoren.md)——博主蒸馏层·捉刀人（33 期）：公文处理条例逐条精讲+国标格式原理拆解（19 条）。
- [corpus/blogger-gongwenbaidu.md](corpus/blogger-gongwenbaidu.md)——博主蒸馏层·公文摆渡（109 期）：句式模板+写作思维模型+马哲底层逻辑（80 条）。
- [corpus/gongzuobaogao.md](corpus/gongzuobaogao.md)——报告蒸馏层：27 份政府工作报告（2000-2026）句式基准/提法迭代/收尾金句/一级骨架（17 条）。
- [corpus/book-shouji2.md](corpus/book-shouji2.md)——书籍蒸馏层·实务经验（秘书工作手记2）：找范文/领导意图揣摩/词句操作/修改整容（52 条）。
- [corpus/book-fuchuan.md](corpus/book-fuchuan.md)——书籍蒸馏层·文种要领（付传）：各文种写法公式/文种间选用辨析/易错点（40 条）。
- [corpus/blogger-gaigaoshi.md](corpus/blogger-gaigaoshi.md)——博主蒸馏层·材料改稿室（79 期）：改稿视角——低水平 vs 高水平对照/领导改稿指令解码/提法进阶（79 条）。
- [corpus/blogger-dayu.md](corpus/blogger-dayu.md)——博主蒸馏层·大雨写材料（82 期）：思路框架视角——逻辑主线/亮点打造/材料四度（46 条）。
- [corpus/blogger-wenxiong.md](corpus/blogger-wenxiong.md)——博主蒸馏层·加夜班的文兄（220 期，含 19 图文期）：数字框架库+申论应试视角——每期一个拿来即用的数字框架/高频句式库/万能素材+检视负面表述库/成稿范例（208 条，含 v0.13 整理补齐 1 条）。
- [corpus/domains.md](corpus/domains.md)——领域素材层（v0.12 新增，评测 P1-1）：安全生产/养老托幼/基层治理/国企办公四大领域机制口径、指标清单、典型句式，来源为历年政府工作报告+既有层归拢+评测产出整理，写领域材料配素材时查（53 条，dataset id=domain_001～053）。
- [corpus/chengwen-fanli.md](corpus/chengwen-fanli.md)——法定公文成稿范例层（v0.12 新增，评测 P0-2/P1-6/P2-2）：纪要/通知/请示/批复/函五文种各 1 篇成稿+版式要素清单+关键块详略尺度说明（5 篇成稿；v0.13 增联署函要点整理条目入 dataset，id=tiaoli_fanli_001）；法定公文跳过 style-params 量化参数对照，以 format-spec.md 合规为验收标准。
