# IAM Permission Implementation

## Determine Policy Structure

**Permissions are grouped into blocks**:

1. **Resource-scoped permissions** - Actions on specific ARNs
2. **Global permissions** - List/Describe actions that require `Resource: "*"`

## Generate Permission Blocks

**Resource-scoped permission block**:

```yaml
- Sid: <ServiceName><ResourceType>Permissions
  Effect: Allow
  Action:
    - <service>:Create<Resource>
    - <service>:Delete<Resource>
    - <service>:Describe<Resource>
    - <service>:Update<Resource>
    - <service>:Tag Resource
    - <service>:UntagResource
  Resource:
    - 'arn:aws:<service>:{{ aws_region }}:{{ aws_account_id }}:<resource-type>/*'
```

**Global permission block**:

```yaml
- Sid: <ServiceName><ResourceType>GlobalPermissions
  Effect: Allow
  Action:
    - <service>:List<Resources>
    - <service>:Describe<Resource>  # If doesn't require resource ARN
  Resource:
    - '*'
```

## Add Permissions to Policy File

**Locate policy file**:

```bash
cd ~/dev/aws-terminator
# Read aws/policy/<appropriate-file>.yaml
```

**Use Edit tool** to add permissions:

- Find appropriate insertion point (alphabetically by Sid)
- Insert new permission blocks
- Ensure no duplicate permissions (check existing blocks first)

## Permission Best Practices

**Least privilege**:

- Only add actions actually used by tests or terminators
- Avoid wildcards like `Delete*` unless necessary
- Scope resources to specific ARN patterns

**Action naming patterns**:

```yaml
# Prefer explicit actions
- service:CreateFoo
- service:DeleteFoo
- service:DescribeFoo

# Over wildcards
- service:*  # Too broad
```

**Resource ARN patterns**:

```yaml
# Specific resource type
Resource:
  - 'arn:aws:service:{{ aws_region }}:{{ aws_account_id }}:foo/*'

# Multiple resource types
Resource:
  - 'arn:aws:service:{{ aws_region }}:{{ aws_account_id }}:foo/*'
  - 'arn:aws:service:{{ aws_region }}:{{ aws_account_id }}:bar/*'

# Global (only for List/Describe)
Resource:
  - '*'
```
