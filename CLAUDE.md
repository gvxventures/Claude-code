# CLAUDE.md

This file provides context and conventions for AI assistants (Claude Code and others) working in this repository.

## Repository Overview

**Repository:** gvxventures/Claude-code
**Purpose:** Starter/template repository for Claude Code projects
**Current state:** Initial scaffold — no source code yet

This is a fresh repository with no established language, framework, or tooling. As the project grows, update this file to reflect actual conventions and structure.

## Repository Structure

```
Claude-code/
├── README.md       # Project title only — expand as the project takes shape
└── CLAUDE.md       # This file
```

## Git Workflow

### Branch Strategy

- `main` — stable, production-ready code
- Feature branches follow the pattern: `claude/<description>-<id>` (e.g. `claude/add-claude-documentation-IgdK7`)

### Branch Rules

- **Never push directly to `main`** without explicit permission
- Develop all changes on the designated feature branch
- Commit with clear, descriptive messages
- Push with: `git push -u origin <branch-name>`

### Commit Messages

- Use imperative mood: "Add feature" not "Added feature"
- Keep the subject line under 72 characters
- Reference issues or context where relevant

## Development Setup

No tooling has been established yet. When a language and framework are chosen:

1. Document the setup steps here (e.g. `npm install`, `pip install -r requirements.txt`)
2. Add a `.gitignore` appropriate for the chosen stack
3. Configure linting and formatting tools
4. Add a test runner and document how to run tests

## Code Conventions

No code exists yet. When writing the first code:

- Establish and document the language and version here
- Add linting config (ESLint, Ruff, etc.) and note the lint command
- Add a formatter (Prettier, Black, etc.) and note the format command
- Define where source lives (e.g. `src/`, `lib/`) and where tests live (e.g. `tests/`, `__tests__/`)

## Testing

No tests exist yet. When adding tests:

- Document the test framework and the command to run tests (e.g. `npm test`, `pytest`)
- Aim for tests alongside source code or in a dedicated `tests/` directory
- Do not commit code that breaks existing tests

## Working with AI Assistants

### Key Principles

- Read files before modifying them
- Make minimal, targeted changes — avoid unrelated refactors
- Do not add comments, docstrings, or type annotations to code you did not change
- Prefer editing existing files over creating new ones
- Do not create helpers or abstractions for one-time operations
- Check with the user before taking irreversible actions (force pushes, deleting branches, dropping data)

### GitHub Interactions

Use `mcp__github__*` tools for all GitHub interactions (issues, PRs, comments). Do not use the `gh` CLI.

Do not create pull requests unless explicitly asked.

## CI/CD

No CI/CD pipelines are configured. When added, document them here and in `.github/workflows/`.

## Notes for Future Updates

When this file becomes stale, update it to reflect:
- The actual tech stack and chosen language/framework
- Real setup instructions
- Established test commands
- Lint and format commands
- Any project-specific gotchas or non-obvious conventions
