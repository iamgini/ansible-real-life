# Terminator Class Implementation

For each resource type, generate and add the terminator class.

## Determine Base Class

**Read resource describe output** to check for timestamp field:

```bash
# If analysis includes example API response, check for:
# CreatedTime, LaunchTime, StartTime, CreationDate, CreatedAt, etc.
```

**Decision**:

- Has timestamp → use `Terminator` base class
- No timestamp → use `DbTerminator` base class

## Generate Terminator Class Code

**Template for `Terminator` base class**:

```python
class <ResourceType>Terminator(Terminator):
    @staticmethod
    def create(credentials):
        def get_<resource_type_snake_case>(client):
            # Use paginator if API supports it and can return >default limit
            # Otherwise use simple list call
            <list_call> = client.<list_operation>()<'ResponseKey'>
            return <list_call>

        return Terminator._create(
            credentials,
            <ResourceType>Terminator,
            '<boto3-service-name>',
            get_<resource_type_snake_case>
        )

    @property
    def id(self):
        return self.instance['<IdField>']

    @property
    def name(self):
        # Prefer Name field, fallback to id
        return self.instance.get('<NameField>', self.id)

    @property
    def created_time(self):
        return self.instance['<CreatedTimeField>']

    def terminate(self):
        # Add any pre-delete requirements (e.g., stop, detach)
        # Then delete
        self.client.<delete_operation>(<IdParam>=self.id)
```

**Template for `DbTerminator` base class**:

```python
class <ResourceType>Terminator(DbTerminator):
    @staticmethod
    def create(credentials):
        def get_<resource_type_snake_case>(client):
            <list_call> = client.<list_operation>()<'ResponseKey'>
            return <list_call>

        return Terminator._create(
            credentials,
            <ResourceType>Terminator,
            '<boto3-service-name>',
            get_<resource_type_snake_case>
        )

    @property
    def name(self):
        return self.instance['<NameField>']

    def terminate(self):
        self.client.<delete_operation>(<NameParam>=self.name)
```

## Add Class to Terminator File

**Locate insertion point**:

```bash
cd ~/dev/aws-terminator
# Read the appropriate terminator file
# Classes are typically alphabetically ordered
# Insert new class in alphabetical position
```

**Use Edit tool** to add the class:

- Read the terminator file
- Find insertion point (alphabetically by class name)
- Insert the new class code

## Handle Special Cases

**Pagination required**:

```python
def get_resources(client):
    paginator = client.get_paginator('list_resources')
    resources = paginator.paginate(MaxResults=100).build_full_result()['Resources']
    return resources
```

**Filter by account owner**:

```python
from aws.terminator.util import get_account_id

def get_resources(client):
    account = get_account_id(credentials)
    return client.describe_resources(OwnerIds=[account])['Resources']
```

**Flattening nested lists**:

```python
def get_resources(client):
    return [item for group in client.describe_groups()['Groups']
            for item in group['Items']]
```

**Pre-delete operations**:

```python
def terminate(self):
    # Example: Stop resource before deleting
    if self.instance['State'] != 'stopped':
        self.client.stop_resource(ResourceId=self.id)
        # Wait for stopped state if needed

    self.client.delete_resource(ResourceId=self.id)
```

**Ignore terminated/deleted resources**:

```python
@property
def ignore(self):
    return self.instance['State'] in ['terminated', 'deleted']
```

**Custom age limit**:

```python
@property
def age_limit(self):
    # Default is 20 minutes
    # Override for resources that need longer to provision
    return datetime.timedelta(minutes=50)
```
