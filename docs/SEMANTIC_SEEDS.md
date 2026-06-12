# Semantic Seeds

Each seed contains:

- `id`
- `name`
- `meaning`
- `compact`
- `expansion`
- `categories`
- `target_models`
- `priority`

## Usage

- Seed mapper selects seeds from extracted semantics.
- Safety seeds are mandatory when related constraints are detected.
- Different targets can prioritize different seed families.

## Safety Seeds

Seeds for `no_sudo`, `no_external_api`, `no_destructive_actions`, `stay_inside_root` are treated as hard constraints.
