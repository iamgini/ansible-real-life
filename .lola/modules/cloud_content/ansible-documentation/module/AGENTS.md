# Ansible Documentation

Module provides skills and workflows for working with Ansible documentation at docs.ansible.com.

## When to Use

### Skills

- **ansible-markdown-docs skill**: Use the `ansible-markdown-docs` skill to fetch and render Ansible
  documentation from docs.ansible.com using the `Accept: text/markdown` header.
  Invoke when the user asks to "Get Ansible documentation", provides a `docs.ansible.com`
  URL, or asks to "fetch", "show", or "look up" Ansible docs.

## Configuration

**Required Dependencies:**

- `curl` — Used to fetch documentation pages from docs.ansible.com

## Notes

- Documentation is fetched using the `Accept: text/markdown` header, which instructs
  Read the Docs to return page content as Markdown instead of HTML.
- Only pages on `docs.ansible.com` are supported; the skill validates the URL before fetching.
