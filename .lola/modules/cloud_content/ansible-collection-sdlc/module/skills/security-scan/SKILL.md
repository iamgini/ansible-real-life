---
name: security-scan
description: >
  Scans Ansible collection dependencies, CI workflows, and code for security
  vulnerabilities. Use this skill when asked to audit security, detect
  hardcoded secrets, check for vulnerable packages, or validate supply chain
  risks before releases. Supports optional `--update` and `--fix` flags.
metadata:
  author: Ansible Community
  version: 1.0.0
  inspired-by: https://github.com/ansible/apme
user-invocable: true
---

# Security Scan

Scan an Ansible collection for security vulnerabilities, hardcoded secrets,
and compromised dependencies.

## Purpose

Identify security issues before they reach production:

- Hardcoded secrets in code, tests, or examples
- Vulnerable Python dependencies
- Compromised GitHub Actions versions
- Supply chain risks in CI/CD pipelines

## Scope

**Primary use case**: Catch secrets before they are pushed to shared branches. Run this scan:

- Before creating a PR
- In CI pipelines on pull requests
- Before releases

**Secondary use case**: Identify existing secrets that need remediation. For secrets already in git history:

- The secret is already exposed and should be rotated immediately
- Use `git filter-repo` or BFG to remove from history
- This skill identifies what needs rotation, not how to scrub history

## When to Invoke

TRIGGER when:

- User asks to "scan for vulnerabilities" or "security audit"
- Before creating a release
- After adding new dependencies
- When reviewing external contributions
- User asks to "check for secrets" or "find hardcoded credentials"

DO NOT TRIGGER when:

- Running general code review (use `pr-review` instead)
- Checking code style (use `ansible-lint` instead)

## Usage

```bash
/security-scan                    # Full scan of current collection
/security-scan --update           # Fetch latest advisories, then scan
/security-scan --fix              # Attempt to fix vulnerable dependencies
```

## What Gets Scanned

### 1. GitHub Actions (CI/CD Supply Chain)

Searches `.github/workflows/*.yml` and `.github/workflows/*.yaml` for:

- Vulnerable action versions with known CVEs
- Actions from untrusted sources
- Actions not pinned to commit SHAs
- Deprecated or archived actions

**Known vulnerable actions** (examples):

- `actions/checkout` < v4 (various CVEs)
- `actions/upload-artifact` < v4 (path traversal)
- Unmaintained third-party actions

### 2. Python Dependencies

Searches `requirements.txt`, `*-requirements.txt`, `pyproject.toml`, `bindep.txt` for:

- Packages with known CVEs (via pip-audit or safety)
- Yanked package versions
- Packages with supply chain compromises

### 3. Ansible Content

Searches `plugins/`, `roles/`, `playbooks/` for:

- Hardcoded passwords, tokens, API keys
- Private keys or certificates
- AWS credentials, Azure secrets, GCP keys
- Vault passwords in plaintext

**Patterns detected**:

- `password:`, `secret:`, `token:`, `api_key:` with literal values
- Base64-encoded secrets
- Private key headers (`-----BEGIN <TYPE> PRIVATE KEY-----`)
- Cloud provider credential patterns

### 4. Test Fixtures and Examples

Searches `tests/`, `examples/`, `docs/` for:

- Real API keys or credentials in examples
- Sensitive data in integration test configs

**Exceptions**: Skip findings where:

- An inline comment marks the credential as intentional (e.g., `# test-credential: intentional`)
- The file is clearly a test fixture with generated/example data

**Recommendation**: Generate test credentials (keys, certificates) at runtime rather than committing them. This avoids false positives and prevents certificate expiration issues in tests.

### 5. Git History (Optional)

With `--deep` flag, searches git history for:

- Accidentally committed secrets later removed
- Credentials in old commits

## Scan Procedure

### Step 1: Check for scanning tools

```bash
# Check if pip-audit is available
pip-audit --version 2>/dev/null || echo "pip-audit not installed"

# Check if gitleaks is available
gitleaks version 2>/dev/null || echo "gitleaks not installed"

# Check if trivy is available
trivy --version 2>/dev/null || echo "trivy not installed"
```

If tools are missing, provide installation instructions and continue with
built-in pattern matching.

### Step 2: Scan Python dependencies

```bash
# Using pip-audit (preferred)
pip-audit -r requirements.txt -r test-requirements.txt 2>/dev/null

# Or using safety
safety check -r requirements.txt 2>/dev/null

# Manual check for known bad packages
grep -E "^(eventlet|gevent|requests)==[0-2]\." requirements*.txt
```

### Step 3: Scan GitHub Actions

```bash
# Check for unpinned actions
grep -rE "uses: [^@]+$" .github/workflows/

# Check for vulnerable action versions
grep -rE "actions/checkout@v[1-3]" .github/workflows/
grep -rE "actions/upload-artifact@v[1-3]" .github/workflows/
```

### Step 4: Scan for secrets

```bash
# Using gitleaks (required for reliable detection)
if command -v gitleaks &>/dev/null; then
    gitleaks detect --source . --no-git --report-format json --report-path gitleaks-report.json
else
    echo "WARNING: gitleaks not installed. Secret detection skipped."
    echo "Install: https://github.com/gitleaks/gitleaks#installing"
fi
```

**Why gitleaks**: Manual regex patterns like `BEGIN.*PRIVATE KEY` or `AKIA` have high
false-positive rates. `AKIA` is just the key ID (like a username), not secret material.
`BEGIN.*PRIVATE KEY` matches search patterns and validation code. gitleaks uses
context-aware detection and supports `.gitleaksignore` for marking false positives.

### Step 5: Generate report

Output findings in structured format:

```
## Security Scan Report

### Summary
- Total issues found: N
- Critical: N
- High: N
- Medium: N
- Low: N

### Findings

#### Critical

1. **Hardcoded AWS credentials** (SEC-001)
   - File: `tests/integration/targets/ec2/tasks/main.yml`
   - Line: 42
   - Pattern: `aws_access_key: AKIA...`
   - Fix: Use environment variables or Ansible Vault

#### High

2. **Vulnerable dependency** (SEC-002)
   - Package: `requests==2.25.0`
   - CVE: CVE-2023-32681
   - Fix: Upgrade to `requests>=2.31.0`

### Recommendations

1. [ ] Remove hardcoded credentials and use Ansible Vault
2. [ ] Update vulnerable dependencies
3. [ ] Pin GitHub Actions to commit SHAs
```

## Known Vulnerable Packages (Ansible Ecosystem)

This list is maintained and updated periodically:

| Package | Vulnerable Versions | CVE | Severity |
|---------|---------------------|-----|----------|
| `ansible` | < 2.9.27 | Multiple | High |
| `ansible-core` | < 2.14.14, < 2.15.9, < 2.16.3 | CVE-2024-0690 | Medium |
| `paramiko` | < 3.4.0 | CVE-2023-48795 | High |
| `cryptography` | < 41.0.0 | Multiple | High |
| `requests` | < 2.31.0 | CVE-2023-32681 | Medium |
| `urllib3` | < 2.0.7 | CVE-2023-45803 | Medium |
| `jinja2` | < 3.1.3 | CVE-2024-22195 | Medium |
| `pyyaml` | < 6.0.1 | CVE-2020-14343 | Critical |

## GitHub Actions Security

### Recommended Practices

Pin actions to full commit SHA, not tags:

```yaml
# Bad - tag can be moved
- uses: actions/checkout@v4

# Good - immutable reference
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
```

### Known Vulnerable Actions

| Action | Vulnerable Versions | Issue |
|--------|---------------------|-------|
| `actions/checkout` | v1, v2, v3 | Various path traversal issues |
| `actions/upload-artifact` | v1, v2, v3 | Path traversal CVE-2024-XXXXX |
| `github/codeql-action` | < 2.2.5 | Command injection |

## Auto-Fix Capabilities

With `--fix` flag, the skill can automatically:

1. **Update vulnerable dependencies** in `requirements.txt`
2. **Pin GitHub Actions** to commit SHAs
3. **Add `.gitignore` entries** for common secret files

**Cannot auto-fix**:

- Hardcoded secrets (requires manual remediation)
- Secrets in git history (requires `git filter-repo`)

## Integration

This skill integrates with:

- `pr-review` - Security findings included in PR reviews
- `release` - Security scan before release
- `create-pr` - Optional pre-PR security check

## Configuration

Optional environment variables:

```bash
# Skip specific checks
export SECURITY_SCAN_SKIP="git-history,examples"

# Custom patterns file
export SECURITY_SCAN_PATTERNS="$HOME/.security-patterns.yml"

# Output format
export SECURITY_SCAN_FORMAT="json"  # or "markdown" (default)
```

## Exit Codes

- `0`: No security issues found
- `1`: Security issues found (see report)
- `2`: Scan failed (missing dependencies, invalid config)

## References

- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [GitHub Security Advisories](https://github.com/advisories)
- [pip-audit](https://github.com/pypa/pip-audit)
- [gitleaks](https://github.com/gitleaks/gitleaks)
- [Ansible Security Best Practices](https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#how-do-i-keep-secret-data-in-my-playbook)
