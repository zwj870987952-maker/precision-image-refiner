# Precision Image Refiner 实战 Prompt 模版库

本目录记录了在商业个护产品（如 Kustie 洗护用品）实际精修过程中反复验证、效果最佳的提示词方案。

---

## 模版 1：1:1 原位死锁重绘（针对 AI 塑料假花假草替换）

适用场景：原图构图完美，但底层植物、石头是早期 AI 伪劣噪点或蜡质塑料感。

```text
Modify input_file_0.png with localized photorealistic inpainting and texture upgrade:

KEEP IDENTICAL (ABSOLUTE 1:1 COMPOSITION LOCK):
- Preserve the exact shapes, proportions, contours, typography, Chinese/English label characters, and positions of the product bottles standing in the center.
- Maintain the warm studio peach/apricot gradient background with radiant halo.
- Retain the exact compact island podium silhouette, the positions and count of the front small round pebbles, and the relative positions of the 3 flowers.
- ZERO newly added branches, twigs, or extra objects.

TEXTURE RECONSTRUCTION (HIGH-FREQUENCY PHOTOREALISM):
- Natural Velvet Moss: Replace fake turf with microscopic velvety forest star-moss, individual fuzzy moss strands, fine natural fibers, and damp organic soil depth.
- Authentic Mineral Rock: Natural weathered granite/limestone pedestal with crisp mineral facets, micro-pores, natural cracks, and realistic contact shadows.
- Clean Fresh Botanical Blooms: Soft, velvety matte petals with delicate cellular veining. ABSOLUTELY ZERO EXCESSIVE DEWDROPS (no dense water droplets). Clean, dry, pristine petals with natural curling edges.
- Golden Nectar Fluid: Clear, transparent, high-viscosity amber honey streaming down from the stone and pooling naturally on the tabletop surface.

Hasselblad medium format macro commercial product photography, 8k resolution, razor-sharp textures, zero hallucinated objects.
```

---

## 模版 2：参考图材质迁移（语义隔离防抄构图）

适用场景：用户提供了一张材质极佳的高清参考图（`input_file_1.png`），但参考图包含了无关杂物（如落叶、黑树枝、拉平地面）。

```text
Modify input_file_0.png referencing the tactile surface materials of input_file_1.png:

COMPOSITION (100% STRICTLY FROM input_file_0.png ONLY):
- The spatial layout, silhouettes, and positions must strictly follow input_file_0.png.
- DO NOT copy the wide flattened ground, black branches, or fallen petals from input_file_1.png!
- Preserve the isolated compact island base from input_file_0.png with clean smooth studio margins.
- Preserve the exact front row of small round pebbles from input_file_0.png.

SURFACE TEXTURES (TRANSFER MATERIAL PROPERTIES FROM input_file_1.png):
- Flowers: Match the dry, matte, clean velvety petals from input_file_1.png. Clean dry petals without heavy water droplets or spray.
- Moss: Match the dense, clumped, fuzzy velvety natural green moss from input_file_1.png.
- Stone: Match the hard, sharp mineral rock cleavage and rough texture from input_file_1.png.
- Fluid: Match the pure, clear amber liquid fluidity and glossy surface tension from input_file_1.png.

Ultra-high-definition macro commercial advertising photography, medium-format clarity, zero composition drift.
```
