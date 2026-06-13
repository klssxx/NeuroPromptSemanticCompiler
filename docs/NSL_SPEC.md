# NSL v0.1 Formal Spec

## Grammar-like Shape

```text
document   := header newline fields
header     := "NSL/0.1"
fields     := field (newline field)*
field      := KEY "=" VALUE
KEY        := [A-Z_][A-Z0-9_]*
VALUE      := any_text_without_newline
```

## Canonical Fields

`ID TARGET R G CTX T C P TOOLS IN OUT STYLE RISKS SEEDS VERIFY`

## Separator Semantics

- `;` concept groups (dense semantic groups)
- `,` task/style/tool items
- `>` priority ordering chain

## Safety Rule

If present in source context, these constraints must survive compilation:

- `no_sudo`
- `no_external_api`
- `no_destructive_actions`
- `stay_inside_project_root`

## Balanced Example

```text
NSL/0.1
ID=run_x1
TARGET=codex
R=senior_ai_tool_builder
G=create_local_semantic_prompt_compiler
CTX=ubuntu;python;local_first;offline
T=extract_semantics,map_seeds,compile_nsl,reconstruct,verify_loss,export_reports,test_cli
C=no_sudo,no_external_api,no_destructive_actions,stay_inside_project_root
P=safety>semantic_preservation>working_mvp>clarity>compression
OUT=cli,files,tests,reports,optimized_prompt
SEEDS=S001,S010,S024,S033,S058,S084
VERIFY=context_loss,critical_constraints,unit_tests
```
