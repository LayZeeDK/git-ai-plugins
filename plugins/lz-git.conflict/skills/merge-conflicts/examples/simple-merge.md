# Simple Merge Conflict Resolution Example

This example walks through resolving a typical merge conflict.

## Scenario

You're on the `main` branch and merging `feature/user-profile`:

```bash
git merge feature/user-profile
# Auto-merging src/user.ts
# CONFLICT (content): Merge conflict in src/user.ts
# Automatic merge failed; fix conflicts and then commit the result.
```

## Step 1: Create Backup Branch

```bash
git rev-parse --abbrev-ref HEAD
# main

git branch lz-git/conflict/main/backup-20240115-143022Z
```

## Step 2: Identify Conflicts

```bash
git diff --name-only --diff-filter=U
# src/user.ts
```

## Step 3: Read the Conflicted File

```typescript
// src/user.ts
import { Database } from './database';
<<<<<<< HEAD
import { Logger } from './logger';
=======
import { Validator } from './validator';
>>>>>>> feature/user-profile

export interface User {
  id: string;
  name: string;
<<<<<<< HEAD
  email: string;
  createdAt: Date;
=======
  email: string;
  phone?: string;
>>>>>>> feature/user-profile
}

export class UserService {
  constructor(private db: Database) {}

<<<<<<< HEAD
  async createUser(name: string, email: string): Promise<User> {
    Logger.info(`Creating user: ${name}`);
    const user: User = {
      id: crypto.randomUUID(),
      name,
      email,
      createdAt: new Date()
    };
=======
  async createUser(name: string, email: string, phone?: string): Promise<User> {
    Validator.validateEmail(email);
    const user: User = {
      id: crypto.randomUUID(),
      name,
      email,
      phone
    };
>>>>>>> feature/user-profile
    return this.db.save('users', user);
  }
}
```

## Step 4: Analyze Each Conflict

### Conflict 1: Import Statements

- **HEAD**: Added `Logger` import
- **feature/user-profile**: Added `Validator` import
- **Resolution**: Include both imports

### Conflict 2: User Interface

- **HEAD**: Added `createdAt: Date`
- **feature/user-profile**: Added `phone?: string`
- **Resolution**: Include both properties

### Conflict 3: createUser Method

- **HEAD**: Added logging with `Logger.info()`
- **feature/user-profile**: Added validation and `phone` parameter
- **Resolution**: Combine logging, validation, and phone parameter

## Step 5: Apply Resolution

```typescript
// src/user.ts
import { Database } from './database';
import { Logger } from './logger';
import { Validator } from './validator';

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  createdAt: Date;
}

export class UserService {
  constructor(private db: Database) {}

  async createUser(name: string, email: string, phone?: string): Promise<User> {
    Logger.info(`Creating user: ${name}`);
    Validator.validateEmail(email);
    const user: User = {
      id: crypto.randomUUID(),
      name,
      email,
      phone,
      createdAt: new Date()
    };
    return this.db.save('users', user);
  }
}
```

## Step 6: Validate

Check that:
- All conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) are removed
- Code is syntactically valid
- Both features (logging + validation) are present
- TypeScript types are consistent

## Step 7: Complete Merge

```bash
git add src/user.ts
git commit -m "Merge feature/user-profile: combine logging and validation"
```

## Result

The merge successfully combined:
- Logger import and usage from `main`
- Validator import and usage from `feature/user-profile`
- Both new User properties (`createdAt` and `phone`)
- Both new features in `createUser` method
