# Disjoint Additions Example

This example demonstrates resolving conflicts where both branches add to the same structure without modifying the same code.

## Scenario

Two feature branches independently add exports to a module's index file.

**Branch A (feature/auth)** adds authentication utilities:
```typescript
export { validateToken } from './auth/validate-token';
export { refreshToken } from './auth/refresh-token';
```

**Branch B (feature/i18n)** adds internationalization utilities:
```typescript
export { formatMessage } from './i18n/format-message';
export { loadLocale } from './i18n/load-locale';
```

## The Conflict

When merging, Git produces:

```typescript
// src/utils/index.ts
export { sanitizeInput } from './sanitize-input';
export { formatDate } from './format-date';
<<<<<<< HEAD
export { validateToken } from './auth/validate-token';
export { refreshToken } from './auth/refresh-token';
=======
export { formatMessage } from './i18n/format-message';
export { loadLocale } from './i18n/load-locale';
>>>>>>> feature/i18n
```

## Analysis

**Conflict Type**: Disjoint (Textual Conflict Subtype 2)

**Characteristics**:
- Both branches add to the same location
- Additions are independent - no overlap in functionality
- No naming collisions

**Resolution Strategy**: Union of both additions

## Resolution

Include both sets of exports. Consider alphabetical ordering for maintainability:

```typescript
// src/utils/index.ts
export { sanitizeInput } from './sanitize-input';
export { formatDate } from './format-date';
export { formatMessage } from './i18n/format-message';
export { loadLocale } from './i18n/load-locale';
export { refreshToken } from './auth/refresh-token';
export { validateToken } from './auth/validate-token';
```

## Verification Checklist

1. **No naming collisions**: Verify no duplicate export names
2. **All imports valid**: Check that all source files exist
3. **No circular dependencies**: Ensure new exports don't create cycles
4. **Type checking**: Run `tsc --noEmit` to verify types

## Common Variations

### Array Additions

```typescript
<<<<<<< HEAD
const plugins = ['auth', 'logging'];
=======
const plugins = ['auth', 'i18n'];
>>>>>>> feature/i18n
```

Resolution:
```typescript
const plugins = ['auth', 'i18n', 'logging'];
```

### Object Property Additions

```typescript
<<<<<<< HEAD
const config = {
  api: { timeout: 5000 },
  cache: { ttl: 3600 },
};
=======
const config = {
  api: { timeout: 5000 },
  logging: { level: 'info' },
};
>>>>>>> feature/logging
```

Resolution:
```typescript
const config = {
  api: { timeout: 5000 },
  cache: { ttl: 3600 },
  logging: { level: 'info' },
};
```

## When to Flag for Review

Even disjoint additions may need review when:

- **Order matters**: Some arrays are order-sensitive (middleware, plugins)
- **Limits exist**: Adding may exceed array bounds or config limits
- **Performance implications**: Adding exports affects bundle size
- **Feature interactions**: Added features might conflict at runtime

In these cases, present the proposed resolution but ask for confirmation.
