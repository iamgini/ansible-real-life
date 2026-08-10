---
name: aws-terminator-analyze
description: >-
  Use this skill when analyzing an Ansible AWS collection PR to determine what
  aws-terminator terminator classes and IAM permissions are needed. Fetches PR
  changes, checks existing terminator coverage, and generates a structured
  analysis report with implementation recommendations. Invoke for "analyze aws
  terminator", "check terminator coverage", or "what terminator classes
  needed".
allowed-tools: Read Bash(command:gh *) Bash(command:git *) Bash(command:grep *)
argument-hint: "--pr <number> [--repo <owner/repo>]"
triggers:
  - "analyze aws terminator"
  - "aws-terminator analyze"
  - "check terminator coverage"
  - "what terminator classes needed"
user-invocable: true
---

# AWS Terminator Analyze

Analyzes a pull request from an Ansible AWS collection (amazon.aws, community.aws, amazon.ai, amazon.cloud) to determine what terminator classes and IAM
permissions need to be added to the mattclay/aws-terminator repository.

## Purpose

When new AWS modules are added to Ansible collections, the aws-terminator repository needs:

1. **Terminator classes** to clean up resources created during integration tests
2. **IAM permissions** for both the integration tests and the terminators

This skill automates the analysis to identify what's needed.

## Quick Start

```bash
# Analyze a PR from community.aws
/aws-terminator-analyze --pr 2353 --repo ansible-collections/community.aws

# Analyze an amazon.aws PR (default repo)
/aws-terminator-analyze --pr 1234
```

**What it does**: Fetches the PR, identifies new AWS resource types, checks existing terminator coverage, and generates a report with implementation recommendations.

**See full documentation below** for detailed workflow steps, configuration options, and report format.

## When to Use

- Analyzing a new module PR in ansible-collections/amazon.aws or community.aws
- Reviewing changes that add new AWS resource types
- Before creating a companion aws-terminator PR
- After someone mentions "CI failures due to missing permissions"

## Usage

```bash
# Analyze a community.aws PR
/aws-terminator-analyze --pr 2353 --repo ansible-collections/community.aws

# Analyze an amazon.aws PR (default repo)
/aws-terminator-analyze --pr 1234

# Analyze with existing terminator PR reference
/aws-terminator-analyze --pr 2353 --repo ansible-collections/community.aws --terminator-pr 315
```

## Step 1: Validate Input

Check required parameters:

- `--pr <number>` is required
- `--repo <owner/repo>` defaults to `ansible-collections/community.aws`
- `--terminator-pr <number>` is optional (for checking existing terminator PR)

Valid repositories:

- `ansible-collections/amazon.aws`
- `ansible-collections/community.aws`
- `ansible-collections/amazon.ai`
- `ansible-collections/amazon.cloud`

## Step 2: Fetch PR Metadata

```bash
gh pr view <PR_NUMBER> --repo <REPO> --json title,body,files,state
```

Extract:

- PR title and description
- List of changed files
- PR state (open/closed/merged)
- Any references to existing aws-terminator PRs

## Step 3: Identify New Modules

From the file list, identify new module files:

```bash
# Get module files from PR
gh api repos/<REPO>/pulls/<PR_NUMBER>/files --paginate | \
  jq -r '.[] | select(.filename | contains("plugins/modules/")) | .filename'
```

**Extract module names**:

- `plugins/modules/foo_bar.py` → `foo_bar` (creates FooBar resources)
- `plugins/modules/foo_bar_info.py` → skip (info-only, no resources created)

**AWS service detection**:
Look for boto3 service client names in the module code:

```python
client = module.client('service-name')  # e.g., 'medialive', 'rds', 'ec2'
```

## Step 4: Analyze Resource Creation Patterns

For each module, check the patch content for resource creation calls:

```bash
gh api repos/<REPO>/pulls/<PR_NUMBER>/files --jq \
  '.[] | select(.filename == "plugins/modules/MODULE.py") | .patch'
```

**Look for create/launch/run patterns**:

```python
# Resource creation indicators
client.create_*()
client.run_*()
client.launch_*()
client.start_*()
client.register_*()
```

**Extract resource type from API calls**:

- `client.create_user_pool()` → UserPool resource
- `client.create_cluster()` → Cluster resource
- `client.run_instances()` → Instance resource

## Step 5: Check Integration Tests

Get integration test files:

```bash
gh api repos/<REPO>/pulls/<PR_NUMBER>/files --paginate | \
  jq -r '.[] | select(.filename | contains("tests/integration/targets/")) | \
    select(.filename | endswith("main.yml") or endswith("tasks.yml")) | .filename'
```

**Analyze test content** for:

- Resource creation in setup/test blocks
- Always blocks (cleanup attempts)
- Wait conditions (indicates async resources)
- Dependent resources (e.g., security groups before instances)

## Step 6: Check Existing Terminator Coverage

Clone or pull latest aws-terminator repo:

```bash
# Clone from upstream (mattclay's repo) for read-only analysis
# For implementation, you'll need your own fork
cd ~/dev/aws-terminator || git clone https://github.com/mattclay/aws-terminator.git ~/dev/aws-terminator
cd ~/dev/aws-terminator
git fetch origin
git pull origin main
```

**Search for existing terminators**:

```bash
# Search by resource type
grep -r "class.*<ResourceType>" aws/terminator/

# Example: search for MediaLive
grep -r "class MediaLive" aws/terminator/
```

**Terminator file organization**:

- `compute.py` - EC2, ASG, ELB, placement groups
- `networking.py` - VPC, subnets, security groups
- `paas.py` - Lambda, ECS, ECR, EKS
- `data_services.py` - RDS, Redshift, DynamoDB
- `storage_services.py` - S3, EFS
- `application_services.py` - SQS, SNS, SES, CloudFormation, MediaLive
- `application_security.py` - WAF, Inspector, Cognito
- `security_services.py` - IAM, KMS, STS

## Step 7: Check Existing IAM Permissions

**Search for permissions**:

```bash
cd ~/dev/aws-terminator
grep -r "service:Action" aws/policy/
```

**Policy file organization** (same as terminator files):

- `compute.yaml`
- `networking.yaml`
- `paas.yaml`
- `data-services.yaml`
- `storage-services.yaml`
- `application-services.yaml`
- `application-security.yaml`
- `security-services.yaml`

## Step 8: Determine What's Needed

### Terminator Classes Needed

For each resource type, determine if a terminator is needed:

**YES if**:

- ✅ Resource is created by modules or integration tests
- ✅ Resource persists after test (not auto-deleted)
- ✅ No existing terminator class found

**NO if**:

- ❌ Resource is auto-deleted with parent (e.g., Cognito clients with user pools)
- ❌ Resource is ephemeral (auto-expires)
- ❌ Terminator already exists

### Terminator Base Class Selection

**Use `Terminator` base class if**:

- Resource API response has a timestamp field (`CreatedTime`, `LaunchTime`, `StartTime`, `CreationDate`)

**Use `DbTerminator` base class if**:

- Resource has NO creation timestamp field

### IAM Permissions Needed

Determine required permissions:

**From integration tests**:

- Create/Modify/Delete operations from test tasks
- Describe/List operations for idempotency checks

**From terminators**:

- Describe/List operations (for discovering resources)
- Delete operations (for cleanup)
- Any prerequisite operations (e.g., stop before delete)

## Step 9: Check for Existing Terminator PR

If `--terminator-pr` is provided, fetch and analyze:

```bash
gh pr view <TERMINATOR_PR> --repo mattclay/aws-terminator --json title,body,files,state
```

Compare:

- What terminators are in the existing PR
- What permissions are in the existing PR
- What's missing from the existing PR

## Step 10: Generate Analysis Report

Output a structured report:

````markdown
## AWS Terminator Analysis for <REPO> PR #<NUMBER>

**PR Title**: <title>
**PR URL**: https://github.com/<REPO>/pull/<NUMBER>
**Status**: <open/merged/closed>

### Resources Being Added

**New modules**:
1. `module_name` - Creates ResourceType resources using `service-name` boto3 client
2. `another_module` - Creates AnotherResource resources

**Integration test targets**:
- `target_name` - Creates X, Y, Z resources in setup
- `another_target` - Creates A, B resources

### Terminator Coverage Analysis

| Resource Type | Existing Terminator | Status | Recommended File |
|--------------|---------------------|--------|------------------|
| FooResource | ❌ None | **Need to create** | `application_services.py` |
| BarResource | ✅ `BarResource` | **Covered** | N/A |
| BazResource | ⚠️ `BazTerminator` (partial) | **Needs update** | `networking.py` |

### Terminator Classes Needed

#### 1. FooResource

**File**: `aws/terminator/application_services.py`
**Base class**: `Terminator` (has `CreatedTime` field)

**Required properties**:
- `id` - from `FooId` field
- `name` - from `FooName` field
- `created_time` - from `CreatedTime` field

**Terminate method**:
```python
def terminate(self):
    self.client.delete_foo(FooId=self.id)
```

**Notes**:
- Uses boto3 service `service-name`
- List operation: `client.list_foos()['Foos']`
- May need pagination if list can exceed API limits

#### 2. BarChildResource (if needed)

**Analysis**: BarChild resources are auto-deleted when parent BarResource is deleted.
**Recommendation**: **No separate terminator needed**

### IAM Permission Analysis

| Permission | Existing | Status | Recommended File |
|-----------|----------|--------|------------------|
| `service:CreateFoo` | ❌ None | **Need to add** | `application-services.yaml` |
| `service:DeleteFoo` | ❌ None | **Need to add** | `application-services.yaml` |
| `service:DescribeFoo` | ❌ None | **Need to add** | `application-services.yaml` |
| `service:ListFoos` | ❌ None | **Need to add** | `application-services.yaml` |
| `service:UpdateFoo` | ✅ Present | **Covered** | N/A |

### IAM Permissions Needed

**Add to** `aws/policy/application-services.yaml`:

```yaml
- Sid: ServiceNamePermissions
  Effect: Allow
  Action:
    - service:CreateFoo
    - service:DeleteFoo
    - service:DescribeFoo
    - service:UpdateFoo
    - service:TagResource
    - service:UntagResource
  Resource:
    - 'arn:aws:service:{{ aws_region }}:{{ aws_account_id }}:foo/*'

- Sid: ServiceNameListPermissions
  Effect: Allow
  Action:
    - service:ListFoos
  Resource:
    - '*'
```

### Existing Terminator PR Status

**aws-terminator PR #<NUMBER>**: <URL>
**Status**: <open/merged/closed>

**Coverage**:
- ✅ FooResource terminator implemented
- ✅ IAM permissions added
- ❌ Missing BazResource terminator

**Recommendation**:
[COMPLETE | NEEDS UPDATES | MISSING]

### Next Steps

**If no terminator PR exists**:
1. Fork mattclay/aws-terminator on GitHub (if not already forked)
2. Clone your fork to ~/dev/aws-terminator
3. Use `/aws-terminator-implement` to generate classes and permissions
4. Test locally with `python cleanup.py --target FooResource -v -c`
5. Push to your fork and submit PR to mattclay/aws-terminator

**If terminator PR exists but incomplete**:
1. Checkout PR branch: `gh pr checkout <PR_NUMBER> --repo mattclay/aws-terminator`
2. Add missing terminators/permissions
3. Update PR

**If terminator PR is complete**:
- ✅ Ready for merge
- CI failures in ansible PR should resolve after terminator PR merges

### References

- aws-terminator repository: https://github.com/mattclay/aws-terminator
- Ansible Collection PR: https://github.com/<REPO>/pull/<NUMBER>
- aws-terminator PR: https://github.com/mattclay/aws-terminator/pull/<NUMBER> (if exists)

---
*Analysis generated by /aws-terminator-analyze skill*
````

## Output Format

Present the analysis in a clear, structured format with:

- Summary of resources being added
- Terminator coverage status (✅ covered, ❌ missing, ⚠️ partial)
- Specific code recommendations for missing terminators
- IAM permission recommendations
- Status of existing terminator PR (if referenced)
- Clear next steps

## Configuration

Optional environment variables:

```bash
# Local aws-terminator path (defaults to ~/dev/aws-terminator)
export AWS_TERMINATOR_PATH="~/custom/path"
```

If not set, the skill uses `~/dev/aws-terminator` as the default location.

**Note**: This skill clones mattclay/aws-terminator for read-only analysis. For implementation, use `/aws-terminator-implement` which requires your fork.

## Error Handling

**PR not found**:

```
Error: PR #<NUMBER> not found in <REPO>
Check the PR number and repository name.
```

**Not an AWS collection**:

```
Error: <REPO> is not an AWS collection repository
This skill only works with:
- ansible-collections/amazon.aws
- ansible-collections/community.aws
- ansible-collections/amazon.ai
- ansible-collections/amazon.cloud
```

**No module changes**:

```
No new modules found in PR #<NUMBER>
This PR does not add or modify modules in plugins/modules/
No terminator changes needed.
```

## Related Skills

- `/aws-terminator-implement` - Implement terminator classes and permissions based on this analysis
- `/pr-review` - General PR review (use this for AWS terminator analysis)

## References

- aws-terminator repository: https://github.com/mattclay/aws-terminator
- Ansible Cloud Content Handbook: https://github.com/ansible-collections/cloud-content-handbook
- Ansible Collection PRs: GitHub PRs in aws collections
