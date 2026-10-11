# Contributing

Thanks for helping improve AI Marketing Squad.

1. Create a focused branch for each change.
2. Install development dependencies with `python -m pip install -e ".[dev]"`.
3. Add or update tests for behavior changes; do not rely only on a successful live-model run.
4. Run `pytest` and `ruff check .` before submitting.
5. Never commit credentials, private campaign data, or outputs that contain sensitive information.
6. Clearly label any metrics as measured, estimated, or not yet measured.

Changes to agent prompts should explain the failure mode they address and, when practical, include an evaluation case.
