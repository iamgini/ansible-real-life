---
name: ansible-markdown-docs
description: >-
  Fetch Ansible documentation from docs.ansible.com as Markdown. Use when the user asks
  about an Ansible topic, references a docs.ansible.com URL, or when the agent needs to
  look up official Ansible documentation to complete a task or verify information.
user-invocable: true
triggers:
  - "get ansible documentation"
  - "docs.ansible.com"
  - "fetch ansible docs"
  - "show ansible documentation"
  - "look up ansible docs"
---

# Skill: ansible-markdown-docs

## Purpose

Fetch a page from docs.ansible.com as Markdown and use its content as context — either
to answer a user question or to inform the agent's own reasoning during a task. The raw
Markdown is context for the agent — do not dump it directly at the user.

## When to Invoke

TRIGGER when:

- The user asks about an Ansible topic that warrants looking up official documentation
- The user provides a `docs.ansible.com` URL
- The user asks to "look up", "find", or "check" something in the Ansible docs
- The agent needs to verify Ansible behaviour, syntax, or requirements while completing a task
- Another skill or workflow requires authoritative Ansible documentation as input

DO NOT TRIGGER when:

- The documentation needed is not on `docs.ansible.com`
- The question can be answered from existing context without fetching a page

## Inputs

- `url` (optional): A full `https://docs.ansible.com/...` URL.
  If omitted, the skill searches for the best matching page based on the user's topic.

## Prerequisites

- `curl` available in PATH
- Web search available for resolving topic descriptions to URLs.
  If web search is unavailable, ask the user to provide a direct `docs.ansible.com` URL.

## Workflow

### Step 1 — Resolve the URL

**If the user provided a `docs.ansible.com` URL**, use it directly and skip to Step 2.

**If the user described a topic** (e.g. "Ansible community package collections requirements"),
perform a web search scoped to docs.ansible.com to find the most relevant page:

- Search query: `site:docs.ansible.com <topic>`
- Select the most relevant result URL
- If no confident match is found, ask the user to clarify or provide a URL directly

### Step 2 — Validate the URL

Ensure the resolved URL begins with `https://docs.ansible.com/`. If it does not, refuse:

> "I can only fetch pages from `docs.ansible.com`. Please provide a valid URL or rephrase
> your topic so I can find the right page."

### Step 3 — Fetch the documentation

Run:

```bash
curl -s -m 30 <url> -H "Accept: text/markdown"
```

The `Accept: text/markdown` header instructs docs.ansible.com (powered by Read the Docs)
to return the page content as Markdown instead of HTML.

### Step 4 — Handle the response

**Success**: Use the returned Markdown as context to answer the user's question.
Summarise, quote relevant sections, and explain — do not paste the raw Markdown in full.

**Empty or HTML response**: If the response starts with `<!DOCTYPE` or `<html`, or is empty,
try an alternative URL from the search results. If all attempts fail, inform the user:

> "I wasn't able to retrieve that page as Markdown. Try providing the exact
> `docs.ansible.com` URL directly."

**curl error**: Report the error and suggest checking network connectivity or the URL.

### Step 5 — Answer conversationally

Use the fetched content to directly address what the user asked. For example:

- "Look up the Ansible community package collections requirements" →
  fetch the relevant page, then summarise the requirements clearly
- "What does the playbooks intro say about plays?" →
  fetch the playbooks intro page, then quote and explain the relevant section

Offer to fetch related pages or dig deeper if the answer is incomplete.

## Example Interactions

### Example 1: URL provided

```
User: "Get the docs at https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html"

Step 1: URL provided — use directly.
Step 2: Validate ✓
Step 3: curl -s -m 30 <url> -H "Accept: text/markdown"
Step 4: Use content as context.
Step 5: Summarise and answer.
```

### Example 2: Topic description

```
User: "Look up the Ansible community package collections requirements"

Step 1: No URL — search site:docs.ansible.com ansible community package collections requirements
        → resolves to e.g. https://docs.ansible.com/ansible/latest/community/collection_contributors/collection_requirements.html
Step 2: Validate ✓
Step 3: curl -s -m 30 <url> -H "Accept: text/markdown"
Step 4: Use content as context.
Step 5: Answer: "According to the Ansible docs, community package collections must meet the
        following requirements: ..."
```

## Notes

- Always use `curl -s -m 30` (silent mode with 30-second timeout) to suppress progress output
  and prevent hangs on network issues.
- The fetched Markdown is agent context — synthesise from it, do not print it verbatim.
- Only fetch from `docs.ansible.com`; validate before every request.
- **NEVER truncate the fetched content.** Process the full response regardless of length.
  If the content is large, save it to a temporary file and reference the path rather than
  truncating or summarising prematurely.
- **NEVER pipe the curl command to `head` or any other truncating command.** Always capture
  the full output and write it to a temporary file if needed.
