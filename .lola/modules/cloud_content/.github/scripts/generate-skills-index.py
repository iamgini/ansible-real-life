#!/usr/bin/env python3
"""Generate SKILLS.md index from all SKILL.md files in the repository."""

import yaml
from pathlib import Path
from datetime import datetime, timezone


def extract_frontmatter(skill_file: Path) -> dict | None:
    """Extract YAML frontmatter from a SKILL.md file."""
    content = skill_file.read_text()
    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def get_module_name(skill_path: Path) -> str:
    """Extract module name from skill path."""
    parts = skill_path.parts
    for i, part in enumerate(parts):
        if part == 'module' and i > 0:
            return parts[i - 1]
    return 'unknown'


def generate_skills_index(repo_root: Path) -> str:
    """Generate the SKILLS.md content."""
    skills_by_module: dict[str, list[dict]] = {}

    for skill_file in repo_root.glob('*/module/skills/*/SKILL.md'):
        fm = extract_frontmatter(skill_file)
        if not fm:
            continue

        module = get_module_name(skill_file)
        skill_name = fm.get('name', skill_file.parent.name)
        description = fm.get('description', 'No description')
        if isinstance(description, str):
            description = ' '.join(description.split())

        rel_path = skill_file.relative_to(repo_root)

        if module not in skills_by_module:
            skills_by_module[module] = []

        skills_by_module[module].append({
            'name': skill_name,
            'description': description,
            'path': str(rel_path),
        })

    for skills in skills_by_module.values():
        skills.sort(key=lambda s: s['name'])

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    lines = [
        '# Skills Index',
        '',
        '> Auto-generated from SKILL.md files. Do not edit manually.',
        f'> Last updated: {timestamp}',
        '',
    ]

    for module in sorted(skills_by_module.keys()):
        skills = skills_by_module[module]
        lines.append(f'## {module}')
        lines.append('')
        lines.append('| Skill | Description |')
        lines.append('|-------|-------------|')
        for skill in skills:
            link = f"[{skill['name']}]({skill['path']})"
            lines.append(f"| {link} | {skill['description']} |")
        lines.append('')

    total = sum(len(s) for s in skills_by_module.values())
    lines.append('---')
    lines.append(f'Total skills: {total}')
    lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    repo_root = Path('.')
    content = generate_skills_index(repo_root)
    Path('SKILLS.md').write_text(content)
    print('Generated SKILLS.md')
