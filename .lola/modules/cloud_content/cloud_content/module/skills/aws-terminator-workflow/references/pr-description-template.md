# PR Description Template

Create comprehensive PR body:

````markdown
# Add <service> terminators and permissions

This PR adds comprehensive support for AWS <ServiceName> resources created by the Ansible <collection> collection.

## Related Ansible Collection PR

ansible-collections/<collection>#<PR_NUMBER>: <PR_TITLE>

## Changes

### Terminator Classes Added

**File**: `aws/terminator/<terminator-file>.py`

<For each terminator class>
- **<ResourceType>Terminator** - Handles <resource> lifecycle
  - Base class: `Terminator` | `DbTerminator`
  - List operation: `client.<list_operation>()`
  - Delete operation: `client.<delete_operation>()`
  - Special handling: [None | Pagination | Pre-delete stop | Child dependencies]

### IAM Permissions Added

**File**: `aws/policy/<policy-file>.yaml`

<For each permission block>
- **<ServiceName><ResourceType>Permissions** - Resource-scoped actions
  - Actions: <service>:Create*, Delete*, Describe*, Update*
  - Resources: `arn:aws:<service>:region:account:<resource-type>/*`

- **<ServiceName>GlobalPermissions** - List/Describe actions
  - Actions: <service>:List*, Describe*
  - Resources: `*`

## Testing

### Tox Validation

- ✅ pycodestyle: Passed
- ✅ pylint: Passed
- ✅ yamllint: Passed
- ✅ policy: Passed

### Manual Testing

<If manual testing was performed>
```bash
# Created test resources in AWS account
# Ran terminator in check mode
python cleanup.py --stage dev --target <ResourceType>Terminator -v -c

# Output:
cleanup: DEBUG located <ResourceType>Terminator: count=X
cleanup: DEBUG checked <ResourceType>Terminator: stale=True
```

## Implementation Notes

<Any special considerations>
- Child resources (e.g., <ChildType>) are auto-deleted with parent → no separate terminator needed
- <ResourceType> requires stop-before-delete logic
- Pagination required for <ListOperation> (can exceed default limit)

## Deployment Checklist

After merge:
- [ ] Deploy permissions: `make test_policy STAGE=dev`
- [ ] Test with ansible-test: `ansible-test integration <module> --remote-stage dev`
- [ ] Deploy to prod: `make test_policy STAGE=prod`
- [ ] Deploy lambda (if terminator classes changed): `make terminator_lambda`

## References

- Analysis: [Include analysis output or link]
- Ansible collection PR: https://github.com/ansible-collections/<collection>/pull/<PR_NUMBER>
- AWS <ServiceName> API docs: https://docs.aws.amazon.com/...
````
