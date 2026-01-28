# Complex Rebase Conflict Resolution Example

This example demonstrates resolving conflicts during an interactive rebase with multiple conflicting commits.

## Scenario

You're rebasing `feature/api-refactor` onto `main` after main received several updates:

```bash
git checkout feature/api-refactor
git rebase main
# Auto-merging src/api/client.ts
# CONFLICT (content): Merge conflict in src/api/client.ts
# Auto-merging src/api/types.ts
# CONFLICT (content): Merge conflict in src/api/types.ts
# error: could not apply abc1234... Refactor API client
```

## Step 1: Create Backup Branch

```bash
git rev-parse --abbrev-ref HEAD
# feature/api-refactor

git branch lz-git/conflict/feature/api-refactor/backup-20240115-160045Z
```

## Step 2: Understand the Rebase State

Check rebase progress:
```bash
git rebase --show-current-patch
# Shows the commit being applied

ls .git/rebase-merge/
# Shows rebase state files
```

**Important Rebase Context:**
- In rebase, `HEAD` is the branch you're rebasing *onto* (main)
- The "incoming" section contains your commits being replayed
- This is the reverse of merge conflicts!

## Step 3: Identify All Conflicts

```bash
git diff --name-only --diff-filter=U
# src/api/client.ts
# src/api/types.ts
```

## Step 4: Resolve First File (client.ts)

### Read the Conflicted File

```typescript
// src/api/client.ts
<<<<<<< HEAD
import { ApiConfig, ApiResponse, ErrorHandler } from './types';
import { Logger } from '../utils/logger';

export class ApiClient {
  private config: ApiConfig;
  private errorHandler: ErrorHandler;
  private logger: Logger;

  constructor(config: ApiConfig) {
    this.config = config;
    this.errorHandler = new ErrorHandler();
    this.logger = new Logger('ApiClient');
  }

  async request<T>(endpoint: string): Promise<ApiResponse<T>> {
    this.logger.info(`Request: ${endpoint}`);
=======
import { ApiConfig, ApiResponse } from './types';

export class ApiClient {
  private config: ApiConfig;
  private retryCount: number;

  constructor(config: ApiConfig, retryCount = 3) {
    this.config = config;
    this.retryCount = retryCount;
  }

  async request<T>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
>>>>>>> abc1234 (Refactor API client)
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`);
      // ... rest of implementation
```

### Analysis

| Aspect | HEAD (main) | Incoming (feature branch) |
|--------|-------------|---------------------------|
| Imports | Added ErrorHandler, Logger | Original imports |
| Properties | errorHandler, logger | retryCount |
| Constructor | Takes config, creates handlers | Takes config + retryCount |
| request() | Has logging | Has options parameter |

### Resolution Strategy

Combine both sets of changes:
- Keep ErrorHandler and Logger from main
- Keep retryCount and RequestOptions from feature branch
- Merge constructor to support all features
- request() gets both logging and options

### Resolved File

```typescript
// src/api/client.ts
import { ApiConfig, ApiResponse, ErrorHandler, RequestOptions } from './types';
import { Logger } from '../utils/logger';

export class ApiClient {
  private config: ApiConfig;
  private errorHandler: ErrorHandler;
  private logger: Logger;
  private retryCount: number;

  constructor(config: ApiConfig, retryCount = 3) {
    this.config = config;
    this.errorHandler = new ErrorHandler();
    this.logger = new Logger('ApiClient');
    this.retryCount = retryCount;
  }

  async request<T>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    this.logger.info(`Request: ${endpoint}`);
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`);
      // ... rest of implementation
```

## Step 5: Resolve Second File (types.ts)

### Read the Conflicted File

```typescript
// src/api/types.ts
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
<<<<<<< HEAD
  headers: Record<string, string>;
}

export interface ErrorHandler {
  handle(error: Error): void;
  log(message: string): void;
=======
  retryPolicy?: RetryPolicy;
}

export interface RetryPolicy {
  maxRetries: number;
  backoffMs: number;
}

export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
>>>>>>> abc1234 (Refactor API client)
}

export interface ApiResponse<T> {
  data: T;
  status: number;
}
```

### Resolution

Combine all type definitions:

```typescript
// src/api/types.ts
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  headers: Record<string, string>;
  retryPolicy?: RetryPolicy;
}

export interface ErrorHandler {
  handle(error: Error): void;
  log(message: string): void;
}

export interface RetryPolicy {
  maxRetries: number;
  backoffMs: number;
}

export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
}
```

## Step 6: Stage and Continue Rebase

```bash
# Stage resolved files
git add src/api/client.ts src/api/types.ts

# Continue rebase
git rebase --continue
```

If more commits have conflicts, repeat the process.

## Step 7: Handle Subsequent Commits

```bash
# Another conflict might appear:
# CONFLICT (content): Merge conflict in src/api/client.ts
# error: could not apply def5678... Add retry logic

# Repeat the resolution process for each commit
git diff --name-only --diff-filter=U
# Resolve...
git add <files>
git rebase --continue
```

## Step 8: Verify Completion

```bash
git rebase --show-current-patch
# fatal: No rebase in progress?
# This means rebase is complete!

git log --oneline -5
# Verify commit history looks correct
```

## Result

The rebase successfully combined:
- ErrorHandler and Logger infrastructure from main
- RetryPolicy and RequestOptions from feature branch
- All type definitions merged
- Commit history is clean and linear

## Abort Option

If things go wrong, you can always abort:

```bash
git rebase --abort
# Returns to state before rebase started
```

This is why the backup branch is important - even if you complete a bad rebase, you can recover:

```bash
git checkout feature/api-refactor
git reset --hard lz-git/conflict/feature/api-refactor/backup-20240115-160045Z
```
