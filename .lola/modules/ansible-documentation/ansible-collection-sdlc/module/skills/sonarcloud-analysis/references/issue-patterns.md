# Common Issue Patterns and Guidance

## Weak Cryptography (python:S2245)

**Pattern:** Using `random` module for security-sensitive operations

**Fix:**

- If cryptographic randomness is needed: Use `secrets` module
- If randomness is for hashing but not cryptographic purposes: Add `usedforsecurity=False` parameter (SonarCloud recognises this)
- If not security-sensitive (e.g., generating unique IDs): Mark as SAFE with justification

**Example with usedforsecurity=False:**

```python
# For MD5 hash used for non-cryptographic purposes (e.g., checksums, cache keys)
hashlib.md5(data, usedforsecurity=False).hexdigest()
```

This parameter explicitly indicates to both Python and SonarCloud that the hash is not being used for security purposes.

## HTTP URLs (encrypt-data)

**Pattern:** Using HTTP instead of HTTPS

**Fix:**

- If HTTP is required (e.g., AWS metadata endpoint `http://169.254.169.254`): Mark as SAFE
- Otherwise: Change to HTTPS

## Cognitive Complexity (python:S3776)

**Pattern:** Functions with deeply nested logic

**Fix:**

- Extract nested logic into helper functions
- Simplify conditional statements
- Prioritise extracting logic that can be unit tested

## Duplicate Strings (python:S1192)

**Pattern:** Magic strings repeated multiple times

**Fix:**

- Extract into named constants
- Use descriptive constant names
- Group related constants

## Generic Exceptions (python:S112)

**Pattern:** Raising or catching generic `Exception`

**Fix:**

- Use specific exception types
- Create custom exception classes for domain-specific errors

## Duplicate Branches (python:S1862)

**Pattern:** Identical code in different conditional branches

**Fix:**

- Refactor to eliminate duplication
- Verify whether different conditions should have different logic
