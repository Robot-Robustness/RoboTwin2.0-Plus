# Contributing to RoboTwin 2.0-Plus

Thanks for your interest in improving RoboTwin 2.0-Plus! This project extends
[RoboTwin 2.0](https://github.com/TianxingChen/RoboTwin) with structured
perturbation categories for VLA robustness evaluation. Contributions of all
kinds are welcome — new perturbations, bug fixes, docs, and additional tasks.

## Getting set up

1. Follow the [Installation](README.md#installation) steps in the README.
2. Fork the repo and create a feature branch off `main`.
3. Verify your environment works with a clean baseline run:
   ```bash
   bash collect_data.sh beat_block_hammer demo_clean 0
   ```

## Adding or changing a perturbation

Perturbations are **config-driven and backward compatible** — a feature only
activates when its YAML key is present. When adding one:

- Put the dispatch logic in the relevant `envs/` module (see the
  "Key modified files" table in the README for where each dimension lives).
- Add a `task_config/demo_<name>.yml` config that enables it.
- Emit a short `[CODE]` diagnostic line during collection (see the
  "Log Diagnostics" section of the README) so users can confirm it fired.
- Document the new config in the README config tables.
- Confirm existing configs still run unchanged.

## Pull requests

- Keep PRs focused; one logical change per PR.
- Describe *what* the change tests/fixes and *how you verified it* (which
  task + config you ran, and what the diagnostics showed).
- Do not commit data, model weights, videos, or generated assets — these are
  covered by `.gitignore`.
- Do not commit API keys. `code_gen/` uses placeholder strings and the
  description pipeline reads keys from environment variables — keep it that way.

## Reporting issues

Use the issue templates under `.github/ISSUE_TEMPLATE/`. For bugs, please
include the exact `collect_data.sh` command, the task/config, your GPU/OS, and
the full traceback.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License, consistent with the rest of the project (see `LICENSE` and
`NOTICE`).
