from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ============ Shared Items ============

class ClusterItem(BaseModel):
    name: str  # e.g. "技术驱动型" or "未分类"
    count: int

class TrendItem(BaseModel):
    date: str
    click_rate: float
    accept_rate: float

class FeatureItem(BaseModel):
    name: str # internal name, e.g. "social_influence"
    label: str # display name, e.g. "社交影响"
    importance: float

# ============ Response Models ============

class DashboardResponse(BaseModel):
    # Frontend expected fields (camelCase)
    userCount: int
    activeActivityCount: int
    totalRecommendations: int
    avgClickRate: float
    clusterDistribution: List[ClusterItem]
    recommendationTrend: List[TrendItem]
    featureImportance: List[FeatureItem]
    
    # Legacy fields for backward compatibility
    total_users: int
    total_activities: int
    active_activities: int
    total_rewards: int
    total_recommendations: int
    click_rate: float
    accept_rate: float

class AdminUserItem(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    status: int
    cluster_tag: str
    created_at: Optional[str] = None

class AdminUserListResponse(BaseModel):
    items: List[AdminUserItem]
    total: int
    page: int
    page_size: int

class PotentialUserItem(BaseModel):
    username: str
    probability: float
    userType: str
    topFactor: str
    recommendation: str

class PotentialAnalysisResponse(BaseModel):
    highPotentialCount: int
    mediumPotentialCount: int
    lowPotentialCount: int
    topUsers: List[PotentialUserItem]

class StrategyItem(BaseModel):
    dimension: str
    avgScore: float
    level: str
    strategy: str
    userCount: int

class LogItem(BaseModel):
    timestamp: str
    level: str
    message: str
    user: str

class SystemLogResponse(BaseModel):
    items: List[LogItem]
    total: int
    page: int
    page_size: int

class ConfigResponse(BaseModel):
    max_recommendations: int
    cold_start_count: int
    min_score: float
    diversity_weight: float

class ModelInfoResponse(BaseModel):
    model_type: str
    trained_at: Optional[str]
    accuracy: float
    auc: float
    train_samples: int
    test_samples: int
    feature_importance: Dict[str, float]

class UserStatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
    cluster_distribution: List[Dict[str, Any]] # {"cluster": str, "count": int}

class ActivityStatsResponse(BaseModel):
    total: int
    active: int
    draft: int
    ended: int
    type_distribution: List[Dict[str, Any]] # {"type": str, "count": int}
    incentive_distribution: List[Dict[str, Any]] # {"type": str, "count": int}

class ClusterStatsItem(BaseModel):
    cluster_tag: str
    count: int
    avg_factors: Dict[str, float]

class ClusterRebuildItem(BaseModel):
    cluster_id: int
    label: str
    count: int

class ClusterRebuildResponse(BaseModel):
    message: Optional[str] = None
    error: Optional[str] = None
    total_users: Optional[int] = None
    n_clusters: Optional[int] = None
    clusters: List[ClusterRebuildItem]
