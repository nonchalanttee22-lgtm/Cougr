# Example Quality Standard

This document defines the minimum quality bar that every project under `examples/` must satisfy before being considered a professional reference. Future cleanup issues should use the [checklist at the end](#quality-checklist) to track progress example by example.

## Purpose

Examples are the primary onboarding surface for external developers building games with `cougr-core` on Stellar/Soroban. They must be self-contained, buildable without access to the internal monorepo, and explicit about which Cougr pattern they demonstrate. A reader should be able to clone the repo, `cd` into any example, follow its README, and have a working Soroban contract in minutes.

---

## 1. Dependency Requirements

Every example must declare `cougr-core` using the published crate on crates.io, **not** a local path dependency.

```toml
# Correct
[dependencies]
cougr-core = "1.0"
soroban-sdk = "25.1.0"

# Wrong — breaks for external users
[dependencies]
cougr-core = { path = "../../" }
```

Path dependencies silently work inside the monorepo but fail for any developer who installs the example independently. The published crate is the contract.

---

## 2. Required Validation Commands

Every example must pass both of the following commands without errors or warnings:

```bash
cargo test
stellar contract build
```

`cargo test` validates the game logic in the Soroban test environment. `stellar contract build` validates that the contract compiles to a valid WASM artifact using the Stellar toolchain. A Rust crate that compiles with `cargo build` but fails `stellar contract build` is not a valid Soroban contract.

CI workflows for each example should run both commands on every push to `main` and `develop`.

---

## 3. Module Structure

The source layout of every example should reflect the separation of concerns that Cougr encourages. Monolithic `lib.rs` files are acceptable only for the simplest two- or three-system examples; anything more complex must be split.

### Minimum layout

```
examples/<name>/
├── Cargo.toml
├── README.md
└── src/
    ├── lib.rs          # Contract entrypoints, #[contract] impl, GameApp wiring
    ├── components.rs   # Cougr components (impl_component! types)
    └── systems.rs      # Game systems registered with GameApp
```

### Extended layout (use when applicable)

| File | When to add |
|---|---|
| `types.rs` | Domain enums or structs shared across modules but not Cougr components |
| `auth.rs` | Session key setup, `CougrAccount` wiring, multi-device logic |
| `privacy.rs` | Commit-reveal flows, Merkle proof helpers, hidden-state management |
| `zk.rs` | Groth16 / BLS proof submission and verification wrappers |

Do not add files that are not used. Do not collapse `components.rs` and `systems.rs` back into `lib.rs` once they exist.

---

## 4. README Requirements

Every example must have a `README.md` that covers all of the following sections. Keep each section concise; depth belongs in inline code comments, not in the README.

| Section | Required content |
|---|---|
| **Purpose and pattern** | One paragraph: what game mechanic does this demonstrate and which Cougr pattern does it showcase? |
| **Public contract API** | A table or list of every `#[contractimpl]` function: name, parameters, return type, one-line description |
| **Architecture overview** | How systems, components, and the `GameApp` tick interact. A short prose description or ASCII diagram |
| **Storage model** | What is stored in instance storage vs persistent storage vs temporary storage, and why |
| **Main gameplay flow** | Step-by-step description of one complete game round, from initialization to terminal state |
| **Cougr APIs used** | Which modules from `cougr-core` are imported and why (ECS, scheduler, ZK, auth, standards) |
| **Build and test commands** | The exact commands: `cargo test` and `stellar contract build` |
| **Known limitations** | Anything intentionally simplified or out of scope for this example |

Avoid embedding hardcoded contract IDs, testnet addresses, or deployment results in the README. Those belong in a local `NOTES.md` or a developer's own notes.

---

## 5. Testing Requirements

Each example must have a test module (typically `src/lib.rs` inline tests or `src/test.rs`) that covers the following categories:

| Category | What to test |
|---|---|
| **Initialization** | Calling the init function produces valid starting state |
| **Happy-path gameplay** | One full game round proceeds without errors |
| **Invalid actions** | Illegal moves, out-of-turn actions, or bad input return the expected error |
| **Rule and invariant tests** | Game-specific invariants hold after any sequence of valid moves |
| **Cougr integration** | If the example uses `GameApp`, `SimpleQueryBuilder`, auth, or ZK APIs, at least one test exercises that integration path |

Tests must use the `soroban-sdk` `testutils` feature and `Env::default()`. Do not mock the Soroban environment at the Rust level; use the SDK test harness.

---

## 6. Repository Hygiene

- Do not commit `target/` directories. Each example's `.gitignore` (or the root `.gitignore`) must exclude them.
- Do not commit `.wasm` artifacts, `*.wasm`, or build output.
- `Cargo.lock` should be committed for examples (they are end-user applications, not libraries).
- Keep `Cargo.toml` minimal: only direct dependencies, no unused features, no wildcard version specifiers.

---

## 7. Canonical vs Transitional Examples

### Canonical examples

A canonical example is a maintained reference architecture. It is held to the full standard in this document and is expected to stay current as `cougr-core` evolves. Canonical examples are the ones new contributors should read first.

Current canonical examples:

| Example | Pattern demonstrated |
|---|---|
| `snake` | Arcade loop, `GameApp` tick model, basic ECS |
| `battleship` | Hidden-information, commit-reveal, `privacy::stable` Merkle primitives |
| `guild_arena` | Account abstraction, social recovery, multi-device authorization |

### Transitional examples

A transitional example is one that was written before the current standard or that intentionally preserves an older pattern for compatibility reference. It must be clearly marked as such in its own README:

```markdown
> **Transitional example**: This example uses an older Cougr pattern and is preserved
> for compatibility reference. For the current recommended approach, see `snake`.
```

Transitional examples are still expected to pass `cargo test` and `stellar contract build`. They are not required to match the module structure or README depth of canonical examples, but they must not mislead readers into thinking the older pattern is preferred.

---

## 8. Cougr API Usage Guidance

Use the following table to decide which Cougr APIs an example should use and document.

| API | Use when |
|---|---|
| `GameApp` | Any example with more than one system or stage |
| `ScheduleStage` | Systems must run in a defined order within a tick |
| `SimpleWorld` | The example stores and queries entities with multiple components |
| `SimpleQueryBuilder` | The example scans entities by component type (more than one entity type) |
| `auth` (Beta) | The example demonstrates session keys, multi-device flows, or account recovery |
| `privacy::stable` | The example demonstrates commit-reveal, Merkle proofs, or selective disclosure |
| `privacy::experimental` | The example demonstrates Groth16 proof submission or BN254/BLS12-381 operations |
| `ops` standards | The example needs pausability, access control, or ownership transfer |

When an API is used, the README must explain **why** that API was chosen, not just that it was used.

---

## Quality Checklist

Copy this checklist into a follow-up cleanup issue for each example:

```markdown
## Example quality checklist — `<example-name>`

### Dependencies
- [ ] Uses published `cougr-core` version, not a path dependency

### Build validation
- [ ] `cargo test` passes
- [ ] `stellar contract build` passes

### Module structure
- [ ] `lib.rs` contains only contract entrypoints and GameApp wiring
- [ ] `components.rs` exists and contains all `impl_component!` types
- [ ] `systems.rs` exists and contains game logic systems
- [ ] Additional modules (`auth.rs`, `privacy.rs`, `zk.rs`, `types.rs`) added only if used

### README
- [ ] Purpose and pattern section present
- [ ] Public contract API documented
- [ ] Architecture overview present
- [ ] Storage model described
- [ ] Main gameplay flow documented
- [ ] Cougr APIs used section present with rationale
- [ ] Build and test commands shown
- [ ] Known limitations noted
- [ ] No hardcoded testnet contract IDs or deployment results

### Tests
- [ ] Initialization test present
- [ ] Happy-path gameplay test present
- [ ] Invalid action test present
- [ ] Rule/invariant test present
- [ ] Cougr integration test present (if applicable)
- [ ] Tests use `soroban-sdk` testutils and `Env::default()`

### Repository hygiene
- [ ] `target/` excluded from version control
- [ ] No committed `.wasm` artifacts
- [ ] `Cargo.lock` committed
- [ ] `Cargo.toml` has no unused dependencies or wildcard versions

### Classification
- [ ] Marked as canonical or transitional in the README
- [ ] If transitional: banner note present pointing to preferred alternative
```
