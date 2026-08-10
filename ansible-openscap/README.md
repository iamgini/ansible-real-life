# Ansible OpenSCAP

This project has been superseded by the **ansible-collection-compliance** project, which provides a complete Ansible collection (`iamgini.compliance`) for OpenSCAP-based compliance scanning and remediation.

See: [ansible-collection-compliance](../../ansible-collection-compliance/)

Features of the new project:

- OpenSCAP scanning with multiple execution modes (direct, EE, agentless)
- CIS and STIG profile support with custom profile overlays
- Automated fix generation from scan results
- Report collection and push to central report servers
- Exception management for known acceptable findings
- Molecule-based testing (container and full VM scenarios)
- Dashboard integration via ansible-dashboard-reporting
