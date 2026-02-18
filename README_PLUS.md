# RoboTwin-Plus: Robustness Testing via Structured Perturbations

> Extending RoboTwin with LIBERO-Plus-style perturbation categories
> Source: `/work/behnam/RoboTwin/` | Upstream: `/shared_work/markhsp/RoboTwin_repo/`
> Plus patches: `/shared_work/markhsp/robotwin_plus/`

---

## LIBERO-Plus Reference Taxonomy

LIBERO-Plus (arXiv: 2510.13626) defines **7 perturbation dimensions, 21 sub-dimensions**, and 5 difficulty levels for evaluating VLA robustness:

| Dimension | Sub-dims | Codes | Description |
|-----------|----------|-------|-------------|
| **Objects Layout** | 2 | O1, O2 | O1: confounding/distractor objects (416 unseen objects); O2: target object pose perturbation |
| **Background Textures** | 2 | B1, B2 | B1: scene theme (950 curated textures); B2: surface/tabletop appearance |
| **Light Conditions** | 4 | L1-L4 | L1: diffuse color; L2: direction; L3: specular; L4: shadows |
| **Camera Viewpoints** | 3 | C1-C3 | C1: distance; C2: spherical position; C3: orientation |
| **Robot Initial States** | 1 | -- | Initial joint angle perturbation (0.1-0.5 rad) |
| **Language Instructions** | 3 | R1-R3 | R1: distraction; R2: common sense rewording; R3: reasoning chain |
| **Sensor Noise** | 5 | N1-N5 | N1: motion blur; N2: gaussian blur; N3: zoom blur; N4: fog; N5: glass blur |

---

## RoboTwin-Plus Coverage Map

| LIBERO-Plus | Code | Status | Config File |
|-------------|------|--------|-------------|
| Sensor: Motion blur | N1 | DONE | `demo_vision_noise.yml` / `demo_vision_noise_plus.yml` |
| Sensor: Gaussian blur | N2 | DONE | `demo_vision_noise.yml` / `demo_vision_noise_plus.yml` |
| Sensor: Zoom blur | N3 | DONE | `demo_vision_noise.yml` / `demo_vision_noise_plus.yml` |
| Sensor: Fog | N4 | DONE | `demo_vision_noise.yml` / `demo_vision_noise_plus.yml` |
| Sensor: Glass blur | N5 | DONE | `demo_vision_noise.yml` / `demo_vision_noise_plus.yml` |
| Light: Diffuse tint | L1 | DONE | `demo_light.yml` |
| Light: Direction | L2 | DONE | `demo_light.yml` |
| Light: Specular | L3 | DONE | `demo_light.yml` |
| Light: Shadows | L4 | DONE | `demo_light.yml` |
| Camera: Distance | C1 | DONE | `demo_camera.yml` |
| Camera: Spherical | C2 | DONE | `demo_camera.yml` |
| Camera: Orientation | C3 | DONE | `demo_camera.yml` |
| Robot initial state | -- | DONE | `demo_robot_state.yml` |
| Language: Distraction | R1 | **DONE** | `demo_language.yml` / `demo_language_plus.yml` |
| Language: Common sense | R2 | **DONE** | `demo_language_r2.yml` / `demo_language_plus.yml` |
| Language: Reasoning chain | R3 | **DONE** | `demo_language_r3.yml` / `demo_language_plus.yml` |
| Objects: Confounders | O1 | **DONE (enhanced)** | `demo_objects_plus.yml` |
| Objects: Target pose | O2 | **DONE** | `demo_objects_plus.yml` |
| Background: Scene theme | B1 | **DONE (enhanced)** | `demo_background_plus.yml` |
| Background: Surface | B2 | **DONE** | `demo_background_plus.yml` |

**Summary: 21/21 LIBERO-Plus sub-dimensions fully implemented.**

---

## Deployment

The plus patches are **drop-in replacements** that sit on top of Behnam's existing code. All changes are backward-compatible — existing configs work identically because new features only activate when their YAML keys are present.

### Install

```bash
# 1. Back up originals
cp /work/behnam/RoboTwin/envs/_base_task.py /work/behnam/RoboTwin/envs/_base_task.py.bak
cp /work/behnam/RoboTwin/envs/utils/create_actor.py /work/behnam/RoboTwin/envs/utils/create_actor.py.bak
cp /work/behnam/RoboTwin/description/utils/generate_episode_instructions.py /work/behnam/RoboTwin/description/utils/generate_episode_instructions.py.bak

# 2. Replace patched files (backward-compatible)
cp /shared_work/markhsp/robotwin_plus/envs/_base_task.py /work/behnam/RoboTwin/envs/
cp /shared_work/markhsp/robotwin_plus/envs/utils/create_actor.py /work/behnam/RoboTwin/envs/utils/
cp /shared_work/markhsp/robotwin_plus/description/generate_episode_instructions.py /work/behnam/RoboTwin/description/utils/

# 3. Add new YAML configs
cp /shared_work/markhsp/robotwin_plus/task_config/demo_*_plus.yml /work/behnam/RoboTwin/task_config/
cp /shared_work/markhsp/robotwin_plus/task_config/demo_language_r2.yml /work/behnam/RoboTwin/task_config/
cp /shared_work/markhsp/robotwin_plus/task_config/demo_language_r3.yml /work/behnam/RoboTwin/task_config/

# 4. Add pre-generated R2/R3 instruction variants (50 tasks x 50 variants)
cp -r /shared_work/markhsp/robotwin_plus/description/task_instruction_plus/ /work/behnam/RoboTwin/description/task_instruction_plus/
```

### Test the new configs

```bash
cd /work/behnam/RoboTwin

# Background Plus (B1+ color tint / B2 surface material / floor)
bash collect_data.sh beat_block_hammer demo_background_plus 0

# Objects Plus (O1+ variable distractor count / O2 target pose noise)
bash collect_data.sh beat_block_hammer demo_objects_plus 0

# Sensor Noise Plus (gentler L1-L2 severity)
bash collect_data.sh beat_block_hammer demo_vision_noise_plus 0

# Language Plus — all R1+R2+R3 together
bash collect_data.sh beat_block_hammer demo_language_plus 0

# Language R2 only (common sense rewording)
bash collect_data.sh beat_block_hammer demo_language_r2 0

# Language R3 only (reasoning chain / goal state)
bash collect_data.sh beat_block_hammer demo_language_r3 0
```

### Verify existing configs still work (regression)

```bash
bash collect_data.sh beat_block_hammer demo_clean 0
bash collect_data.sh beat_block_hammer demo_randomized 0
bash collect_data.sh beat_block_hammer demo_vision_noise 0
bash collect_data.sh beat_block_hammer demo_language 0
```

### What to look for in logs

Each new feature prints diagnostics:
```
[B1+] Wall color tint: (0.72, 1.43, 0.55)
[B2]  Table surface: metallic=0.45, roughness=0.62, tint=(1.12, 0.88, 0.95)
[B1+] Floor color: (0.61, 0.42, 0.87)
[O1+] Placing 11 distractor objects (range 3-15)
[O2]  Perturbed 4 object poses (pos_std=0.020m, rot_max=15.0deg)
[Sensor Noise] gaussian @ L1 (s=0.00)
  [R2] Episode 0: 25 commonsense variants
  [R3] Episode 0: 10 reasoning variants
```

### Note on GPU

`collect_data.sh` needs a GPU. On the cluster, wrap in sbatch:

```bash
#!/bin/bash
#SBATCH --job-name=rtwplus_test
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --qos=high
#SBATCH --output=/shared_work/markhsp/logs/rtwplus_test_%j.out

export HF_HOME=/shared_work/markhsp/.cache/huggingface
export UV_CACHE_DIR=/shared_work/markhsp/.cache/uv
export PIP_CACHE_DIR=/shared_work/markhsp/.cache/pip
export XDG_CACHE_HOME=/shared_work/markhsp/.cache

cd /work/behnam/RoboTwin
bash collect_data.sh beat_block_hammer demo_background_plus 0
bash collect_data.sh beat_block_hammer demo_objects_plus 0
bash collect_data.sh beat_block_hammer demo_vision_noise_plus 0
bash collect_data.sh beat_block_hammer demo_language_plus 0
```

---

## What the Plus Configs Add (vs Original RoboTwin)

### 1. Background Plus (B1+ / B2) — `demo_background_plus.yml`

Goes beyond `demo_randomized.yml` which only swaps textures from a fixed pool.

| Feature | Original `demo_randomized` | **RoboTwin-Plus** |
|---------|---------------------------|-------------------|
| Wall texture | Random swap from seen/unseen pool | Same **+ random color tint** [0.4, 1.8] per RGB channel |
| Table surface | Same texture swap as wall | **B2: Material randomization** — metallic [0, 0.8], roughness [0.05, 0.95], color tint |
| Floor | Not touched | **Random floor color** [0.3, 1.0] per channel |

**Code**: `_base_task.py` lines 541-590, `create_actor.py` (create_table with `surface_params`)
**YAML keys**: `domain_randomization.background_plus.{enabled, color_tint, tint_range, surface_material, metallic_range, roughness_range, floor_texture}`

### 2. Objects Plus (O1+ / O2) — `demo_objects_plus.yml`

Goes beyond `demo_objects.yml` which just sets `cluttered_table: true` (fixed 10 objects, no pose noise).

| Feature | Original `demo_randomized` | **RoboTwin-Plus** |
|---------|---------------------------|-------------------|
| Distractor count | Fixed 10 | **Random 3-15** per episode (configurable) |
| Target object pose | Static (as loaded) | **O2: Gaussian position noise** (2cm std) + **yaw rotation** (+/-15deg) |

**Code**: `_base_task.py` lines 282-297 (O1+ dispatch), 597-634 (O2 method `_apply_target_pose_perturbation`)
**YAML keys**: `domain_randomization.object_plus.{enabled, distractor_min, distractor_max, target_pose_perturbation.{enabled, position_std, rotation_max_deg}}`

**O2 details**: Perturbs all task-relevant actors (skips table/wall/ground/robot links). Position noise is x,y only (keeps z to avoid floating/clipping). Rotation is yaw-only (avoids tipping objects over).

### 3. Sensor Noise Plus (N1-N5 gentler) — `demo_vision_noise_plus.yml`

Same 5 noise types but with reduced severity so images stay recognizable.

| Noise | Original max (L2, s=0.25) | **Plus max** (L1-L2, s=0-0.25) | Reduction |
|-------|--------------------------|--------------------------------|-----------|
| N1 Motion | kernel 6, sigma 2.75 | kernel **3**, sigma **1.6** | ~40% less |
| N2 Gaussian | sigma 3.25 | sigma **1.6** | ~50% less |
| N3 Zoom | 1.22x | **1.09x** | ~60% less |
| N4 Fog | alpha 0.6 | alpha **0.35** | ~40% less |
| N5 Glass | sigma 1.0, delta 2 | sigma **0.6**, delta **1** | ~40% less |

**Key change**: Severity is now **YAML-configurable** via `sensor_noise_severity_min` / `sensor_noise_severity_max`. Default (when keys absent) matches Behnam's original behavior (always L2) for backward compatibility.

### 4. Language Plus (R1 + R2 + R3) — `demo_language_plus.yml`

Goes beyond `demo_language.yml` which only has R1 (distraction prefixes). Adds R2 and R3 following LIBERO-Plus taxonomy.

| Type | What it does | Example |
|------|-------------|---------|
| **R1 Distraction** | Wraps instruction in irrelevant conversational context | "Hey, before we start, could you please pick up {A} and strike the block." |
| **R2 Common Sense** | Replaces object names with functional descriptions, verb synonyms | "Seize the striking tool {A} with {a} and apply force to the rectangular solid." |
| **R3 Reasoning Chain** | Rewrites as goal-state / outcome description | "Ensure the block has been struck using {A} held by {a}." |

**Pre-generated variants**: 50 tasks x 50 variants each = **2,500 total instructions**
- 15 R1 (distraction) per task
- 25 R2 (common sense rewording) per task
- 10 R3 (reasoning chain / goal state) per task

Distribution follows LIBERO-Plus (~50% R2, ~30% R1, ~20% R3).

**Instruction variants preserve placeholders** (`{A}`, `{B}`, `{a}`, etc.) so they get instantiated with concrete object descriptions at runtime, just like the original templates.

**YAML configs**:
- `demo_language_plus.yml` — all R1+R2+R3 generated together (`language.mode: language_plus`)
- `demo_language_r2.yml` — R2-only ablation (`language.mode: r2`)
- `demo_language_r3.yml` — R3-only ablation (`language.mode: r3`)

**Code**: `generate_episode_instructions.py` — added `load_plus_instructions()`, R2/R3 dispatch in `generate_episode_descriptions()`, fixed `perturb_mode` bug in `__main__`

---

## Patched Files

All in `/shared_work/markhsp/robotwin_plus/`:

| File | What changed |
|------|-------------|
| `envs/_base_task.py` | B1+/B2 background (lines 156-164, 541-590), O1+/O2 objects (lines 166-174, 282-297, 597-634), sensor noise severity config + reduced params (lines 81-96, 801-916) |
| `envs/utils/create_actor.py` | `create_table()` accepts `surface_params` dict for B2 material randomization |
| `description/generate_episode_instructions.py` | R2/R3 dispatch using pre-generated variants, `load_plus_instructions()`, `save_episode_descriptions()` saves R2/R3 keys, fixed `perturb_mode` bug |
| `description/task_instruction_plus/*.json` | **50 files** — pre-generated R1/R2/R3 instruction variants (2,500 total) |
| `task_config/demo_background_plus.yml` | B1+/B2 ablation config |
| `task_config/demo_objects_plus.yml` | O1+/O2 ablation config |
| `task_config/demo_vision_noise_plus.yml` | Gentler N1-N5 with severity_min=1, severity_max=2 |
| `task_config/demo_language_plus.yml` | R1+R2+R3 combined language perturbation |
| `task_config/demo_language_r2.yml` | R2-only (common sense rewording) ablation |
| `task_config/demo_language_r3.yml` | R3-only (reasoning chain) ablation |

---

## Full YAML Inventory

**Total: 20 configs** (6 original + 8 Behnam + 6 plus)

### Original/Upstream (6)
| File | Type |
|------|------|
| `_embodiment_config.yml` | Internal — robot asset paths |
| `_camera_config.yml` | Internal — camera specs |
| `_config_template.yml` | Internal — template |
| `_eval_step_limit.yml` | Internal — step budgets |
| `demo_clean.yml` | Baseline (modified by Behnam) |
| `demo_randomized.yml` | Original full DR |

### Added by Behnam (8)
| File | Perturbation |
|------|-------------|
| `demo_vision_noise.yml` | Sensor Noise N1-N5 |
| `demo_light.yml` | Lighting L1-L4 |
| `demo_camera.yml` | Camera C1-C3 |
| `camera_viewpoints.yaml` | Camera params |
| `demo_robot_state.yml` | Robot init state |
| `demo_language.yml` | Language R1 |
| `demo_background.yml` | Background B1 only |
| `demo_objects.yml` | Objects O1 (same as randomized) |

### Added by RoboTwin-Plus (6)
| File | What's new vs original |
|------|----------------------|
| `demo_background_plus.yml` | B1+ color tint + B2 surface material + floor color |
| `demo_objects_plus.yml` | O1+ variable distractor count + O2 target pose noise |
| `demo_vision_noise_plus.yml` | Configurable severity, gentler L1-L2 defaults |
| `demo_language_plus.yml` | R1+R2+R3 combined language perturbation |
| `demo_language_r2.yml` | R2-only common sense rewording |
| `demo_language_r3.yml` | R3-only reasoning chain / goal state |

### Runnable ablation configs: 15
`demo_clean`, `demo_randomized`, `demo_vision_noise`, `demo_light`, `demo_camera`, `demo_robot_state`, `demo_language`, `demo_background`, `demo_objects`, **`demo_background_plus`**, **`demo_objects_plus`**, **`demo_vision_noise_plus`**, **`demo_language_plus`**, **`demo_language_r2`**, **`demo_language_r3`**

---

## Merging on a Local Machine

The plus patches are self-contained. To merge with Behnam's repo locally:

```
your_local_robotwin/                      # Behnam's original repo
├── envs/
│   ├── _base_task.py                     ← REPLACE with robotwin_plus/envs/_base_task.py
│   └── utils/
│       └── create_actor.py               ← REPLACE with robotwin_plus/envs/utils/create_actor.py
├── description/
│   ├── utils/
│   │   └── generate_episode_instructions.py  ← REPLACE with robotwin_plus/description/generate_episode_instructions.py
│   └── task_instruction_plus/            ← NEW DIRECTORY (copy entire folder)
│       ├── adjust_bottle.json
│       ├── beat_block_hammer.json
│       └── ... (50 files total)
└── task_config/
    ├── demo_background_plus.yml          ← NEW
    ├── demo_objects_plus.yml             ← NEW
    ├── demo_vision_noise_plus.yml        ← NEW
    ├── demo_language_plus.yml            ← NEW
    ├── demo_language_r2.yml              ← NEW
    └── demo_language_r3.yml              ← NEW
```

All replacements are backward-compatible — existing configs (demo_clean, demo_randomized, etc.) work identically because new features only activate when their YAML keys are present.

---

## Behnam's Original Modifications vs Upstream RoboTwin

### Modified files (from upstream)

**`envs/_base_task.py`** — all perturbation logic:
- Sensor noise setup + application in `get_obs()` (N1-N5)
- Lighting ablation (L1-L4) in `setup_scene()`
- Camera viewpoint perturbation (C1-C3) after camera load
- Robot initial state randomization

**`description/utils/generate_episode_instructions.py`**:
- `make_r1_distraction()` function + `perturb` parameter

**`task_config/demo_clean.yml`** — modified from upstream:
- NOTE: Has drifted — now has `random_head_camera_dis: 0.15` and `language.mode: r1`

### Object Perturbation: demo_objects.yml vs demo_randomized.yml

Original `demo_objects.yml` uses the **exact same** `get_cluttered_table()` as `demo_randomized.yml` (fixed 10 objects, same pool). It's just an isolation — everything else disabled.

`demo_objects_plus.yml` goes further: variable 3-15 distractors + O2 target pose perturbation.

---

## References

- LIBERO-Plus paper: https://arxiv.org/abs/2510.13626
- LIBERO-Plus GitHub: https://github.com/sylvestf/LIBERO-plus
- RoboTwin 2.0: https://robotwin-platform.github.io/
- RoboTwin GitHub: https://github.com/TianxingChen/RoboTwin
