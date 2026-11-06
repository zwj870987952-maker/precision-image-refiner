# 本地超分管线

本管线只处理已保存的本地图片，不调用 Gemini 或任何生成 API。依赖见 skill 根目录的 `requirements.txt`；需要安装时使用当前选定 Python 的 `python -m pip install -r "<skill目录>/requirements.txt"`，优先复用已有环境。

## 模型与命令

模型必须接受 RGB float32 NCHW 输入，输出 RGB NCHW，放大倍数为 4；默认使用 CPUExecutionProvider。支持动态空间尺寸的 RealESRGAN x4 ONNX 模型。

按顺序寻找显式 `--model`、skill 内 `models/real_esrgan_x4.onnx`、`~/.cache/precision-image-refiner/real_esrgan_x4.onnx`，并兼容复用本机已有的 `~/.gemini/antigravity/scratch/models/real_esrgan_x4.onnx`。显式模型路径不存在时不会悄悄替换。

模型缺失且实际任务需要下载时，可加 `--download-model`，下载到缓存目录；可用 `--model-url` 指定用户选择的来源。内置地址继承自原技能，迁移时未在线验证，下载失败时如实报告并使用用户提供的模型。下载保留 TLS 校验，先写临时文件再重命名。

```powershell
python "<skill目录>/scripts/master_superres_pipeline.py" --input "C:/project/input.png" --output "C:/project/outputs" --prefix poster --model "C:/models/real_esrgan_x4.onnx"
```

分块默认 200px，pad 为 20px，步长为 tile-size 减 2×pad。显存或内存不足时可调低 `--tile-size`，并满足 `tile-size > 2×pad`。神经结果仍按原图 4 倍尺寸分配全图数组，大图应先评估可用内存。

背景平滑须提供与输入原图同尺寸的灰度 `--bg-mask`：白色代表背景，黑色代表保留，灰度作为过渡。不根据画面顶部或两侧猜测背景。默认不平滑。`--no-bg-smooth` 保留为兼容选项。

## 输出与限制

- `<prefix>_sr.png`：实际原图 4 倍的神经结果，经过 Lab 色度回填。
- `<prefix>_4k.png/.jpg`：长边 3840，保持纵横比。
- `<prefix>_5k.png/.jpg`：长边 5120，保持纵横比。
- `<prefix>_100pct_macro_crop.png`：5K 图的一块实际像素裁切；默认下半部，可用 `--qa-box X Y W H` 指定在 5K 图上的坐标。
- `<prefix>_manifest.json`：输入、神经及导出尺寸，额外插值情况与裁切坐标。

PNG 无损编码，JPEG quality=100 且 subsampling=0；两者均写入 300 DPI 元数据。裁切无需放大即可检查文件真实像素，聊天预览本身仍可能缩放。

Lab 回填是保色策略，不是色彩管理或零偏色证明；输出按 RGB 数值处理，不保留输入的原始 ICC 配置。脚本根据 EXIF 朝向读取图像，含实际透明像素的输入会拒绝处理，避免静默丢失透明背景，应继续使用支持透明图片的工具。
