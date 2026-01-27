# File Type Resolution Strategies

Detailed resolution strategies organized by file type.

## JavaScript/TypeScript

### General Approach

1. Parse the file to understand structure
2. Identify conflict within AST context (function, class, module)
3. Merge at the semantic level, not line level

### Import Statements

**Strategy**: Union with deduplication and sorting

```typescript
// Resolution rules:
// 1. Combine all unique imports
// 2. Sort alphabetically by module path
// 3. Group: external packages, then relative imports
// 4. Prefer named imports over default when both exist
```

### Function Changes

**Strategy**: Analyze function purpose and combine changes

- Parameter additions: combine parameters, update call sites
- Return type changes: use more specific type
- Body changes: merge non-conflicting changes, flag logic conflicts

### Class Modifications

**Strategy**: Merge members, check for conflicts

- New properties: include all
- New methods: include all
- Modified methods: apply smart merge or flag

### Type Definitions

**Strategy**: Union types and interfaces

```typescript
// If both branches extended an interface:
<<<<<<< HEAD
interface User {
  id: string;
  name: string;
  email: string;
}
=======
interface User {
  id: string;
  name: string;
  phone?: string;
}
>>>>>>> feature/contact

// Resolution: combine properties
interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
}
```

## Python

### Import Statements

**Strategy**: Combine and organize

```python
# Resolution rules:
# 1. Standard library imports first
# 2. Third-party imports second
# 3. Local imports third
# 4. Alphabetical within each group
# 5. Combine from X import a, b, c
```

### Function/Method Changes

**Strategy**: Similar to JavaScript

- Combine parameter additions
- Merge docstring updates
- Flag logic conflicts in body

### Class Changes

**Strategy**: Merge class body elements

- `__init__` parameters: combine
- New methods: include all
- Decorator changes: combine unique decorators

## JSON Files

### General Approach

1. Parse both versions as JSON
2. Deep merge objects
3. Handle array conflicts based on context

### package.json

**Dependencies**:
```json
// Rules:
// 1. Union of all dependencies
// 2. Higher version wins for same package
// 3. Sort alphabetically
// 4. Preserve section order (dependencies, devDependencies, etc.)
```

**Scripts**:
```json
// Rules:
// 1. Include all unique scripts
// 2. Same script name: flag for review
// 3. Sort alphabetically
```

**Other fields**:
```json
// Rules:
// 1. version: prefer incoming
// 2. name, description: prefer incoming
// 3. Arrays: union
// 4. Objects: deep merge
```

### tsconfig.json / jsconfig.json

**Strategy**: Merge compiler options

```json
// Rules:
// 1. Union all options
// 2. Conflicting values: prefer stricter
// 3. paths: merge path mappings
// 4. include/exclude: union arrays
```

### .eslintrc.json

**Strategy**: Merge configuration

```json
// Rules:
// 1. rules: merge, prefer stricter rule
// 2. extends: union arrays
// 3. plugins: union arrays
// 4. env: merge objects
```

## YAML Files

### General Approach

1. Parse as YAML
2. Deep merge structures
3. Preserve comments where possible (difficult)

### docker-compose.yml

**Strategy**: Merge services

```yaml
# Rules:
# 1. Union of services
# 2. Same service: deep merge configuration
# 3. volumes: union arrays
# 4. networks: union arrays
# 5. environment: merge variables
```

### GitHub Actions Workflows

**Strategy**: Merge jobs and steps

```yaml
# Rules:
# 1. Union of jobs
# 2. Same job: merge steps arrays
# 3. env: merge environment variables
# 4. on: merge trigger events
```

## Markdown Files

### General Approach

1. Identify document structure (headings, sections)
2. Merge section by section
3. Preserve formatting

### README.md

**Strategy**: Section-aware merge

```markdown
# Rules:
# 1. Same heading: merge content under heading
# 2. New sections: include in appropriate location
# 3. Lists: union of items
# 4. Code blocks: flag for review
# 5. Badges: union
```

### Documentation Files

**Strategy**: Careful content merge

- Preserve accuracy
- Combine complementary information
- Flag contradictory statements

## Lock Files

### package-lock.json / yarn.lock / pnpm-lock.yaml

**Strategy**: NEVER manually merge

```bash
# Resolution steps:
# 1. Accept either version (prefer incoming)
# 2. Delete the lock file
# 3. Run package manager install:
#    - npm: npm install
#    - yarn: yarn install
#    - pnpm: pnpm install
# 4. Commit regenerated lock file
```

### Cargo.lock (Rust)

**Strategy**: Regenerate

```bash
# Resolution:
# 1. Accept either version
# 2. cargo update
# 3. Commit regenerated lock
```

### go.sum (Go)

**Strategy**: Regenerate

```bash
# Resolution:
# 1. Accept either version
# 2. go mod tidy
# 3. Commit regenerated sum
```

## Configuration Files

### .env / .env.example

**Strategy**: Union of variables

```bash
# Rules:
# 1. Include all unique variables
# 2. Same variable: flag for review
# 3. Maintain grouping/comments
# 4. .env.example: include all, use placeholder values
```

### .gitignore

**Strategy**: Union of patterns

```bash
# Rules:
# 1. Include all unique patterns
# 2. Remove duplicates
# 3. Maintain organization (group by purpose)
# 4. Sort within groups
```

### Editor Configs (.vscode/settings.json, .editorconfig)

**Strategy**: Merge settings

```json
// Rules:
// 1. Union of settings
// 2. Conflicting values: prefer incoming
// 3. Maintain formatting
```

## Test Files

### Test Suites

**Strategy**: Include all tests

```javascript
// Rules:
// 1. Union of describe blocks
// 2. Union of test cases
// 3. Same test modified: smart merge or flag
// 4. Setup/teardown: merge carefully
```

### Test Fixtures

**Strategy**: Union of fixture data

- Include all test data
- Same fixture name: flag for review

## Database Migrations

### SQL Migrations

**Strategy**: NEVER merge migration content

```sql
-- Rules:
-- 1. Keep migrations separate
-- 2. Rename conflicting migration numbers
-- 3. Ensure migration order is valid
-- 4. Test migration sequence
```

### ORM Migrations (Prisma, TypeORM, etc.)

**Strategy**: Regenerate if needed

1. Keep separate migration files
2. Resolve migration numbering conflicts
3. Regenerate types/client after resolution
