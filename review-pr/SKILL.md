---
name: review-pr
description: Systematically review pull requests with focus on critical paths, code quality, security, and production readiness. Use when reviewing PRs or branch merges.
disable-model-invocation: false
allowed-tools: Bash Read Grep Glob
argument-hint: [branch-name]
---

# Pull Request Systematic Review

Perform a thorough, systematic review of a pull request broken into focused parts. Prioritize critical areas without overkill.

## Usage

```bash
/review-pr branch-name
```

Or let Claude auto-invoke by asking:
```
Review this PR for me
Review Sayantan's branch
```

## Review Process

### 1. **Initial Assessment** (Quick Overview)
- Fetch and analyze commit history
- Get diff statistics (files changed, lines added/removed)
- Identify the main areas of change (new features, refactors, bug fixes)
- Check for any obvious red flags (secrets, large binary files, etc.)

### 2. **Architecture & Structure Review**
Focus on:
- New directory structures and organization
- Module separation and dependencies
- Configuration management patterns
- Integration points between components

**Output**: High-level architecture assessment with any structural concerns.

### 3. **Code Quality Review** (Priority areas first)
Examine in order of criticality:
1. **Security-sensitive code**: Authentication, authorization, data handling
2. **Core business logic**: Main algorithms, data processing pipelines
3. **Integration points**: API calls, database interactions, external services
4. **Supporting code**: Utilities, helpers, configuration

For each area, check:
- Code clarity and maintainability
- Error handling completeness
- Edge case coverage
- Appropriate abstractions (no over-engineering)

**Output**: Specific file-level findings with line references.

### 4. **Security & Best Practices**
- Credentials and secrets handling (check for hardcoded values)
- Input validation and sanitization
- Environment variable usage
- Dependency security (requirements.txt, package.json)
- File permissions and access patterns

**Output**: Security findings and best practice violations.

### 5. **Dependencies & Configuration**
- Review requirements.txt / package.json completeness
- Check for version pinning
- Verify imports match dependencies
- Examine configuration files (.env examples, config files)

**Output**: Dependency issues and missing requirements.

### 6. **Testing & Validation Needs**
Identify what needs testing based on criticality:
- **Critical**: Data pipelines, financial calculations, user-facing features
- **Important**: Integration points, configuration loading, error handling
- **Nice-to-have**: Utilities, helpers, UI components

For existing tests:
- Check coverage of critical paths
- Verify test data quality
- Review test assertions

**Output**: Testing gaps prioritized by criticality.

### 7. **Documentation Review**
- README accuracy and completeness
- Code comments (only where logic isn't self-evident)
- API documentation
- Setup/deployment instructions

**Output**: Documentation gaps or inaccuracies.

## Review Guidelines

### What to Focus On
✅ **Security vulnerabilities**
✅ **Data integrity issues**
✅ **Breaking changes**
✅ **Performance bottlenecks**
✅ **Missing error handling**
✅ **Critical path testing**
✅ **Production readiness**

### What to Avoid (No Overkill)
❌ Nitpicking formatting (unless it impacts readability)
❌ Suggesting abstractions for one-off code
❌ Requiring tests for trivial utilities
❌ Adding comments to self-explanatory code
❌ Over-engineering simple solutions

### Code Quality Quick Checks
When reviewing logic/structure, watch for:
- **Repeated code blocks** (3+ times = candidate for extraction)
- **Functions doing multiple things** (split if mixing concerns)
- **Unclear names** (variables/functions should be self-explanatory)
- **Premature abstractions** (helper for one caller = over-engineering)
- **Comments explaining "what"** (code should show what, comments explain why)

## Output Format

Structure findings as:

```markdown
## Review Summary for [branch-name]

### Overview
- [High-level description of changes]
- [Main areas touched]
- [Overall risk assessment: Low/Medium/High]

### Critical Findings 🔴
- [File:Line] [Issue with security/data/production impact]

### Important Issues 🟡
- [File:Line] [Code quality, best practice violations]

### Suggestions 🟢
- [File:Line] [Nice-to-have improvements]

### Testing Recommendations
**Critical** (must test):
- [Specific feature/path to test]

**Important** (should test):
- [Feature/path to test]

### Documentation Needs
- [What documentation is missing or needs updating]

### Dependencies
- [Any missing or problematic dependencies]

### Approval Recommendation
- [ ] Approve (ready to merge)
- [ ] Approve with comments (merge after addressing suggestions)
- [ ] Request changes (critical issues must be fixed)

### Next Steps
1. [Action items for PR author]
2. [Follow-up tasks]
```

## Smart Prioritization

**Focus time on**:
- New production code
- Security-sensitive areas
- Data handling pipelines
- External integrations

**Quick pass on**:
- Test files (verify they exist and cover critical paths)
- Documentation (check completeness, not prose)
- Configuration files (verify format and required fields)
- Reference/example code

## Integration with Workflow

After review, offer to:
1. Create detailed PR comments on specific files
2. Generate a testing checklist
3. Draft PR approval/change request message
4. Create follow-up issues for non-blocking items
