# Governance

This document describes how the ansible-community/ai-forge repository is managed, who is involved, and how decisions get made.
It is a living document that will evolve as the project and community grow.

## Roles

### Users

A user is anyone in the Ansible community who has installed the Lola modules and uses them with
their AI assistant. No requirements, no obligations beyond using the tools and providing feedback
when something does not work.

Filing a GitHub Issue to describe a workflow problem, suggest a new use case, or report a confusing
experience is a valuable contribution. You do not need to write code or open a pull request to
participate meaningfully.

### Contributors

A contributor is anyone who has shaped the repository in any way: opened an issue, proposed an idea, improved documentation, tested a skill and reported what happened, or submitted a pull request.

Contributions do not need to be code. Describing a manual process that could be automated, testing
a skill and sharing the results, or suggesting improvements to an existing command are all genuine
contributions. Filing a GitHub Issue with an idea is just as valuable as opening a pull request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the mechanics of contributing.

### Maintainers

Maintainers review and merge contributions, maintain skill quality, and participate in direction decisions for the repository.

**Current maintainers:**

See [CODEOWNERS](.github/CODEOWNERS) for the current list of maintainers.

Maintainers are responsible for:

- Reviewing pull requests for quality, Ansible standards compliance, and architectural fit
- Helping contributors get their ideas merged (not gatekeeping)
- Ensuring CI automation and quality tooling stays current
- Guiding the overall direction of the repository
- Coordinating with Red Hat Communities of Practice leadership

**Becoming a maintainer:** When existing maintainers notice consistent, valuable contributions and
sound judgment from a contributor, they will invite that person to join. This is a ladder, not a
gate -- there is no checklist of pull request counts to satisfy. Advancement is nomination-based:
an existing maintainer proposes, and the team discusses.

**Stepping back:** Stepping away from maintainer responsibilities is always welcome and normal. Circumstances change, and rotating in and out of active maintenance is part of a healthy project.

## Contribution Principles

### Follow Ansible Best Practices

When contributing, all skills and commands must align with:

- [Ansible development guidelines](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Red Hat Communities of Practice automation good practices](https://redhat-cop.github.io/)
- Collection standards (namespace.collection naming, galaxy.yml structure, semantic versioning)

The contribution gate (when implemented) will help validate compliance with these standards.

### AI Attribution Required

Transparency about AI assistance is mandatory:

- **All AI-assisted commits** must include a Co-Authored-By trailer:

  ```
  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

  (or the appropriate model/assistant you used)

- **Skills that generate external-facing content** (release notes, documentation, changelogs visible to end users) must include human review steps in their workflow

- **No AI-generated content presented as human-authored original work** -- if AI generated it, say so either in the content itself or in the commit message

Why this matters: The Ansible community values transparency. Users need to know when they're relying on AI-generated guidance so they can apply appropriate scrutiny.

### Test Before Contributing

Skills and commands must be tested before submission:

- Test the skill/command in your own AI assistant (Claude Code, Cursor, etc.)
- Document what you tested and the results in the PR description
- Include example invocations showing the skill in action
- If fixing a bug, demonstrate that the fix resolves the issue

### Cross-AI-Assistant Compatibility

This repository uses the [Lola package manager](https://lobstertrap.org/lola/) to ensure skills work across different AI assistants:

- All skills must work with Lola's packaging format
- Use standard frontmatter fields (see [SKILL_GUIDELINES.md](SKILL_GUIDELINES.md))
- Avoid assistant-specific features unless documented as optional enhancements
- Test with at least one AI assistant before submitting (Claude Code, Cursor, Gemini CLI, etc.)

### Keep the Barrier to Contribution Low

We want people to get comfortable being active contributors. If the process feels exclusive or difficult, that goal fails. Specifically:

- Issues are always welcome, even rough ones
- Maintainers help shape contributions, not reject them
- Technical barriers should not prevent someone with a good idea from contributing
- Documentation can be improved iteratively -- perfect is the enemy of good

## Decision-Making

Most changes just need a pull request and a maintainer review. If something feels like a bigger
shift -- a new module, a change to repository structure, or rethinking how something fundamental
works -- start a conversation first. Open a GitHub Issue or bring it up with a maintainer. This is
not a formal process, just a habit of talking before building when the change affects everyone.

### Consensus-Seeking

Decisions are made by consensus-seeking among maintainers. If maintainers disagree:

1. Discuss the options and tradeoffs openly (in Issues or PRs)
2. Try to find common ground or a compromise solution
3. If consensus cannot be reached, escalate to Red Hat CoP leadership for guidance

We don't use voting. We aim for agreement, not majority rule.

### What Requires Discussion First

These types of changes benefit from upfront discussion (open an Issue first):

- Adding a new Lola module (new top-level directory)
- Changing the repository structure or organization
- Adding new automation or CI requirements
- Changing contribution requirements or quality standards
- Anything that would affect existing users or contributors

### What Can Go Straight to PR

These types of changes can go directly to a pull request:

- New skills or commands within existing modules
- Bug fixes to existing skills
- Documentation improvements
- Updating examples or test scenarios
- Dependency updates

## Quality Standards

### Required for All Contributions

- **Pre-commit hooks pass** -- markdown, YAML, shell script checks
- **Lola-compatible frontmatter** -- all required fields present and valid
- **Documentation with examples** -- users need to see the skill in action
- **No secrets or credentials** -- use placeholders and example data
- **GPL-3.0-or-later license** -- all code must be properly licensed

### Encouraged but Not Required

- Test scenarios documented in the skill file
- Integration with existing skills (e.g., skills that call other skills)
- Error handling and user-friendly failure messages
- Support for multiple AI assistants (not just one)

## Enforcement

Quality standards are enforced through:

1. **Pre-commit hooks** -- run automatically on `git commit`, check formatting and syntax
2. **CI checks** -- run on every PR, validate structure and standards
3. **Contribution gate** (planned) -- automated quality assessment for skills
4. **Human review** -- maintainers review every PR before merge

If a PR does not meet quality standards:

- Maintainers will provide specific feedback on what needs to change
- The goal is to help you get your contribution merged, not block you
- If you're stuck, ask for help -- maintainers are here to assist

## Code of Conduct

This project follows the [Ansible Community Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## Changing This Document

This governance document is not fixed. As the project grows, the way we work together will evolve. To propose a change:

1. Open a GitHub Issue explaining the proposed change and rationale
2. Give the community time to discuss (at least 1 week for significant changes)
3. If consensus is reached, submit a PR updating this document
4. Maintainers will merge after final review

Minor clarifications and typo fixes can skip the Issue and go straight to PR.

## Questions?

- Open a GitHub Issue for questions about governance, contribution process, or project direction
- Tag a maintainer if you need help navigating the process
- Join the discussion in [Ansible community channels](https://docs.ansible.com/ansible/latest/community/communication.html)
