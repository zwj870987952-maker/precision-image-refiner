#!/usr/bin/env python3
"""Tiled RealESRGAN x4 with chroma preservation and dimension-accurate exports.

Adapted from the original precision-image-refiner pipeline; see ../LICENSE.
"""
import argparse
import json
import os
from pathlib import Path
import ssl
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageOps

DEFAULT_MODEL_URL = "https://huggingface.co/SceneWorks/real-esrgan-onnx/resolve/main/real_esrgan_x4.onnx"


def ensure_model(model_path=None, download=False, model_url=DEFAULT_MODEL_URL):
    cache = Path.home() / ".cache/precision-image-refiner/real_esrgan_x4.onnx"
    if model_path:
        target = Path(model_path).expanduser()
        candidates = [target]
    else:
        target = cache
        candidates = [Path(__file__).resolve().parent.parent / "models/real_esrgan_x4.onnx",
                      cache,
                      Path.home() / ".gemini/antigravity/scratch/models/real_esrgan_x4.onnx"]
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size:
            return str(candidate.resolve())
    if not download:
        raise FileNotFoundError("No local x4 ONNX model found. Supply --model or explicitly use --download-model.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    request = urllib.request.Request(model_url, headers={"User-Agent": "precision-image-refiner"})
    try:
        with urllib.request.urlopen(request, timeout=120, context=context) as response:
            with temporary.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
        if not temporary.stat().st_size:
            raise ValueError("Downloaded model is empty")
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return str(target.resolve())


def tile_starts(length, size, pad):
    if size <= 0 or pad < 0 or size <= 2 * pad:
        raise ValueError("tile-size must be positive and greater than 2*pad; pad must be nonnegative")
    if length <= size:
        return [0]
    last = length - size
    return sorted(set(list(range(0, last + 1, size - 2 * pad)) + [last]))


def neural_upscale(img, session, tile_size=200, pad=20):
    h, w = img.shape[:2]
    xs, ys = tile_starts(w, tile_size, pad), tile_starts(h, tile_size, pad)
    scale = 4
    output = np.zeros((h * scale, w * scale, 3), dtype=np.float32)
    weight = np.zeros((h * scale, w * scale, 1), dtype=np.float32)
    inputs = session.get_inputs()
    if len(inputs) != 1 or inputs[0].type != "tensor(float)":
        raise ValueError("Expected a single float32 NCHW input")
    total = len(xs) * len(ys)
    done = 0
    for y in ys:
        for x in xs:
            tile = img[y:y + tile_size, x:x + tile_size]
            th, tw = tile.shape[:2]
            # Pad small inputs so tiny images and border tiles remain valid.
            padded = cv2.copyMakeBorder(tile, 0, tile_size - th, 0, tile_size - tw, cv2.BORDER_REPLICATE)
            inp = np.ascontiguousarray(padded[:, :, ::-1].transpose(2, 0, 1)[None], dtype=np.float32) / 255.0
            result = session.run(None, {inputs[0].name: inp})[0]
            if result.shape != (1, 3, tile_size * scale, tile_size * scale):
                raise ValueError(f"Expected x4 RGB NCHW output, received {result.shape}")
            result = result[0].transpose(1, 2, 0)[:th * scale, :tw * scale, ::-1]
            result = np.clip(result * 255.0, 0, 255)
            window = (np.bartlett(th * scale)[:, None] * np.bartlett(tw * scale)[None, :])[:, :, None]
            window = window.astype(np.float32) + 1e-4
            region = np.s_[y * scale:(y + th) * scale, x * scale:(x + tw) * scale]
            output[region] += result * window
            weight[region] += window
            done += 1
            if done % 5 == 0 or done == total:
                print(f"[SR] {done}/{total} tiles", flush=True)
    if np.any(weight <= 0):
        raise RuntimeError("Tiling left uncovered pixels")
    output /= weight
    return np.clip(output, 0, 255).astype(np.uint8)


def process_master_image(input_image_path, output_dir, prefix="master_image", model_path=None,
                         scale=4, tile_size=200, pad=20, smooth_bg=False, bg_mask=None,
                         download_model=False, model_url=DEFAULT_MODEL_URL, qa_box=None):
    if scale != 4:
        raise ValueError("This pipeline requires an x4 model; --scale must be 4")
    if not prefix or Path(prefix).name != prefix or prefix in {".", ".."}:
        raise ValueError("prefix must be a filename stem, not a path")
    tile_starts(1, tile_size, pad)
    with Image.open(input_image_path) as source:
        source = ImageOps.exif_transpose(source)
        rgba = source.convert("RGBA")
        if rgba.getchannel("A").getextrema()[0] < 255:
            raise ValueError("Transparent input requires an alpha-preserving image tool")
        img = np.array(source.convert("RGB"))[:, :, ::-1].copy()
    h, w = img.shape[:2]
    mask = None
    if smooth_bg:
        if not bg_mask:
            raise ValueError("Background smoothing requires an explicit --bg-mask")
        with Image.open(bg_mask) as source_mask:
            source_mask = ImageOps.exif_transpose(source_mask).convert("L")
            if source_mask.size != (w, h):
                raise ValueError("Background mask must have the same oriented dimensions as the input")
            mask = np.array(source_mask, dtype=np.float32) / 255.0
    model = ensure_model(model_path, download_model, model_url)
    import onnxruntime as ort
    session = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    print(f"[Model] {model}", flush=True)
    sr = neural_upscale(img, session, tile_size, pad)
    original_up = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
    lab_sr = cv2.cvtColor(sr, cv2.COLOR_BGR2LAB)
    lab_original = cv2.cvtColor(original_up, cv2.COLOR_BGR2LAB)
    lab_sr[:, :, 1:] = lab_original[:, :, 1:]
    master = cv2.cvtColor(lab_sr, cv2.COLOR_LAB2BGR)
    if mask is not None:
        mask = cv2.resize(mask, (w * scale, h * scale), interpolation=cv2.INTER_LINEAR)[:, :, None]
        smooth = cv2.bilateralFilter(original_up, 15, 25, 25)
        master = np.clip(master * (1 - mask * 0.5) + smooth * mask * 0.5, 0, 255).astype(np.uint8)
    image = Image.fromarray(master[:, :, ::-1])
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    paths = {}
    native = destination / f"{prefix}_sr.png"
    image.save(native, dpi=(300, 300))
    paths["sr_png"] = str(native)
    sizes = {}
    five_k = None
    for label, edge in [("4k", 3840), ("5k", 5120)]:
        ratio = edge / max(image.size)
        size = (max(1, round(image.width * ratio)), max(1, round(image.height * ratio)))
        exported = image.resize(size, Image.Resampling.LANCZOS)
        sizes[label] = {"width": size[0], "height": size[1], "interpolated_beyond_neural_output": ratio > 1}
        if ratio > 1:
            print(f"[Export] {label}: {size}, includes interpolation beyond neural x4 output", flush=True)
        for ext in ["png", "jpg"]:
            target = destination / f"{prefix}_{label}.{ext}"
            options = {"quality": 100, "subsampling": 0} if ext == "jpg" else {}
            exported.save(target, dpi=(300, 300), **options)
            paths[f"{label}_{ext}"] = str(target)
        if label == "5k":
            five_k = exported
    if qa_box is None:
        qa_box = (int(five_k.width * 0.1), int(five_k.height * 0.72),
                  max(1, int(five_k.width * 0.8)), max(1, int(five_k.height * 0.22)))
    x, y, cw, ch = qa_box
    if x < 0 or y < 0 or cw <= 0 or ch <= 0 or x + cw > five_k.width or y + ch > five_k.height:
        raise ValueError("qa-box must lie within the exported 5K image")
    crop = destination / f"{prefix}_100pct_macro_crop.png"
    five_k.crop((x, y, x + cw, y + ch)).save(crop, dpi=(300, 300))
    paths["crop_qa"] = str(crop)
    manifest = {"input": str(Path(input_image_path).resolve()), "input_size": [w, h],
                "model": model, "neural_size": list(image.size), "exports": sizes,
                "qa_box_xywh": list(qa_box), "background_smoothing": mask is not None,
                "notes": ["Lab chroma preservation is not a zero-color-shift guarantee.",
                          "JPEG is lossy; 300 DPI is metadata; original ICC profile is not retained."],
                "files": paths.copy()}
    manifest_path = destination / f"{prefix}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["manifest"] = str(manifest_path)
    print(json.dumps(paths, ensure_ascii=True, indent=2), flush=True)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", default="./output")
    parser.add_argument("--prefix", "-p", default="master_poster")
    parser.add_argument("--model", "-m")
    parser.add_argument("--scale", "-s", type=int, choices=[4], default=4)
    parser.add_argument("--tile-size", type=int, default=200)
    parser.add_argument("--pad", type=int, default=20)
    parser.add_argument("--bg-mask", help="Input-sized grayscale mask: white=background, black=preserve")
    parser.add_argument("--no-bg-smooth", action="store_true", help="Disable smoothing even when a mask is supplied")
    parser.add_argument("--download-model", action="store_true", help="Explicitly allow model download if missing")
    parser.add_argument("--model-url", default=DEFAULT_MODEL_URL)
    parser.add_argument("--qa-box", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    args = parser.parse_args()
    try:
        process_master_image(args.input, args.output, args.prefix, args.model, args.scale,
                             args.tile_size, args.pad, bool(args.bg_mask) and not args.no_bg_smooth,
                             args.bg_mask, args.download_model, args.model_url, args.qa_box)
    except (ValueError, FileNotFoundError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
