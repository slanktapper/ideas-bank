# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

**ideas-bank** is a bank of independent ideas, tools, and experiments. It is not a
single application: there is no shared build, no shared dependency tree, and no
top-level package manifest. Each idea lives on its own in a folder and is developed
in isolation from the others.

The repository exists to be driven by Claude Code. The conventions below are the
product; treat them as binding.

## Repository layout

The root of the repository contains exactly two kinds of entries:

1. **Direction `.md` files** — repo-level guidance (this file, `DIRECTION.md`, and any
   future direction docs). These describe intent and rules, not implementation.
2. **Project folders**, one per idea/tool/experiment, named with the project's
   **short name**.

Nothing else belongs at the root. No source files, no config for a particular idea,
no shared `src/`, no scratch files. If something is specific to one idea, it goes
inside that idea's folder.

```
ideas-bank/
├── CLAUDE.md            # this file — how Claude works in this repo
├── DIRECTION.md         # repo-level direction + the project registry
├── <short-name>/        # one idea/tool per folder
│   ├── direction.md     # what this idea is, where it is going
│   └── ...              # that idea's own code, config, docs, data
└── <short-name>/
    └── ...
```

### Short names

The short name is the folder name and the identifier the user will use to refer to a
project in conversation. Rules:

- lowercase, hyphen-separated, no spaces (`recipe-parser`, not `Recipe Parser`)
- short enough to type in a sentence — one to three words
- stable; renaming a project folder means updating `DIRECTION.md` too

**The filesystem is the source of truth** for which projects exist. The registry in
`DIRECTION.md` carries the one-line description for each, and may lag behind; when
they disagree, trust the directory listing and fix the registry.

## Start of every conversation: establish the project

Work in this repo is always scoped to one project. **Before doing any work, you must
know which project the conversation is about.**

If the user's first request does not name a project — explicitly, or unambiguously
by context (a path, a file, a distinctive feature name) — **stop and ask.** Use
`AskUserQuestion`, and offer the existing short names as the options, each with its
one-line description. Read the current list by listing the root directory:

```bash
ls -d */ 2>/dev/null | sed 's#/##'
```

Then pair those names with their descriptions from `DIRECTION.md`. Always include an
option for starting a **new** project, since the answer may not be in the list.

Do not guess the project, do not default to "the most recently modified folder", and
do not begin exploratory work in the hope the answer becomes obvious. An unscoped
question ("can you clean up the parser?") when two projects have a parser is exactly
the case this rule exists for.

Once the project is established, stay inside its folder for the rest of the
conversation unless the user redirects you.

## Moving data or code between projects: always ask first

Projects are deliberately independent. Duplication between them is acceptable;
silent coupling is not.

When work requires something from another project — a data file, a module, a schema,
a prompt, a config, a set of results — **do not copy, move, import, or symlink it on
your own.** Stop and ask the user how they want it handled, via `AskUserQuestion`.
Frame the question with what you found, where it lives, and what you need it for, and
offer the realistic options, typically:

- **Copy** it into the destination project — the two diverge from here, no coupling.
- **Move** it — the source project loses it; say what in the source will break.
- **Reference in place** — the destination reads from the source path; note that this
  creates a dependency between two folders meant to be independent.
- **Extract to a new shared project** — a new short-named folder both projects use;
  the heaviest option, worth it only for something genuinely reusable.
- **Reimplement** from scratch in the destination — no shared bytes at all.

Name a recommendation, then wait for the answer. This applies to any cross-folder
flow, including the reverse direction (writing results from the current project into
another one) and including cases where the user's phrasing implies it ("use the
scraper from `link-hoard`") — implied is not the same as decided, so confirm the
mechanism even when the intent is clear.

## Working inside a project

- Each project folder is self-contained: its own dependencies, its own tooling, its
  own tests, its own README/`direction.md`.
- **Read the project's `direction.md` first.** It states what the idea is for and
  what it is deliberately not doing. It outranks your assumptions about the idea.
- There is no repo-wide language, framework, or test runner. Infer conventions from
  the project you are in, and match them. Do not import habits from a sibling folder.
- Run commands from inside the project folder, not from the root.
- If a project has no tooling yet, ask before choosing a stack rather than picking
  one silently.

### Starting a new project

When the user asks for a new idea/tool:

1. Agree on the short name before creating anything.
2. Create `<short-name>/` at the root.
3. Create `<short-name>/direction.md` — start it from the template below and fill it
   in from what the user has told you.
4. Add a row for it to the registry in `DIRECTION.md`.

### `direction.md` template

```markdown
# <short-name>

**Status:** idea | prototype | working | parked | retired

## What it is
One paragraph: the idea in plain language.

## Why
The problem it solves, or the itch it scratches.

## Scope
What this does. Just as importantly: what it deliberately does not do.

## Stack
Language, framework, package manager, anything needed to run it.

## How to run
Install, run, test — the commands, verbatim.

## Open questions
Decisions not yet made. Things to revisit.
```

Keep `direction.md` current as the idea moves. When a project's direction changes,
update the file in the same commit as the change.

## Git conventions

- One project per commit wherever possible. A commit touching three project folders
  should almost always have been three commits.
- Prefix the commit subject with the short name: `recipe-parser: add ingredient
  fraction handling`. Root direction docs use `docs:` or `direction:`.
- Never commit secrets, API keys, or credentials. Each project keeps its own
  `.env.example`; the real `.env` stays untracked.
- Follow the branch instructions given for the session. Do not push to a branch you
  were not asked to push to, and do not open a pull request unless asked.

## Conventions summary

| Rule | Behaviour |
| --- | --- |
| Unknown project | Ask, offering the existing short names |
| Cross-project data or code | Ask how to handle it; never move it unilaterally |
| Root directory | Direction `.md` files and project folders only |
| Project folder | Self-contained; conventions come from inside it |
| New idea | Short name → folder → `direction.md` → registry row |
