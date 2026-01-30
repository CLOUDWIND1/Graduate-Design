# Admin Module Refactor Plan

## Goal
Standardize `admin.py` responses using Pydantic schemas, replacing manual dictionary construction and standardizing on camelCase for frontend compatibility where consistent.

## Proposed Changes

### 1. [NEW] `app/schemas/admin.py`
Create schemas for:
- `DashboardResponse`:
    - `userCount`: int
    - `activeActivityCount`: int
    - `totalRecommendations`: int
    - `avgClickRate`: float
    - `clusterDistribution`: List[ClusterItem]
    - `recommendationTrend`: List[TrendItem]
    - `featureImportance`: List[FeatureItem]
    - (Legacy fields included for backward compatibility: `total_users`, `total_activities`, `active_activities`, `total_rewards`, `click_rate`, `accept_rate`)
- `AdminUserListResponse`: 
    - `items`: List[AdminUserItem]
    - `total`: int
    - `page`: int
    - `page_size`: int
- `PotentialAnalysisResponse`: 
    - `highPotentialCount`: int
    - `mediumPotentialCount`: int
    - `lowPotentialCount`: int
    - `topUsers`: List[PotentialUserItem]
- `DimensionStrategyResponse`: List[StrategyItem]
- `SystemLogResponse`:
    - `items`: List[LogItem]
    - `total`: int
    - `page`: int
    - `page_size`: int

### 2. [MODIFY] `app/api/admin.py`
- Import new schemas.
- Refactor `get_dashboard` to return Pydantic model (preserving dual keys where necessary for backward struct compatibility if needed, but preferably cleaning up).
- Refactor `get_users` to use `AdminUserListResponse`.
- Refactor stats endpoints.

## Verification
- Verify Dashboard loads correctly in frontend (critical).
- Verify User list loads in Admin panel.
