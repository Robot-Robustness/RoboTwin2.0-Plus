# RoboTwin 2.0-Plus: Robustness Testing via Structured Perturbations

> The official benchmark from **[Do World Action Models Generalize Better than VLAs? A Robustness Study](https://arxiv.org/abs/2603.22078)** — a structured perturbation suite for evaluating the robustness of Vision-Language-Action (VLA) and World Action Model (WAM) policies.

[![Paper](https://img.shields.io/badge/arXiv-2603.22078-b31b1b.svg)](https://arxiv.org/abs/2603.22078)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/perturbations-7%20dims%20%C2%B7%2021%20sub--dims-brightgreen)](#perturbation-taxonomy)

RoboTwin 2.0-Plus provides **7 structured perturbation dimensions (21 sub-dimensions)** — objects,
background, lighting, camera, robot state, language, and sensor noise — applied per episode
through declarative configs to measure how VLA/WAM policies degrade under distribution shift.
It is built on the RoboTwin 2.0 platform (two-arm Aloha-Agilex embodiment) and remains backward
compatible with it (see [Repository Structure](#repository-structure) for the lineage).

**Contents:** [Installation](#installation) · [Quick Start](#quick-start) ·
[Perturbation Taxonomy](#perturbation-taxonomy) · [Configs](#all-19-yaml-config-files) ·
[Repository Structure](#repository-structure) · [Contributing](CONTRIBUTING.md) ·
[Citing](#citation)

---

## Installation

RoboTwin 2.0-Plus uses the same environment as RoboTwin 2.0.

```bash
# 1. Clone
git clone https://github.com/markli1hoshipu/RoboTwin2.0-Plus.git
cd RoboTwin2.0-Plus

# 2. Create a Python 3.10 environment (conda recommended)
conda create -n RoboTwin python=3.10 -y
conda activate RoboTwin

# 3. Install dependencies (torch, sapien, mplib, curobo, pytorch3d, ...)
#    Takes ~20 min. See script/_install.sh for the exact steps it applies.
bash script/_install.sh

# 4. Download assets (embodiments, objects, background textures) from HuggingFace
bash script/_download_assets.sh
```

For the authoritative, step-by-step base install (including troubleshooting), see the
[RoboTwin 2.0 install guide](https://robotwin-platform.github.io/doc/usage/robotwin-install.html).
A GPU is required for data collection and evaluation.

> **Optional — policy baselines & description generation.** Training/evaluating the VLA
> baselines under `policy/` and running the LLM-based instruction generator in
> `description/` need extra dependencies and API keys (set via environment variables,
> e.g. `AZURE_API_KEY`). These are not required just to collect perturbed data.

---

## Perturbation Taxonomy

RoboTwin 2.0-Plus implements the same perturbation taxonomy as its sister benchmark
**[LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus)** — both are introduced in the same
paper. The taxonomy comprises **21 sub-dimensions across 7 perturbation dimensions** — the clean
(no-perturbation) baseline plus the 20 perturbation sub-dimensions listed below:

| Dimension | Sub-dims | Codes | Description |
|-----------|----------|-------|-------------|
| **Objects Layout** | 2 | O1, O2 | O1: confounding/distractor objects (117 object types); O2: target object pose perturbation |
| **Background Textures** | 2 | B1, B2 | B1: scene theme (950 curated textures); B2: surface/tabletop appearance |
| **Light Conditions** | 4 | L1-L4 | L1: diffuse color; L2: direction; L3: specular; L4: shadows |
| **Camera Viewpoints** | 3 | C1-C3 | C1: distance; C2: spherical position; C3: orientation |
| **Robot Initial States** | 1 | -- | Initial joint angle perturbation (std=0.1 rad, clip ±0.225 rad) |
| **Language Instructions** | 3 | R1-R3 | R1: distraction; R2: common sense rewording; R3: reasoning chain |
| **Sensor Noise** | 5 | N1-N5 | N1: motion blur; N2: gaussian blur; N3: zoom blur; N4: fog; N5: glass blur |

**Coverage: all 20 perturbation sub-dimensions implemented on the RoboTwin platform** — which,
together with the clean baseline, make up the 21-sub-dimension taxonomy reported in the paper.
C2 (camera spherical position) is disabled by default for simulation stability, leaving 19
perturbation sub-dimensions active out of the box.

---

## Quick Start

All data collection uses the same command pattern:

```bash
bash collect_data.sh <task_name> <config_name> <gpu_id>
```

- `<task_name>` — any of the 50 RoboTwin tasks (e.g. `beat_block_hammer`, `place_bread_basket`)
- `<config_name>` — a YAML config name from `task_config/` (without `.yml`)
- `<gpu_id>` — GPU index (e.g. `0`)

### Clean Baseline (no perturbation)

```bash
bash collect_data.sh beat_block_hammer demo_clean 0
```

### The 7 Perturbation Branches

Each branch corresponds to one LIBERO-Plus dimension. Run any of them individually:

| # | Branch | Command | What it tests |
|---|--------|---------|---------------|
| 1 | **Sensor Noise** (N1-N5) | `bash collect_data.sh beat_block_hammer demo_vision_noise 0` | Motion / gaussian / zoom blur, fog, glass blur — cycles one noise type per episode |
| 2 | **Lighting** (L1-L4) | `bash collect_data.sh beat_block_hammer demo_light 0` | Diffuse tint (always), direction + shadows (50%), specular (50%) — random mix per episode |
| 3 | **Camera** (C1+C3) | `bash collect_data.sh beat_block_hammer demo_camera 0` | Distance scaling + orientation; spherical position (C2) is disabled by default for stability |
| 4 | **Robot State** | `bash collect_data.sh beat_block_hammer demo_robot_state 0` | Initial joint angle noise (Gaussian, clipped) + gripper extremes |
| 5 | **Language** (R1+R2+R3) | `bash collect_data.sh beat_block_hammer demo_language_plus 0` | Distraction + common sense rewording + reasoning chain instructions |
| 6 | **Background** (B1+/B2) | `bash collect_data.sh beat_block_hammer demo_background_plus 0` | Wall/floor color tint + table surface material randomization |
| 7 | **Objects** (O1+/O2) | `bash collect_data.sh beat_block_hammer demo_objects_plus 0` | Variable distractor count (3-15) + target object pose noise |

### Language Sub-branch Ablations

For isolating individual language perturbation types:

```bash
# R1 only — distraction prefixes
bash collect_data.sh beat_block_hammer demo_language 0

# R2 only — common sense rewording
bash collect_data.sh beat_block_hammer demo_language_r2 0

# R3 only — reasoning chain / goal state description
bash collect_data.sh beat_block_hammer demo_language_r3 0
```

### Original Core Configs (single-dimension baselines)

These test individual dimensions without Plus enhancements:

```bash
bash collect_data.sh beat_block_hammer demo_background 0   # B1 texture swap only
bash collect_data.sh beat_block_hammer demo_objects 0      # O1 fixed 10 distractors
bash collect_data.sh beat_block_hammer demo_randomized 0   # Original full DR
```

### GPU Note

`collect_data.sh` requires a GPU. On a Slurm cluster, wrap in sbatch:

```bash
#!/bin/bash
#SBATCH --job-name=rtwplus_test
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --partition=compute

cd /path/to/RoboTwin2.0-Plus
bash collect_data.sh beat_block_hammer demo_background_plus 0
```

---

## What Each Config Does

### demo_clean.yml — Clean Baseline
No perturbation. Deterministic scene layout, default lighting, standard camera, original task instructions.

### demo_vision_noise.yml — Sensor Noise (N1-N5)
Applies one of 5 noise types per episode (cycled): motion blur, gaussian blur, zoom blur, fog, glass blur. Noise is injected into camera observations at render time.

### demo_light.yml — Lighting (L1-L4)
Randomly combines lighting perturbations per episode: L1 diffuse color tint (always on), L2 directional shift (linked to L4), L3 specular highlights (50% chance), L4 shadow manipulation (50% chance). Each episode gets a random mix of these modes.

### demo_camera.yml — Camera Viewpoints (C1 + C3; C2 disabled by default)
Perturbs the head-camera viewpoint per episode. **C1** scales distance (0.85–1.0×) and **C3** perturbs orientation (yaw/pitch/roll, 0–5°). **C2** (spherical azimuth/elevation, ±10°) is included in the config but ships with `enabled: false` for simulation stability — set `camera.c2.enabled: true` in `demo_camera.yml` to add it. Toggle any sub-dimension's `enabled` flag to isolate it.

### demo_robot_state.yml — Robot Initial State
Adds Gaussian noise to initial joint angles (configurable std and clip range) plus random gripper extreme positions.

### demo_language.yml — Language R1 (Distraction)
Wraps original task instructions in irrelevant conversational context (e.g., "Hey, before we start, could you please...").

### demo_language_plus.yml — Language R1+R2+R3 (Combined)
All three language perturbation types together:
- **R1**: Distraction wrapping (~30%)
- **R2**: Common sense rewording — replaces object names with functional descriptions, verb synonyms (~50%)
- **R3**: Reasoning chain — rewrites as goal-state / outcome description (~20%)

Uses 2,500 pre-generated instruction variants (50 tasks x 50 variants) in `description/task_instruction_plus/`.

### demo_language_r2.yml / demo_language_r3.yml — Language Ablations
R2-only or R3-only for isolating individual language perturbation effects.

### demo_background_plus.yml — Background (B1+/B2)
Goes beyond texture swaps:
- **B1+**: Random wall color tint + random floor color (not just texture IDs)
- **B2**: Table surface material randomization — metallic [0, 0.8], roughness [0.05, 0.95], color tint per channel

### demo_objects_plus.yml — Objects (O1+/O2)
Goes beyond fixed 10 distractors:
- **O1+**: Variable distractor count per episode (default 3-15)
- **O2**: Target object pose perturbation — Gaussian position noise (2cm std, x/y only) + yaw rotation (±15deg)

### demo_background.yml / demo_objects.yml — Original Baselines
Core single-dimension baselines (B1 texture swap only, O1 fixed 10 distractors). Useful for comparison against Plus versions.

### demo_randomized.yml — Original Full DR
Upstream RoboTwin domain randomization (texture swap + 10 distractors + random lighting). Does not include Plus features.

---

## All 19 YAML Config Files

All configs live in `task_config/`.

### Internal configs (5) — not runnable directly

| # | File | Purpose |
|---|------|---------|
| 1 | `_config_template.yml` | Template for creating new configs |
| 2 | `_camera_config.yml` | Camera hardware specs |
| 3 | `_embodiment_config.yml` | Robot asset paths |
| 4 | `_eval_step_limit.yml` | Step budgets per task |
| 5 | `camera_viewpoints.yaml` | Camera perturbation parameters for C1/C2/C3 |

### Runnable configs (14)

| # | File | Layer | Perturbation | Run for evaluation? |
|---|------|-------|-------------|---------------------|
| 6 | `demo_clean.yml` | Upstream | None (clean baseline) | **Yes — baseline** |
| 7 | `demo_randomized.yml` | Upstream | Original full DR (texture + 10 distractors + light) | No — legacy |
| 8 | `demo_vision_noise.yml` | Core | Sensor Noise N1-N5 | **Yes — Branch 1** |
| 9 | `demo_light.yml` | Core | Lighting L1-L4 | **Yes — Branch 2** |
| 10 | `demo_camera.yml` | Core | Camera C1+C3 (C2 off by default) | **Yes — Branch 3** |
| 11 | `demo_robot_state.yml` | Core | Robot initial state perturbation | **Yes — Branch 4** |
| 12 | `demo_language.yml` | Core | Language R1 only (distraction) | No — use `demo_language_plus` instead |
| 13 | `demo_background.yml` | Core | Background B1 only (texture swap) | No — use `demo_background_plus` instead |
| 14 | `demo_objects.yml` | Core | Objects O1 only (fixed 10 distractors) | No — use `demo_objects_plus` instead |
| 15 | **`demo_background_plus.yml`** | **Plus** | B1+ color tint + B2 surface material + floor | **Yes — Branch 5** |
| 16 | **`demo_objects_plus.yml`** | **Plus** | O1+ variable distractors (3-15) + O2 pose noise | **Yes — Branch 6** |
| 17 | **`demo_language_plus.yml`** | **Plus** | R1 + R2 + R3 combined | **Yes — Branch 7** |
| 18 | **`demo_language_r2.yml`** | **Plus** | R2 only (common sense rewording) | Optional ablation |
| 19 | **`demo_language_r3.yml`** | **Plus** | R3 only (reasoning chain) | Optional ablation |

### Summary: the 8 configs you need

To run a full LIBERO-Plus-style evaluation, use **1 baseline + 7 perturbation branches**:

```bash
# 0. Clean baseline
bash collect_data.sh <task> demo_clean 0

# 1. Sensor Noise (N1-N5)
bash collect_data.sh <task> demo_vision_noise 0

# 2. Lighting (L1-L4)
bash collect_data.sh <task> demo_light 0

# 3. Camera (C1+C3; C2 off by default)
bash collect_data.sh <task> demo_camera 0

# 4. Robot State
bash collect_data.sh <task> demo_robot_state 0

# 5. Background (B1+/B2)
bash collect_data.sh <task> demo_background_plus 0

# 6. Objects (O1+/O2)
bash collect_data.sh <task> demo_objects_plus 0

# 7. Language (R1+R2+R3)
bash collect_data.sh <task> demo_language_plus 0
```

Replace `<task>` with any of the 50 RoboTwin tasks (e.g. `beat_block_hammer`).

---

## Log Diagnostics

Each Plus feature prints diagnostics during data collection:

```
[B1+] Wall color tint: (0.72, 1.43, 0.55)
[B2]  Table surface: metallic=0.45, roughness=0.62, tint=(1.12, 0.88, 0.95)
[B1+] Floor color: (0.61, 0.42, 0.87)
[O1+] Placing 11 distractor objects (range 3-15)
[O2]  Perturbed 4 object poses (pos_std=0.020m, rot_max=15.0deg)
Episode noise: gaussian @ L2
  [R2] Episode 0: 25 commonsense variants
  [R3] Episode 0: 10 reasoning variants
```

---

## Repository Structure

This repo has 3 layered commits:

1. **Upstream RoboTwin v2.0** — original codebase
2. **Core perturbation extensions** — N1-N5, L1-L4, C1-C3, R1, robot init state
3. **RoboTwin 2.0-Plus** — B1+/B2 background, O1+/O2 objects, R2/R3 language

All changes are backward-compatible — existing configs work identically because new features only activate when their YAML keys are present.

> **Note on `policy/`.** The `policy/` directory (ACT, DP, DP3, RDT, pi0, OpenVLA-OFT,
> TinyVLA, DexVLA, …) is **inherited from RoboTwin 2.0** and vendors third-party VLA
> baselines, each under its own upstream license. RoboTwin 2.0-Plus does not modify these
> backends — they're kept so you can evaluate policies against the perturbed data. See
> [`NOTICE`](NOTICE) for the full lineage and per-component attribution.

### Key modified files (vs upstream)
| File | What changed |
|------|-------------|
| `envs/_base_task.py` | Sensor noise, lighting, camera, robot init (Core) + B1+/B2, O1+/O2 config parsing and dispatch (Plus) |
| `envs/camera/camera.py` | Camera ablation C1/C2/C3 support (Core) |
| `envs/utils/create_actor.py` | `create_table()` accepts `surface_params` for B2 material randomization (Plus) |
| `description/utils/generate_episode_instructions.py` | R1 distraction (Core) + R2/R3 dispatch (Plus) |

### Key new files
| File | Purpose |
|------|---------|
| `description/task_instruction_plus/*.json` | 50 files — pre-generated R1/R2/R3 instruction variants (2,500 total) |
| `task_config/demo_*_plus.yml` | Plus ablation configs |
| `task_config/demo_language_r2.yml` | R2-only ablation |
| `task_config/demo_language_r3.yml` | R3-only ablation |

---

## References

- **RoboTwin 2.0-Plus paper**: *Do World Action Models Generalize Better than VLAs? A Robustness Study* — https://arxiv.org/abs/2603.22078
- LIBERO-Plus paper: https://arxiv.org/abs/2510.13626
- LIBERO-Plus GitHub: https://github.com/sylvestf/LIBERO-plus
- RoboTwin 2.0: https://robotwin-platform.github.io/
- RoboTwin GitHub: https://github.com/TianxingChen/RoboTwin

---

## Authors

RoboTwin 2.0-Plus is developed by:

**Zhanguang Zhang**<sup>1\*</sup>, Zhiyuan Li<sup>1,2</sup>, Behnam Rahmati<sup>1</sup>,
Rui Heng Yang<sup>1</sup>, Yintao Ma<sup>1</sup>, Amir Rasouli<sup>1</sup>,
Sajjad Pakdamansavoji<sup>1</sup>, Yangzheng Wu<sup>1</sup>, Lingfeng Zhang<sup>1</sup>,
Tongtong Cao<sup>1</sup>, Feng Wen<sup>1</sup>, Xinyu Wang<sup>1</sup>,
Xingyue Quan<sup>1</sup>, and **Yingxue Zhang**<sup>1\*</sup>

<sup>1</sup> Huawei Technologies  ·  <sup>2</sup> University of Toronto

\* Corresponding authors: `zhanguang.zhang@huawei.com`, `yingxue.zhang@huawei.com`
Zhiyuan Li contributed during an internship at Huawei Canada.

---

## Citation

If you use RoboTwin 2.0-Plus, please cite our paper (see [`CITATION.cff`](CITATION.cff))
along with the upstream works it builds on:

```bibtex
@article{zhang2026worldaction,
  title   = {Do World Action Models Generalize Better than VLAs? A Robustness Study},
  author  = {Zhang, Zhanguang and Li, Zhiyuan and Rahmati, Behnam and Yang, Rui Heng and
             Ma, Yintao and Rasouli, Amir and Pakdamansavoji, Sajjad and Wu, Yangzheng and
             Zhang, Lingfeng and Cao, Tongtong and Wen, Feng and Wang, Xinyu and
             Quan, Xingyue and Zhang, Yingxue},
  journal = {arXiv preprint arXiv:2603.22078},
  year    = {2026}
}

@article{robotwin2,
  title   = {RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain
             Randomization for Robust Bimanual Robotic Manipulation},
  author  = {Chen, Tianxing and others},
  journal = {arXiv preprint arXiv:2506.18088},
  year    = {2025}
}
```

---

## License & Attribution

RoboTwin 2.0-Plus is released under the [MIT License](LICENSE). It is a derivative work of
RoboTwin 2.0; see [`NOTICE`](NOTICE) for full attribution, the three-layer lineage, and a
summary of modifications. Bundled baselines under `policy/` retain their own licenses.

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) and our
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
