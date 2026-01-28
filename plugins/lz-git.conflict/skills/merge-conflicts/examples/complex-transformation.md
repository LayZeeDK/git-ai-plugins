# Complex Transformation Conflict Example

This example demonstrates resolving conflicts involving multiple simultaneous naming/type changes.

## Scenario

Based on patterns from Microsoft Edge (ISSTA 2022 research).

**Upstream (main branch)** performed a comprehensive refactor:
- Renamed type `PermissionRequestType` -> `RequestType`
- Changed constant naming convention from `PERMISSION_*` -> `k*`

```cpp
// Before
enum class PermissionRequestType {
  PERMISSION_NOTIFICATIONS,
  PERMISSION_GEOLOCATION,
  PERMISSION_CAMERA,
  PERMISSION_CAMERA_PAN_TILT_ZOOM
};

// After
enum class RequestType {
  kNotifications,
  kGeolocation,
  kCamera,
  kCameraPanTiltZoom
};
```

**Downstream (feature branch)** added new code using old conventions:
```cpp
void RequestCameraAccess(PermissionManager* manager) {
  manager->Request(PermissionRequestType::PERMISSION_CAMERA_PAN_TILT_ZOOM);
}
```

## The Problem

Git merge succeeds textually, but compilation fails:

```
error: use of undeclared identifier 'PermissionRequestType'
error: no member named 'PERMISSION_CAMERA_PAN_TILT_ZOOM' in 'RequestType'
```

## Analysis

**Conflict Type**: Complex Transformation (Semantic Conflict Subtype 5)

**Complexity**: High - requires understanding multiple transformation rules

**Transformations to apply**:
1. Type rename: `PermissionRequestType` -> `RequestType`
2. Constant rename pattern: `PERMISSION_X_Y_Z` -> `kXYZ` (camelCase after `k`)

## Resolution

### Step 1: Identify All Transformation Rules

From the upstream commit, extract the patterns:

| Before | After | Rule |
|--------|-------|------|
| `PermissionRequestType` | `RequestType` | Drop `Permission` prefix |
| `PERMISSION_NOTIFICATIONS` | `kNotifications` | `PERMISSION_X` -> `kX` (capitalize first letter) |
| `PERMISSION_CAMERA_PAN_TILT_ZOOM` | `kCameraPanTiltZoom` | Convert SCREAMING_SNAKE to kPascalCase |

### Step 2: Find All Downstream Usages

```bash
grep -r "PermissionRequestType\|PERMISSION_" --include="*.cpp" --include="*.h"
```

### Step 3: Apply Transformations

**Original downstream code**:
```cpp
void RequestCameraAccess(PermissionManager* manager) {
  manager->Request(PermissionRequestType::PERMISSION_CAMERA_PAN_TILT_ZOOM);
}
```

**After applying transformations**:
```cpp
void RequestCameraAccess(PermissionManager* manager) {
  manager->Request(RequestType::kCameraPanTiltZoom);
}
```

### Step 4: Verify

```bash
# Compile
make clean && make

# Run tests to verify behavior
make test
```

## TypeScript/JavaScript Example

**Upstream refactor** - modernizing API conventions:

```typescript
// Before
export enum HttpStatusCode {
  HTTP_OK = 200,
  HTTP_NOT_FOUND = 404,
  HTTP_INTERNAL_ERROR = 500,
}

// After
export enum StatusCode {
  Ok = 200,
  NotFound = 404,
  InternalError = 500,
}
```

**Downstream usage** with old conventions:
```typescript
if (response.status === HttpStatusCode.HTTP_NOT_FOUND) {
  showNotFoundPage();
}
```

**Transformation rules**:
1. `HttpStatusCode` -> `StatusCode`
2. `HTTP_X_Y` -> `XY` (remove prefix, PascalCase)

**Resolved**:
```typescript
if (response.status === StatusCode.NotFound) {
  showNotFoundPage();
}
```

## Handling Partial Matches

Sometimes downstream code uses patterns that don't have exact upstream equivalents:

**Upstream** defines:
```typescript
enum RequestType {
  kNotifications,
  kGeolocation,
  kCamera,
}
```

**Downstream** added a new permission:
```typescript
manager->Request(PermissionRequestType::PERMISSION_MICROPHONE);
```

**Problem**: `kMicrophone` doesn't exist in the enum yet.

**Resolution**:
1. Apply the transformation: `PermissionRequestType::PERMISSION_MICROPHONE` -> `RequestType::kMicrophone`
2. Add the missing enum value to the upstream definition
3. Verify with the team that the new permission should be added

## When Automated Resolution Is Unreliable

Flag for human review when:

1. **Ambiguous transformations**: Multiple possible interpretations
2. **Inconsistent upstream patterns**: Some constants follow different rules
3. **Semantic changes**: The rename also changed behavior, not just names
4. **Missing mappings**: No clear upstream equivalent exists

Example of inconsistency to flag:
```cpp
// Upstream changes are inconsistent:
PERMISSION_NOTIFICATIONS -> kNotifications  // Standard transform
PERMISSION_CAMERA -> kCameraAccess          // Added "Access" suffix - why?
```

In such cases, present the analysis but ask for confirmation:

> Detected complex transformation with potential inconsistency:
> - Most constants follow `PERMISSION_X` -> `kX` pattern
> - But `PERMISSION_CAMERA` became `kCameraAccess` (added suffix)
>
> For `PERMISSION_MICROPHONE`, should the resolution be:
> 1. `kMicrophone` (following the standard pattern)
> 2. `kMicrophoneAccess` (following the camera exception)
>
> Please clarify the intended convention.

## Prevention

- **Document transformation rules** in commit messages
- **Provide migration scripts** for large-scale renames
- **Use codemods** (jscodeshift, ts-morph) for automated transformations
- **Maintain deprecation aliases** during transition periods
