# Conflict Pattern Catalog

Comprehensive catalog of merge conflict patterns and their resolution strategies.

## Conflict Type Taxonomy

Git merge conflicts fall into two primary categories based on academic research (ISSTA 2022, Ghiotto et al. 2018):

### Textual Conflicts (Immediate Detection)

Git's merge algorithm cannot automatically combine the changes. Conflict markers appear in the file immediately after the merge attempt.

**Key Statistics** (from Ghiotto et al., 175,805 conflicting chunks analyzed):
- 87% of conflicts resolved without writing new code
- 75% resolved by simply choosing one version
- 94% of chunks have <50 lines of code per version
- Median chunk size: 2-2.5 lines

### Semantic Conflicts (Delayed Detection)

Git merge succeeds textually, but the result is broken - compiler errors, failing tests, or runtime bugs. Research shows semantic conflicts are 26x more likely to introduce bugs than textual conflicts.

---

## Textual Conflict Subtypes

### 1. Content Conflicts

Same code region modified on both branches.

**Complexity**: Medium

**Example**: Both branches update a configuration value
```
<<<<<<< HEAD
const CONNECTION_TIMEOUT = 5000;
=======
const CONNECTION_TIMEOUT = 30000;
>>>>>>> feature/slow-networks
```

**Resolution**: Understand the intent behind each change. If slow-network support requires longer timeout, use the higher value. Consider if the change should be configurable instead.

### 2. Disjoint Conflicts

Parallel additions to the same collection or structure.

**Complexity**: Low

**Example**: Both branches add to an export list
```
<<<<<<< HEAD
export { validateInput, sanitizeHtml };
=======
export { validateInput, parseMarkdown };
>>>>>>> feature/markdown
```

**Resolution**: Include both additions - they don't conflict semantically:
```javascript
export { validateInput, sanitizeHtml, parseMarkdown };
```

### 3. Whitespace/Formatting Conflicts

Non-functional formatting differences.

**Complexity**: Low

**Example**: Different indentation styles, trailing whitespace, line endings

**Resolution**: Run project formatter (Prettier, eslint --fix, etc.) after resolving content. For pure whitespace conflicts, prefer incoming version for consistency.

---

## Semantic Conflict Subtypes

These conflicts don't produce conflict markers - they're detected through compilation, type checking, or test failures after the merge completes.

### 4. Rename/Refactor Conflicts

Symbol renamed upstream while downstream adds new usages of old name.

**Complexity**: Medium-High

**Example** (from Microsoft Edge - ISSTA 2022):
- Upstream: `IsIncognito()` renamed to `GetIncognito()`
- Downstream: New code calls `browser->IsIncognito()`
- Merge succeeds, but compilation fails: "no member named IsIncognito()"

**Detection**: Compiler error referencing undefined symbol that existed before merge

**Resolution**: Apply the same rename transformation to downstream code. Use `git log --all --oneline -- <file>` to find the rename commit and understand the transformation.

### 5. Complex Transformation Conflicts

Multiple simultaneous changes to types, naming conventions, or APIs.

**Complexity**: High

**Example** (from Microsoft Edge - ISSTA 2022):
```cpp
// Before (upstream)
PermissionRequestType::PERMISSION_NOTIFICATIONS

// After (upstream) - type AND constant renamed
RequestType::kNotifications
```

Downstream code using `PermissionRequestType::PERMISSION_CAMERA_PAN_TILT_ZOOM` must become `RequestType::kCameraPanTiltZoom`.

**Resolution**: Identify the transformation pattern (both type rename and constant naming convention change) and apply consistently to all downstream usages.

### 6. API Signature Conflicts

Method parameters or return types changed upstream.

**Complexity**: High

**Example**:
- Upstream: `fetchUser(id)` changed to `fetchUser(id, options)`
- Downstream: Added new calls to `fetchUser(id)`
- Merge succeeds, but type checker fails

**Detection**: Type errors about missing arguments or incompatible types

**Resolution**: Update downstream call sites to match new signature. May require understanding what the new parameter does to provide correct values.

### 7. Structural/File Move Conflicts

File reorganization conflicts with content changes.

**Complexity**: High

**Example**:
- Branch A: Renames `src/utils.ts` to `src/helpers/string-utils.ts`
- Branch B: Adds new function to `src/utils.ts`
- Merge: New function may end up in wrong location or be lost

**Detection**: Missing exports, file not found errors, or silently lost changes

**Resolution**: Use `git log --follow` to track file origin, apply changes to new location. Verify all changes from both branches are preserved.

### 8. Entangled Conflicts

Multiple developers' changes intertwined across function signatures, bodies, and call sites. Research shows these involve median of 4 developers and are 26x more likely to have bugs.

**Complexity**: Very High

**Example**: Function signature, implementation, and multiple callers all modified differently across branches.

**Resolution**: Flag for careful human review. Do not auto-resolve. Consider breaking the resolution into smaller, verifiable steps. May require understanding the full intent of all changes involved.

---

## Code Conflicts

### Import Statement Conflicts

**Pattern**: Both branches added imports to the same location.

```javascript
<<<<<<< HEAD
import { UserService } from './user.service';
import { AuthGuard } from './auth.guard';
=======
import { UserService } from './user.service';
import { LogService } from './log.service';
>>>>>>> feature/logging
```

**Resolution**: Union of all unique imports, sorted:

```javascript
import { AuthGuard } from './auth.guard';
import { LogService } from './log.service';
import { UserService } from './user.service';
```

### Function Body Conflicts

**Pattern**: Both branches modified the same function differently.

```typescript
<<<<<<< HEAD
function processUser(user: User) {
  validateUser(user);
  user.lastAccess = new Date();
  return saveUser(user);
}
=======
function processUser(user: User) {
  validateUser(user);
  logUserAccess(user);
  return saveUser(user);
}
>>>>>>> feature/audit
```

**Resolution**: Analyze intent and combine:

```typescript
function processUser(user: User) {
  validateUser(user);
  user.lastAccess = new Date();
  logUserAccess(user);
  return saveUser(user);
}
```

### Function Signature Conflicts

**Pattern**: Both branches changed the function signature.

```python
<<<<<<< HEAD
def create_user(name: str, email: str, role: str = "user") -> User:
=======
def create_user(name: str, email: str, active: bool = True) -> User:
>>>>>>> feature/user-status
```

**Resolution**: Combine parameters (check usage throughout codebase):

```python
def create_user(name: str, email: str, role: str = "user", active: bool = True) -> User:
```

### Class Property Conflicts

**Pattern**: Both branches added properties to the same class.

```typescript
<<<<<<< HEAD
class User {
  id: string;
  name: string;
  createdAt: Date;
}
=======
class User {
  id: string;
  name: string;
  updatedAt: Date;
}
>>>>>>> feature/timestamps
```

**Resolution**: Include both additions:

```typescript
class User {
  id: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### Conditional Logic Conflicts

**Pattern**: Both branches modified conditional logic.

```javascript
<<<<<<< HEAD
if (user.isAdmin || user.isModerator) {
  return allowAccess();
}
=======
if (user.isAdmin && user.isVerified) {
  return allowAccess();
}
>>>>>>> feature/verification
```

**Resolution**: Requires understanding requirements - cannot auto-merge. Flag for human review with explanation:

> This conflict involves business logic changes that may conflict:
> - Branch HEAD added moderator access
> - Branch feature/verification added verification requirement
>
> Cannot automatically determine correct logic. Please clarify intended behavior.

## Configuration Conflicts

### package.json Dependencies

**Pattern**: Both branches updated dependencies.

```json
<<<<<<< HEAD
"dependencies": {
  "lodash": "^4.17.21",
  "axios": "^1.4.0",
  "react": "^18.2.0"
}
=======
"dependencies": {
  "lodash": "^4.17.21",
  "axios": "^1.5.0",
  "date-fns": "^2.30.0"
}
>>>>>>> feature/dates
```

**Resolution**: Merge dependencies, take higher versions:

```json
"dependencies": {
  "axios": "^1.5.0",
  "date-fns": "^2.30.0",
  "lodash": "^4.17.21",
  "react": "^18.2.0"
}
```

### tsconfig.json Compiler Options

**Pattern**: Both branches modified compiler options.

```json
<<<<<<< HEAD
"compilerOptions": {
  "strict": true,
  "noImplicitAny": true,
  "target": "ES2020"
}
=======
"compilerOptions": {
  "strict": true,
  "esModuleInterop": true,
  "target": "ES2022"
}
>>>>>>> feature/modules
```

**Resolution**: Merge options, prefer newer target:

```json
"compilerOptions": {
  "strict": true,
  "noImplicitAny": true,
  "esModuleInterop": true,
  "target": "ES2022"
}
```

### Environment Variables

**Pattern**: Both branches added different env vars.

```env
<<<<<<< HEAD
DATABASE_URL=postgres://localhost:5432/app
REDIS_URL=redis://localhost:6379
=======
DATABASE_URL=postgres://localhost:5432/app
API_KEY=your-api-key-here
>>>>>>> feature/external-api
```

**Resolution**: Include all unique variables:

```env
DATABASE_URL=postgres://localhost:5432/app
REDIS_URL=redis://localhost:6379
API_KEY=your-api-key-here
```

## Structural Conflicts

### File Rename vs Modification

**Scenario**: One branch renamed a file, another modified it.

**Detection**: Git may not auto-detect this. Look for:
- Deleted file with modifications in one branch
- New file with similar content in another

**Resolution**:
1. Identify the rename
2. Apply modifications to the renamed file
3. Ensure no duplicate code

### Directory Structure Changes

**Scenario**: One branch moved files to new directory, another modified them.

**Resolution**:
1. Identify moved files
2. Apply changes to files in new location
3. Update import paths throughout codebase

## Edge Cases

### Whitespace-Only Conflicts

**Pattern**: Changes are only formatting/whitespace.

**Resolution**: Choose incoming version for consistency, unless current branch has specific formatting requirements.

### Comment Conflicts

**Pattern**: Both branches modified comments.

**Resolution**: Combine information from both comments if both add value. Otherwise, prefer more recent/accurate comment.

### Generated Code Conflicts

**Pattern**: Conflicts in auto-generated files.

**Resolution**: Regenerate the file rather than manual merge:
- Lock files: delete and regenerate
- Build outputs: rebuild
- Generated types: run generation script

### Binary File Conflicts

**Pattern**: Conflicts in binary files (images, etc.).

**Resolution**: Cannot merge binary files. Choose one version:
- For assets: prefer incoming unless current has intentional updates
- For compiled files: regenerate from source
