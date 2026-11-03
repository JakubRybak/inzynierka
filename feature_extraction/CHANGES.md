# Changes to shared files

Configs for Jackets & Coats (5 categories), Pants (4) and Shirts & Blouses (2) needed a few additions to the shared
files. Existing configs behave as before, except for the `shell` section in `main_composition`.

## keywords/engine.py, keywords/composition.py

New options, all optional:

| Option | Strategies | Meaning |
| --- | --- | --- |
| `priority` | new strategy | the first value, in keyword order, that has a match (Jeans `distressing`) |
| `default_value` | `single`, `priority`, `composition` | value assigned when nothing else resolved the feature (Jackets & Coats `fit`: `Regular`) |
| `section_only` | `composition` | parse only a section from `main_sections`; text before the first label is ignored; no such section → status `no_section` |
| `fallback` | `composition` | rule evaluated when there was nothing to parse (empty column or no section) |

The shared schema must include all possible outputs, including `default_value` and the values of `fallback`.

## keywords/definitions/common.yaml

- `main_composition`: `shell` added to `main_sections`. A composition with one `Shell:` section is now parsed;
  `Shell:` together with `Body:` stays `ambiguous_main_section`. Assigned compositions: Jackets & Coats +735,
  Trousers +81, Skirts +85, Dresses +58, Tank tops +19, T-shirts +12, others ≤ 15.
- `lining_composition` (new, used by Jackets & Coats): the `Lining` / `Lining N` / `Body lining` section parsed like
  `main_composition` (`section_only`, same materials through the `&materials` anchor). Without the section, `unlined` in
  the description gives `Unlined` (`fallback`); otherwise `Unknown` (`default_value`).

## tests/test_keywords.py

- `test_supported_scope` lists the 17 categories; `product()` takes the section from the config.
- `test_composition`: `Shell: 100% cotton.` is now assigned; `Shell` + `Body` is the ambiguous case.
- New: `test_lining_composition`, `test_default_value`, `test_priority`, `test_excluded_phrases`.

## docs/extraction_rules

- `common/main_composition.md`: the tree mentions Shell.
- `main_composition` tables recomputed after the `shell` change, also in `dresses`, `skirts`, `tops/t-shirts` and
  `tops/tank-tops-and-camisoles`.

## Shared feature contracts

Feature types, values and constraints now live in `schema/`, independently of
keyword extraction. Keyword `strategy` specifies matching/parsing behavior only.
LLM-only fields have no keyword rule, replacing the old `llm` strategy and empty
multi-choice keyword definitions. Missing fields still receive metadata and stay
unresolved until LLM extraction; their keyword strategy is `null`.

`validation.py` is shared by keyword extraction, reference checks and LLM result
validation. Color limits, composition totals, standalone values and cross-feature
dependencies come from the schema. The prompt builder and reference bank no longer
load keyword definitions. Run fingerprints include schema YAML files; use a new run
name after this migration. Historical artifacts are retained unchanged.
