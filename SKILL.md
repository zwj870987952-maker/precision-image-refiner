---
name: precision-image-refiner
description: 商业级产品图与海报局部精准重绘、参考材质迁移与像素级母带超分工作流。适用于产品广告修图、1:1构图死锁重绘、消除AI塑料假噪点、微观摄影级质感注入、以及4K/5K无偏色零锐化海报母带级无损导出。
---

# Precision Image Refiner（商业级局部精准重绘与母带超分 Skill）

本 Skill 专为 AI Agent（Claude Code, Cursor, Antigravity, OpenClaw, GPT 等）设计，用于在面对商业广告修图、电商海报质感重绘任务时，解决常规 AI **“擅自改构图”、“把去噪理解为抹成蜡块”、“滥加反光露水”、“放大后模糊或有马赛克颗粒”** 等致命缺陷。

---

## 一、 核心工作原则（AI 必须严格遵守的铁律）

1. **绝对禁止盲目直接生图**：收到用户简短需求后，必须先走【前置四重对齐协议】，确定边界才能动手。
2. **1:1 原位死锁法则**：除非用户明确授权“允许构图重组”，否则所有物体的相对位置、大小、摆放朝向、阴影和前后遮挡必须 1:1 绝对保持。
3. **参考图“语义隔离”法则**：当用户提供参考图时，必须明确参考图仅作为“材质/质感参考”，绝对禁止把参考图中的次要物体、错别字或外延构图元素（如树枝、落花瓣、拉宽地面）带入画面。
4. **高频置换替代低频抹平**：严禁在 Prompt 中单纯堆叠 `denoise`，这会导致 AI 抹杀物理细节变成塑料蜡块；必须以显式微距单反词汇（植物细胞脉络、天鹅绒星状青苔纤维、矿物晶体解理）显式置换伪噪点。
5. **母带级超分替代简单插值**：严禁仅用双三次/Lanczos 平滑拉伸（放大后必发虚）；必须运行分块神经超分与 Lab 色度死锁管线。

---

## 二、 阶段 1：前置四重对齐协议（Pre-flight Confirmation）

当用户给出简短需求（如“帮我改下底座的花草和石头，现在太假了”）时，Agent **必须首先输出以下对齐模板，向用户确认并补齐关键信息**：

```markdown
收到您的重绘需求！为确保【绝对不改动您满意的部分，且绝不盲目过度发挥】，在开始前与您确认以下基准：

1. **绝对锁定不变**：[例如：上方两款产品瓶身造型、泵头、品牌排版文字、背景演播室橙粉光晕色温 100% 保持不变]
2. **允许重绘区域**：[例如：仅限底座的花朵、青苔、岩石与流淌蜜液]
3. **构图锁定级数**：严格 1:1 原位死锁（保留前排小圆石、三朵花相对位置、独立岛屿紧凑感，不扩增底座）
4. **材质与质感要求**：
   - 花瓣：干净柔嫩、高级哑光微距质感，彻底去除多余碎露水；
   - 青苔：毛茸茸、成簇生长的天然高密天鹅绒纤维；
   - 岩石：天然风化粗砺矿物晶体切面；
   - 蜜液：纯净通透、高折射与饱满表面张力。
5. **是否需要参考图**：如果您有满意的材质标杆图，可随时提供，我将仅提取其材质质感，绝不改变现有构图。

请确认以上边界是否准确，确认后立即为您执行！
```

---

## 三、 阶段 2：局部超写实微距重绘与 Prompt 编写规范

调用图像生成/重绘工具（如 Midjourney, Stable Diffusion Inpainting, 或 Gemini `generate_image`）时：

### 1. 双图输入的角色定义
- `input_file_0.png`：**COMPOSITION MASTER（构图与主体绝对母体）**。
- `input_file_1.png`：**TEXTURE REFERENCE ONLY（材质参考）**。

### 2. 标准 Prompt 模版
```text
Modify input_file_0.png with strict 1:1 composition lock and photorealistic material upgrade:

STRICT COMPOSITION LOCK (DO NOT ALTER):
- 100% preserve the exact composition, silhouette, scales, and positions of all objects from input_file_0.png.
- Maintain the exact product bottles, labels, typography, and background lighting.
- Retain the exact isolated compact island base with clean studio table margins on left and right.
- Retain the exact 4-5 small round pebbles arranged in the moss in front.
- NO added branches, NO black twigs, NO fallen petals on rock, NO flattened wide ground.

TEXTURE RECONSTRUCTION (REFERENCE input_file_1.png FOR SURFACE FINISH ONLY):
- Fresh Real Flowers: velvety, soft matte botanical petals with organic cellular veining. ABSOLUTELY ZERO EXCESSIVE DEWDROPS OR WATER DROPLETS. Clean, dry, pristine petals.
- Lush Velvety Moss: microscopic fuzzy star-moss fibers, dense clumping, rich organic depth.
- Natural Mineral Stone: weathered natural granite rock with crisp crystalline facets, pores, and natural crevices.
- Honey: crystal-clear golden amber nectar with realistic fluid surface tension and clean specular highlights.

Hasselblad medium format macro commercial product photography, 8k resolution, razor-sharp textures, zero hallucinated objects.
```

---

## 四、 阶段 3：商业海报级母带超分管线执行

在获得重绘结果后，执行项目内置脚本：

```bash
python scripts/master_superres_pipeline.py \
  --input /path/to/inpainted_image.jpg \
  --output /path/to/output_dir \
  --prefix master_poster
```

### 核心功能与技术实现：
1. **分块神经网络超分（Tiled Neural Super-Resolution）**：
   - 采用 200×200 分块 + 20px 重叠 + 2D Bartlett 帐篷窗加权融合，消除分块拼缝。
2. **Lab 空间 100% 色彩绝对锁定**：
   - 提取超分网络的明度 L 通道，色度 a/b 通道严格取自原图双三次上采样，确保暖光色温 0.00% 偏移。
3. **演播室背景双边滤波保护**：
   - 自动识别纯净背景区域，消除色阶断层（Banding）与微观噪斑。
4. **双规格母带与 QA 原切导出**：
   - `master_poster_4k.png` (标准 4K 竖屏 3840p 无损版)
   - `master_poster_4k.jpg` (100% 满画质，4:4:4 无压缩采样)
   - `master_poster_5k.png` & `master_poster_5k.jpg` (3392×5056，300 DPI 印刷级母带)
   - `master_poster_100pct_macro_crop.jpg` (100% 实际像素切片，用于即时验核微观质感)

---

## 五、 阶段 4：交付验收规范

向用户交付时，必须同时呈现：
1. **母带下载链接**（4K 与 5K 双格式链接）；
2. **海报全景预览图**；
3. **【100% 实际像素微距原切特写】**（展示花瓣经络、青苔绒毛、岩石颗粒，证明放大后绝无模糊与马赛克）。
