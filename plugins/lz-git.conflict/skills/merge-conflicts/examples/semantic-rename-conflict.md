# Semantic Rename Conflict Example

This example demonstrates detecting and resolving semantic conflicts caused by symbol renames.

## Scenario

Based on patterns from Microsoft Edge (ISSTA 2022 research).

**Upstream (main branch)** renamed a method for clarity:
```cpp
// Before
class BrowserContext {
  bool IsIncognito() const;
};

// After
class BrowserContext {
  bool GetIncognito() const;
};
```

**Downstream (feature branch)** added new code using the old name:
```cpp
void CheckPrivacy(BrowserContext* browser) {
  if (browser->IsIncognito()) {
    DisableTracking();
  }
}
```

## The Problem

Git merge succeeds - no conflict markers appear. But compilation fails:

```
error: no member named 'IsIncognito' in 'BrowserContext'
  if (browser->IsIncognito()) {
              ^
```

## Analysis

**Conflict Type**: Rename/Refactor (Semantic Conflict Subtype 4)

**Why Git Missed It**:
- Textually, changes are in different locations
- Git's line-based merge algorithm doesn't understand symbol relationships
- The conflict only manifests at compile/type-check time

## Detection

### Finding the Rename

Use git log to find when the rename happened:

```bash
git log --all --oneline -p -- browser_context.h | grep -A2 -B2 "IsIncognito\|GetIncognito"
```

Or search for the old symbol across branches:

```bash
git log --all --source --oneline -S "IsIncognito"
```

### Understanding the Transformation

The rename commit message or diff shows:
- `IsIncognito()` -> `GetIncognito()`
- This follows a pattern: verb prefix standardization

## Resolution

Apply the same transformation to downstream code:

```cpp
void CheckPrivacy(BrowserContext* browser) {
  if (browser->GetIncognito()) {  // Updated to match upstream rename
    DisableTracking();
  }
}
```

### Steps

1. **Find all usages of old name** in the feature branch:
   ```bash
   grep -r "IsIncognito" --include="*.cpp" --include="*.h"
   ```

2. **Apply the same transformation** to each usage

3. **Verify compilation**:
   ```bash
   # For C++
   make clean && make

   # For TypeScript
   tsc --noEmit
   ```

4. **Run tests** to verify behavior is preserved

## TypeScript/JavaScript Example

Same pattern in a TypeScript codebase:

**Upstream rename**:
```typescript
// Before: user.service.ts
export class UserService {
  async getUser(id: string): Promise<User> { ... }
}

// After: user.service.ts
export class UserService {
  async fetchUser(id: string): Promise<User> { ... }  // Renamed
}
```

**Downstream addition**:
```typescript
// feature branch: user-profile.component.ts
async loadProfile(userId: string) {
  const user = await this.userService.getUser(userId);  // Uses old name
  this.profile = user;
}
```

**Error after merge**:
```
Property 'getUser' does not exist on type 'UserService'.
  Did you mean 'fetchUser'?
```

**Resolution**:
```typescript
async loadProfile(userId: string) {
  const user = await this.userService.fetchUser(userId);  // Updated
  this.profile = user;
}
```

## Prevention

- **Use IDE refactoring tools** that update all usages automatically
- **Run CI on merge commits** to catch semantic conflicts early
- **Consider deprecation period** for significant renames:
  ```typescript
  /** @deprecated Use fetchUser instead */
  getUser(id: string): Promise<User> {
    return this.fetchUser(id);
  }
  ```

## Related Patterns

This pattern extends to:
- **Class renames**: `UserService` -> `UserRepository`
- **Module renames**: `import from './utils'` -> `import from './helpers'`
- **Type renames**: `interface UserDTO` -> `interface UserResponse`
- **Constant renames**: `MAX_RETRIES` -> `RETRY_LIMIT`

Each follows the same resolution approach: identify the transformation and apply it consistently.
