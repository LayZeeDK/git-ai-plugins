# Conflict Pattern Catalog

Comprehensive catalog of merge conflict patterns and their resolution strategies.

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
