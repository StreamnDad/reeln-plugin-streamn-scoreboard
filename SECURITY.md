# Security Policy

## Supported Versions

reeln-plugin-streamn-scoreboard is pre-1.0 software. Security fixes are
published against the latest release only. We recommend always running
the most recent version from
[PyPI](https://pypi.org/project/reeln-plugin-streamn-scoreboard/) or the
[Releases page](https://github.com/StreamnDad/reeln-plugin-streamn-scoreboard/releases).

| Version | Supported          |
| ------- | ------------------ |
| latest release | :white_check_mark: |
| older   | :x:                |

## Scope

reeln-plugin-streamn-scoreboard is a reeln-cli plugin that bridges
`reeln` game initialization to the Streamn Scoreboard OBS plugin by
writing the team names, sport, and period configuration to the
scoreboard's text file output directory. It runs inside `reeln-cli` on
a livestreamer's local machine and performs only local file I/O — it
does not make network requests.

In-scope concerns include, but are not limited to:
- Path traversal when writing to the configured scoreboard output
  directory using team names, sport strings, or game metadata as
  filename or path components
- Unsafe deserialization of game state, roster data, or cached
  scoreboard state files (JSON / text round-trips)
- Command injection via subprocess calls, if any, that incorporate
  user-supplied game metadata
- Insecure file permissions on generated scoreboard text files
- Dependency confusion or typosquatting on the PyPI package name

Out of scope:
- Vulnerabilities in the Streamn Scoreboard OBS plugin itself — report
  those to [StreamnDad/streamn-scoreboard](https://github.com/StreamnDad/streamn-scoreboard/security)
- Vulnerabilities in reeln-cli or other reeln plugins — report those to
  the respective repository
- Issues that require an attacker to already have local code execution
  on the user's machine

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub
issues, discussions, or pull requests.**

Report vulnerabilities using GitHub's private vulnerability reporting:

1. Go to the [Security tab](https://github.com/StreamnDad/reeln-plugin-streamn-scoreboard/security)
   of this repository
2. Click **"Report a vulnerability"**
3. Fill in as much detail as you can: affected version, reproduction steps,
   impact, and any suggested mitigation

If you cannot use GitHub's reporting, email **git-security@email.remitz.us**
instead.

### What to include

A good report contains:
- The version of reeln-plugin-streamn-scoreboard, reeln-cli, and Python
  you tested against
- Your operating system and architecture (macOS / Windows / Linux, arch)
- Steps to reproduce the issue
- What you expected to happen vs. what actually happened
- The potential impact (path traversal, file clobbering, data loss, etc.)
- Any proof-of-concept code, if applicable

### What to expect

This plugin is maintained by a small team, so all timelines below are
best-effort rather than hard guarantees:

- **Acknowledgement:** typically within a week of your report
- **Initial assessment:** usually within two to three weeks, including
  whether we consider the report in scope and our planned next steps
- **Status updates:** roughly every few weeks until the issue is resolved
- **Fix & disclosure:** coordinated with you. We aim to ship a patch
  release reasonably quickly for high-severity issues, with lower-severity
  issues addressed in a future release. Credit will be given in the
  release notes and CHANGELOG unless you prefer to remain anonymous.

If a report is declined, we will explain why. You are welcome to disagree
and provide additional context.
