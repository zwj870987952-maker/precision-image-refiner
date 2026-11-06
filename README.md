# Precision Image Refiner 🎯

> **商业级产品图与海报局部精准重绘、参考材质迁移与像素级母带超分通用工作流（AI Skill 规范）**
> 
> A mature, battle-tested agent skill for photorealistic commercial product image inpainting, strict composition locking, reference material transfer, and 4K/5K zero-color-shift poster upscaling.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Skill Format: Markdown](https://img.shields.io/badge/Skill-SKILL.md-orange.svg)](SKILL.md)

---

## 💡 为什么需要这个 Skill？

当前 AI 图像生成工具（Midjourney, Stable Diffusion, Gemini Imagen, DALL-E 3）在商业海报与产品图精修任务中普遍存在 **4 大致命硬伤**：

1. **构图随意漂移**：要求修改底部底座，AI 却把瓶身、文字、相机机位和背景全都改变了；
2. **“降噪”理解为“抹成蜡块”**：单纯给 Prompt 加 `denoise/clean`，AI 会把青苔、花瓣抹成一团毫无细节的塑料平滑糊块；
3. **过度发挥与乱加元素**：AI 喜欢擅自喷洒密密麻麻的白色反光露水、添加杂枝枯叶，破坏高级纯净感；
4. **放大后发软或有马赛克**：简单数学插值（双三次/Lanczos）本质只是像素拉伸，放大至 100% 查看时细节全无，无法满足 300 DPI 印刷制版需求。

本项目沉淀了一套**工业级、防漂移、高保真**的端到端方法论与代码管线，让任何接入此 Skill 的 AI Agent 都能稳定产出 4K/5K 商业海报级成品。

---

## 🛠️ 核心架构与方法论

```
                    【 用户简短需求输入 】
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │   阶段 1：前置四重对齐协议 (Pre-flight)    │
        │   • 死锁区域 / 构图级别 / 参考图角色 / 避坑清单  │
        └───────────────────────────────────────────┘
                              │ 用户确认无误后执行
                              ▼
        ┌───────────────────────────────────────────┐
        │   阶段 2：1:1 原位微距高频材质置换重绘   │
        │   • 严格原图构图母体 + 语义隔离材质迁移   │
        │   • 拒绝平滑蜡感，微观高频细节显式置换   │
        └───────────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │   阶段 3：4K/5K 商业海报级母带超分管线   │
        │   • 分块神经网络超分 (Tiled RealESRGAN)   │
        │   • Lab 色彩空间 100% 绝对死锁 (0 偏色)   │
        │   • 演播室渐变双边平滑保护 (0 Banding)    │
        └───────────────────────────────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │        阶段 4：双规格母带与 QA 验收       │
        │   • 4K UHD (3840p) + 5K Master (300 DPI)  │
        │   • 100% 实际像素微距原切特写验核         │
        └───────────────────────────────────────────┘
```

---

## 🚀 快速上手 (Quick Start)

### 1. 安装依赖
```bash
git clone https://github.com/<your-username>/precision-image-refiner.git
cd precision-image-refiner
pip install -r requirements.txt
```

### 2. 运行海报级母带超分脚本
```bash
python scripts/master_superres_pipeline.py \
  --input path/to/your_image.jpg \
  --output ./output \
  --prefix product_master
```

输出文件：
- `./output/product_master_4k.png`：标准 4K 竖屏 3840p 无损版
- `./output/product_master_4k.jpg`：标准 4K 100% 满画质 JPG (4:4:4 无色度采样压缩)
- `./output/product_master_5k.png`：5K 巨幅印刷母带 (3392×5056)
- `./output/product_master_100pct_macro_crop.jpg`：100% 实际像素微距特写验核图

---

## 🤖 如何在其他 AI Agent 中使用此 Skill？

本仓库完全兼容各大主流 Agent 规范（Claude Code, Cursor, Antigravity, OpenClaw, AutoGen 等）：

### 方案 A：在 Claude Code / Cursor / Windsurf 中载入
将本项目克隆到工程的 skills 目录或作为上下文载入：
```bash
# 在 Prompt 中引入
@SKILL.md 按照该 Skill 规范对我的输入图进行 1:1 局部重绘与超分。
```

### 方案 B：在 Antigravity / OpenClaw 中全局注册
直接将本目录复制或软链接至 Agent 的 skills 路径：
```bash
# Windows
New-Item -ItemType SymbolicLink -Path "C:\Users\<user>\.gemini\config\skills\precision-image-refiner" -Target "C:\path\to\precision-image-refiner"

# Linux / Mac
ln -s /path/to/precision-image-refiner ~/.config/skills/precision-image-refiner
```

---

## 📁 仓库结构

```
precision-image-refiner/
├── SKILL.md                   # 核心 Agent 指南与前置对齐协议 (Universal Skill Spec)
├── README.md                  # 项目全景说明文档
├── requirements.txt           # 运行依赖
├── LICENSE                    # MIT 开源协议
├── scripts/
│   └── master_superres_pipeline.py  # 工业级 4K/5K 超分与保色流水线脚本
└── examples/
    └── prompt_templates.md    # 经过实战检验的高频微距提示词库与负向规避词
```

---

## Codex 适配版

`codex/precision-image-refiner/` 是独立的 Codex skill 包，包含 Codex 图片工具调用说明、`agents/openai.yaml` 界面配置、提示词参考和修正后的本地超分脚本。仓库根目录保留原通用/Gemini 版本。

在仓库根目录运行以下 PowerShell 命令安装到 Codex 的 skills 目录：

```powershell
$codexSkillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Force -Path $codexSkillRoot | Out-Null
Copy-Item -LiteralPath './codex/precision-image-refiner' -Destination $codexSkillRoot -Recurse -Force
```

在 Codex 中调用：

```text
使用 $precision-image-refiner 精修这张产品图，保持产品、文字和构图。
```

本地超分仅在用户需要时执行，复用可用 Python 环境及本地 x4 ONNX 模型。新版按长边 3840/5120 像素导出 4K/5K 图片，记录实际尺寸和额外插值情况，背景平滑需明确蒙版。依赖、模型与选项详见 [超分说明](codex/precision-image-refiner/references/super_resolution.md)。

## 📜 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。欢迎集成到任何 AI Agent、自动化工作流或商业修图流水线中！
