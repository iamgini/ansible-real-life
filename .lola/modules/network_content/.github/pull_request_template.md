## Summary

<!-- Brief description of what this PR does -->

## Type of Change

<!-- Check all that apply -->

- [ ] 🙋 New skill/command (Tier 2 - Author)
- [ ] 🔧 Skill improvement (Tier 3 - Improve)
- [ ] 🐛 Bug fix
- [ ] 📝 Documentation update
- [ ] 🏗️ Infrastructure/tooling
- [ ] 🎨 Module structure (new Lola module)

## Testing

<!-- Describe how you tested this change -->

**AI Assistant Used:** <!-- e.g., Claude Code 1.5.0, Cursor 0.42, Gemini CLI -->

**Test Scenarios:**

- [ ] Tested happy path
- [ ] Tested error handling
- [ ] Tested edge cases

**Test Results:**

```
<!-- Paste test output or describe what you tested and the results -->

Example:
✅ Skill correctly generated release notes from changelog fragments
✅ Error handling: Clear error when no fragments found
✅ Edge case: Handles collections with no previous releases
```

## Quality Checklist

<!-- Verify all items before submitting -->

### Required for All Contributions

- [ ] Pre-commit hooks pass locally (`pre-commit run --all-files`)
- [ ] No real credentials in examples (use placeholders like `<token>`, `user@example.com`)
- [ ] Professional and inclusive language
- [ ] Follows [Code of Conduct](../CODE_OF_CONDUCT.md)

### For Skills and Commands

- [ ] **Frontmatter is complete:**
  - [ ] `description` — Clear one-sentence summary
  - [ ] `allowed-tools` — All tools used are listed
  - [ ] `argument-hint` — Shows expected arguments (e.g., `"[--version <ver>]"`)
- [ ] **Documentation includes examples** showing how to invoke the skill
- [ ] **Tool usage is safe** (no destructive patterns without confirmation)
- [ ] **Lola-compatible** (standard frontmatter, works with Lola package manager)
- [ ] **Follows Ansible standards** (for Ansible-related skills: collection naming, galaxy.yml structure)

### AI Attribution

<!-- IMPORTANT: Required for transparency -->

- [ ] **If AI-assisted:** Commit message includes `Co-Authored-By` trailer

  ```
  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

  (Replace with the actual model you used)

- [ ] **If NOT AI-assisted:** Check this box to confirm you wrote everything yourself

See [CONTRIBUTING.md](../CONTRIBUTING.md#ai-attribution) for attribution guidelines.

## Related Issues

<!-- Link any related GitHub Issues -->

Closes #<!-- issue number -->

## Additional Context

<!-- Any other information, screenshots, or context -->

## Checklist for Reviewers

<!-- Maintainers: Use this during review -->

- [ ] Aligns with [GOVERNANCE.md](../GOVERNANCE.md) contribution principles
- [ ] Solves a real problem for the Ansible community
- [ ] Documentation is clear and includes examples
- [ ] No security concerns (credentials, destructive operations)
- [ ] CI checks pass
