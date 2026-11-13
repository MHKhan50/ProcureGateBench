# Build verification record

**Verification date:** 13 November 2026

Checks completed in the build environment:

- Python source compiled with `compileall`.
- Package installed in editable mode with `--no-build-isolation --no-deps`.
- Unit and integration tests: 12 passed, 0 failed.
- Full 96-case deterministic CLI runs completed for `rule`, `flat`, and `risk-only` agents.
- Synthetic generator produced 96 scenario rows and 96 separate label rows across 16 paired hard-gate groups.

The local Ollama adapter was not executed against a live model during package verification. Its response parser was unit-tested. Python 3.9 compatibility is maintained in source syntax and declared metadata, but this build environment ran Python 3.13.5; a separate Python 3.9 runtime check remains advisable.

The deterministic baseline metrics are software sanity checks on synthetic cases, not empirical LLM findings. In particular, the gate-aware rule baseline is policy-aligned by construction.
