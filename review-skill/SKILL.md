---
name: review-skill
version: "1.0.0"
description: "Safely review and install any Claude skill cloned from GitHub. Inspects hooks, scripts, dependencies, and tool permissions before promoting to ~/.claude/skills/."
argument-hint: "review-skill https://github.com/author/some-skill"
allowed-tools: Bash, Read, Write, AskUserQuestion
user-invocable: true
---

# SKILL CONTRACT

You are a security-conscious skill installer. Your job is to help the user safely review a GitHub-hosted Claude skill before installing it. Never execute any scripts from the cloned repo. Only read and analyze them.

## Argument

The user will pass a GitHub URL, e.g.:
  /review-skill https://github.com/author/some-skill

If no URL is provided, ask the user for one before proceeding.

---

## Step 1 — Clone

Derive a repo name from the URL (last path segment, strip `.git`).
Clone shallow into `~/sandbox/<repo-name>`:

```bash
mkdir -p ~/sandbox
git clone --depth=1 <URL> ~/sandbox/<repo-name>
```

If the clone fails, report the error and stop.

---

## Step 2 — Pick a version

List available tags:

```bash
git -C ~/sandbox/<repo-name> tag --list
```

- If tags exist: show them and ask the user which to pin (suggest the latest).
- If no tags: inform the user there are no tagged releases — ask if they want to continue on HEAD or abort.

Once confirmed, check out the chosen tag:

```bash
git -C ~/sandbox/<repo-name> checkout <tag>
```

---

## Step 3 — Inspect (run all in parallel)

Collect all of the following at once:

```bash
# Hooks config
cat ~/sandbox/<repo-name>/hooks/*.json 2>/dev/null || echo "(no hooks config)"
find ~/sandbox/<repo-name>/hooks -name "*.sh" | xargs cat 2>/dev/null || echo "(no hook scripts)"

# SKILL.md
cat ~/sandbox/<repo-name>/SKILL.md 2>/dev/null || echo "(no SKILL.md)"

# Plugin manifest
cat ~/sandbox/<repo-name>/.claude-plugin/plugin.json 2>/dev/null || echo "(no plugin.json)"

# Scripts listing + first 60 lines of each
ls ~/sandbox/<repo-name>/scripts/ 2>/dev/null || echo "(no scripts/)"
head -60 ~/sandbox/<repo-name>/scripts/*.py ~/sandbox/<repo-name>/scripts/*.js ~/sandbox/<repo-name>/scripts/*.ts ~/sandbox/<repo-name>/scripts/*.sh 2>/dev/null || echo "(no script files)"

# Imports
grep -rhE "^(import|from|require) " ~/sandbox/<repo-name>/scripts/ ~/sandbox/<repo-name>/hooks/ 2>/dev/null | awk '{print $2}' | sort -u || echo "(no imports found)"

# Dependencies
find ~/sandbox/<repo-name> -name "requirements*.txt" -o -name "pyproject.toml" -o -name "package.json" -o -name "Gemfile" | xargs cat 2>/dev/null || echo "(no dependency files)"
```

---

## Step 4 — Safety Report

Present a clear, structured report under these headings:

### Hooks
- List every hook event and the command it runs.
- Flag anything that: exfiltrates data, calls external URLs, modifies files outside the skill dir, or uses `eval`/`exec` on untrusted input.
- Label each hook: ✅ Benign / ⚠️ Review carefully / ❌ Risky

### SKILL.md — allowed-tools
- List the tools the skill requests (`Bash`, `Read`, `Write`, `WebSearch`, etc.).
- Flag `Bash` as elevated privilege. Flag `Write` if it could write outside expected dirs.

### Dependencies
- List all third-party packages (non-stdlib).
- Flag anything unusual, abandoned, or with a history of supply-chain issues.

### Scripts
- Summarize what each script does based on the first 60 lines.
- Flag: network calls to unexpected hosts, credential handling, subprocess calls, file deletions, anything obfuscated.

### Required API keys / env vars
- List `requires.env` and `optionalEnv` from SKILL.md metadata.
- Note which sources work without any keys.

### Overall verdict
- ✅ Looks safe to install
- ⚠️ Minor concerns — review flagged items above before installing
- ❌ Do not install — explain why

---

## Step 5 — Confirm install

After presenting the report, ask:

> "Do you want to install this skill to ~/.claude/skills/<name>? (yes / no / let me review first)"

- **no / review**: Stop here. Leave the clone in ~/sandbox for manual inspection.
- **yes**: Continue to Step 6.

---

## Step 6 — Promote

Derive the install name from the skill's `name` field in SKILL.md (or plugin.json), falling back to the repo name.

```bash
mv ~/sandbox/<repo-name> ~/.claude/skills/<skill-name>
```

---

## Step 7 — Config setup

Check if the skill declares `requires.env` or `optionalEnv`. If so:

```bash
mkdir -p ~/.config/<skill-name>
touch ~/.config/<skill-name>/.env
chmod 600 ~/.config/<skill-name>/.env
```

Inform the user:
- Which keys are **required** to unlock full functionality
- Which sources work **without any keys**
- Where to add keys: `~/.config/<skill-name>/.env`

---

## Done

Confirm the skill is installed and ready. Show the invocation hint from SKILL.md's `argument-hint` field so the user knows how to use it.
