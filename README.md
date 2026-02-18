# RoboTwin-Plus: Robustness Testing via Structured Perturbations

> Extending [RoboTwin 2.0](https://github.com/TianxingChen/RoboTwin) with [LIBERO-Plus](https://arxiv.org/abs/2510.13626)-style perturbation categories for evaluating VLA robustness.

---

## LIBERO-Plus Reference Taxonomy

LIBERO-Plus defines **7 perturbation dimensions, 21 sub-dimensions**, and 5 difficulty levels:

| Dimension | Sub-dims | Codes | Description |
|-----------|----------|-------|-------------|
| **Objects Layout** | 2 | O1, O2 | O1: confounding/distractor objects (117 object types); O2: target object pose perturbation |
| **Background Textures** | 2 | B1, B2 | B1: scene theme (950 curated textures); B2: surface/tabletop appearance |
| **Light Conditions** | 4 | L1-L4 | L1: diffuse color; L2: direction; L3: specular; L4: shadows |
| **Camera Viewpoints** | 3 | C1-C3 | C1: distance; C2: spherical position; C3: orientation |
| **Robot Initial States** | 1 | -- | Initial joint angle perturbation (std=0.1 rad, clip ±0.225 rad) |
| **Language Instructions** | 3 | R1-R3 | R1: distraction; R2: common sense rewording; R3: reasoning chain |
| **Sensor Noise** | 5 | N1-N5 | N1: motion blur; N2: gaussian blur; N3: zoom blur; N4: fog; N5: glass blur |

**Coverage: 21/21 LIBERO-Plus sub-dimensions fully implemented.**

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
| 3 | **Camera** (C1+C2+C3) | `bash collect_data.sh beat_block_hammer demo_camera 0` | Distance + spherical position + orientation (combined; LIBERO-Plus tests each independently) |
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

### Original Behnam Configs (single-dimension baselines)

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

cd /path/to/robotwin-plus
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

### demo_camera.yml — Camera Viewpoints (C1+C2+C3 combined)
Applies all three camera perturbations together per episode: C1 scales distance (0.5-1.0x), C2 shifts spherical position (azimuth/elevation up to ±25°), C3 perturbs orientation (yaw/pitch/roll within 1-5°). Note: LIBERO-Plus tests C1, C2, C3 independently; this config applies them combined. To isolate a single sub-dimension, edit `demo_camera.yml` and set the other two to `enabled: false`.

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
Behnam's single-dimension baselines (B1 texture swap only, O1 fixed 10 distractors). Useful for comparison against Plus versions.

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
| 8 | `demo_vision_noise.yml` | Behnam | Sensor Noise N1-N5 | **Yes — Branch 1** |
| 9 | `demo_light.yml` | Behnam | Lighting L1-L4 | **Yes — Branch 2** |
| 10 | `demo_camera.yml` | Behnam | Camera C1-C3 | **Yes — Branch 3** |
| 11 | `demo_robot_state.yml` | Behnam | Robot initial state perturbation | **Yes — Branch 4** |
| 12 | `demo_language.yml` | Behnam | Language R1 only (distraction) | No — use `demo_language_plus` instead |
| 13 | `demo_background.yml` | Behnam | Background B1 only (texture swap) | No — use `demo_background_plus` instead |
| 14 | `demo_objects.yml` | Behnam | Objects O1 only (fixed 10 distractors) | No — use `demo_objects_plus` instead |
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

# 3. Camera (C1-C3)
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
2. **Behnam's perturbation extensions** — N1-N5, L1-L4, C1-C3, R1, robot init state
3. **RoboTwin-Plus** — B1+/B2 background, O1+/O2 objects, R2/R3 language

All changes are backward-compatible — existing configs work identically because new features only activate when their YAML keys are present.

### Key modified files (vs upstream)
| File | What changed |
|------|-------------|
| `envs/_base_task.py` | Sensor noise, lighting, camera, robot init (Behnam) + B1+/B2, O1+/O2 config parsing and dispatch (Plus) |
| `envs/camera/camera.py` | Camera ablation C1/C2/C3 support (Behnam) |
| `envs/utils/create_actor.py` | `create_table()` accepts `surface_params` for B2 material randomization (Plus) |
| `description/utils/generate_episode_instructions.py` | R1 distraction (Behnam) + R2/R3 dispatch (Plus) |

### Key new files
| File | Purpose |
|------|---------|
| `description/task_instruction_plus/*.json` | 50 files — pre-generated R1/R2/R3 instruction variants (2,500 total) |
| `task_config/demo_*_plus.yml` | Plus ablation configs |
| `task_config/demo_language_r2.yml` | R2-only ablation |
| `task_config/demo_language_r3.yml` | R3-only ablation |

---

## References

- LIBERO-Plus paper: https://arxiv.org/abs/2510.13626
- LIBERO-Plus GitHub: https://github.com/sylvestf/LIBERO-plus
- RoboTwin 2.0: https://robotwin-platform.github.io/
- RoboTwin GitHub: https://github.com/TianxingChen/RoboTwin
