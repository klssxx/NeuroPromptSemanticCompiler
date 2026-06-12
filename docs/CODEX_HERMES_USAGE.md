# Codex and Hermes Usage

1. Run compiler with `--level all` and your target.
2. Review `context_loss_report.md`.
3. Use `optimized_prompt.txt` for target execution.
4. If critical losses exist, move to safe mode.

## Level Choice

- `safe`: higher preservation, lower compression risk.
- `balanced`: default, best tradeoff.
- `aggressive`: compactest, requires human review.

## Inspection Checklist

- `chosen_compilation.nsl`
- `optimized_prompt.txt`
- `reconstructed_prompt.txt`
- `context_loss_report.md`
