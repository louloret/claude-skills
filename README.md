# Claude Skills

A collection of custom skills for [Claude Code](https://claude.ai/code).

## Skills

### [last30days](https://github.com/louloret/last30days-skill)

Research what people are actually saying about any topic across the last 30 days. Pulls posts and engagement from Reddit, X/Twitter, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web — scoring and ranking them so the best signal rises to the top.

```
/last30days <topic>
```

---

### linkedin-carousel

Turn any topic, article, or workflow into a polished LinkedIn carousel PDF and post text. Generates 8–10 structured slides using Anthropic brand colors, plus a ready-to-paste LinkedIn caption with hook, body, and hashtags.

```
/linkedin-carousel <topic, article, or file path>
```

---

### review-pr

Systematically review a pull request with focus on critical paths, code quality, security, and production readiness. Breaks the review into structured phases — architecture, code quality, security, dependencies, testing, and documentation — and outputs prioritized findings with file and line references.

```
/review-pr <branch-name>
```

---

### review-skill

Safely review and install any Claude skill cloned from GitHub. Inspects hooks, scripts, dependencies, and tool permissions before promoting to `~/.claude/skills/` — so you know what you're running before you run it.

```
/review-skill <github-url>
```

---

## Installation

Clone the repo into your Claude skills directory:

```bash
git clone --recurse-submodules https://github.com/louloret/claude-skills.git ~/.claude/skills
```

Skills are automatically available in Claude Code once they're in `~/.claude/skills/`.
