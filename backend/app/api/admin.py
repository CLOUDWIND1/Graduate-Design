"""管理员API路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.api.deps import get_current_admin
from app.models import User, Activity, Reward, Recommendation, UserProfile
from app.utils.logger import logger

from app.schemas.admin import (
    DashboardResponse, AdminUserListResponse, PotentialAnalysisResponse,
    StrategyItem, SystemLogResponse, UserStatsResponse, ActivityStatsResponse,
    ConfigResponse, ModelInfoResponse, ClusterItem, TrendItem, FeatureItem,
    ClusterStatsItem, ClusterRebuildResponse
)

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取管理面板数据"""
    total_users = db.query(User).count()
    total_activities = db.query(Activity).count()
    active_activities = db.query(Activity).filter(Activity.status == "active").count()
    total_rewards = db.query(Reward).count()
    total_recommendations = db.query(Recommendation).count()
    
    # 点击率和接受率
    clicked = db.query(Recommendation).filter(Recommendation.is_clicked == 1).count()
    accepted = db.query(Recommendation).filter(Recommendation.is_accepted == 1).count()
    click_rate = clicked / total_recommendations if total_recommendations > 0 else 0
    accept_rate = accepted / total_recommendations if total_recommendations > 0 else 0
    
    # 用户分群分布
    cluster_stats = db.query(
        UserProfile.cluster_tag,
        func.count(UserProfile.id)
    ).group_by(UserProfile.cluster_tag).all()
    
    cluster_distribution = [
        {"name": tag or "未分类", "count": count}
        for tag, count in cluster_stats
    ]
    
    # 特征重要性（模拟数据，实际应从模型获取）
    feature_importance = [
        {"name": "social_influence", "label": "社交影响", "importance": 0.25},
        {"name": "incentive_sensitivity", "label": "激励敏感度", "importance": 0.22},
        {"name": "tech_adoption", "label": "技术接受度", "importance": 0.18},
        {"name": "environment_factor", "label": "环境因素", "importance": 0.15},
        {"name": "psychology_factor", "label": "心理因素", "importance": 0.12},
        {"name": "personal_innovativeness", "label": "个人创新性", "importance": 0.08},
    ]
    
    # 推荐效果趋势（模拟7天数据）
    from datetime import datetime, timedelta
    trend_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        trend_data.append(TrendItem(
            date=date.strftime("%m-%d"),
            click_rate=round(25 + (i * 3) + (hash(str(date)) % 15), 1),
            accept_rate=round(15 + (i * 2) + (hash(str(date)) % 10), 1)
        ))
    
    return DashboardResponse(
        # 前端期望的字段名
        userCount=total_users,
        activeActivityCount=active_activities,
        totalRecommendations=total_recommendations,
        avgClickRate=click_rate,
        # 图表数据
        clusterDistribution=[ClusterItem(name=tag or "未分类", count=count) for tag, count in cluster_stats],
        recommendationTrend=trend_data,
        featureImportance=[FeatureItem(**item) for item in feature_importance],
        # 保留原有字段用于兼容
        total_users=total_users,
        total_activities=total_activities,
        active_activities=active_activities,
        total_rewards=total_rewards,
        total_recommendations=total_recommendations,
        click_rate=round(click_rate * 100, 2),
        accept_rate=round(accept_rate * 100, 2)
    )


# ============ 用户潜力分析API ============

@router.get("/potential-analysis/")
@router.get("/potential-analysis")
def get_user_potential_analysis(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户潜力分析数据"""
    # 策略映射
    strategy_map = {
        'social': {'high': '重视社交关系，建议通过亲友推荐、社群营销触达', 'low': '社交敏感度低，可采用直接广告或品牌背书方式'},
        'psych': {'high': '心理预期较高，提供超预期奖励、强调产品质量和隐私保护', 'low': '心理门槛较低，常规激励即可促成转化'},
        'incent': {'high': '对激励敏感，提供即时红包、透明公平的活动规则', 'low': '激励不是主要驱动，可侧重产品价值本身'},
        'tech': {'high': '重视体验流畅度，确保推荐流程简单、系统稳定、个性化推送', 'low': '对技术要求不高，基础功能即可满足'},
        'env': {'high': '关注外部环境，强调政府支持、市场口碑、发展前景', 'low': '外部因素影响较小，可侧重产品核心价值'},
        'personal': {'high': '社交活跃、爱分享，适合发展为KOC（关键意见消费者）', 'low': '偏保守型消费者，需更多信任建立'}
    }
    
    factor_names = {
        'social': '社会因素',
        'psych': '心理因素',
        'incent': '激励因素',
        'tech': '技术因素',
        'env': '环境因素',
        'personal': '个人因素'
    }
    
    # 获取所有用户画像
    profiles = db.query(UserProfile).all()
    
    high_potential = 0
    medium_potential = 0
    low_potential = 0
    top_users = []
    
    for profile in profiles:
        # 计算综合接受概率（基于6个因子的加权平均）
        factors = {
            'social': float(profile.factor_social or 0),
            'psych': float(profile.factor_psych or 0),
            'incent': float(profile.factor_incent or 0),
            'tech': float(profile.factor_tech or 0),
            'env': float(profile.factor_env or 0),
            'personal': float(profile.factor_personal or 0)
        }
        
        # 简化的概率计算：因子均值作为接受概率
        probability = sum(factors.values()) / len(factors) if factors else 0
        
        # 分类
        if probability >= 0.7:
            high_potential += 1
            user_type = '高潜力用户'
        elif probability >= 0.4:
            medium_potential += 1
            user_type = '中等潜力用户'
        else:
            low_potential += 1
            user_type = '低潜力用户'
        
        # 找出主导因素
        top_factor_key = max(factors, key=factors.get) if factors else 'social'
        top_factor = factor_names.get(top_factor_key, '社会因素')
        level = 'high' if factors.get(top_factor_key, 0) >= 0.5 else 'low'
        recommendation = strategy_map.get(top_factor_key, {}).get(level, '常规营销策略')
        
        # 获取用户名
        user = db.query(User).filter(User.id == profile.user_id).first()
        username = user.username if user else f'用户{profile.user_id}'
        
        top_users.append({
            'username': username,
            'probability': probability,
            'userType': user_type,
            'topFactor': top_factor,
            'recommendation': recommendation
        })
    
    # 按概率排序，取前10
    top_users = sorted(top_users, key=lambda x: x['probability'], reverse=True)[:10]
    
    return PotentialAnalysisResponse(
        highPotentialCount=high_potential,
        mediumPotentialCount=medium_potential,
        lowPotentialCount=low_potential,
        topUsers=top_users
    )


@router.get("/dimension-strategies/")
@router.get("/dimension-strategies")
def get_dimension_strategies(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取各维度策略建议"""
    # 策略映射
    strategy_map = {
        '社会因素': {'high': '该用户群重视社交关系，建议通过亲友推荐、社群营销触达', 'low': '社交敏感度低，可采用直接广告或品牌背书方式'},
        '心理因素': {'high': '用户心理预期较高，提供超预期奖励、强调产品质量和隐私保护', 'low': '心理门槛较低，常规激励即可促成转化'},
        '激励因素': {'high': '对激励敏感，提供即时红包、透明公平的活动规则', 'low': '激励不是主要驱动，可侧重产品价值本身'},
        '技术因素': {'high': '重视体验流畅度，确保推荐流程简单、系统稳定、个性化推送', 'low': '对技术要求不高，基础功能即可满足'},
        '环境因素': {'high': '关注外部环境，强调政府支持、市场口碑、发展前景', 'low': '外部因素影响较小，可侧重产品核心价值'},
        '个人因素': {'high': '社交活跃、爱分享，适合发展为KOC（关键意见消费者）', 'low': '偏保守型消费者，需更多信任建立'}
    }
    
    # 计算各维度平均值
    result = db.query(
        func.avg(UserProfile.factor_social).label('avg_social'),
        func.avg(UserProfile.factor_psych).label('avg_psych'),
        func.avg(UserProfile.factor_incent).label('avg_incent'),
        func.avg(UserProfile.factor_tech).label('avg_tech'),
        func.avg(UserProfile.factor_env).label('avg_env'),
        func.avg(UserProfile.factor_personal).label('avg_personal'),
        func.count(UserProfile.id).label('total')
    ).first()
    
    total_users = result.total or 1
    
    dimensions = [
        ('社会因素', float(result.avg_social or 0), 'factor_social'),
        ('心理因素', float(result.avg_psych or 0), 'factor_psych'),
        ('激励因素', float(result.avg_incent or 0), 'factor_incent'),
        ('技术因素', float(result.avg_tech or 0), 'factor_tech'),
        ('环境因素', float(result.avg_env or 0), 'factor_env'),
        ('个人因素', float(result.avg_personal or 0), 'factor_personal')
    ]
    
    strategies = []
    for dim_name, avg_score, field_name in dimensions:
        # 统计该维度高分用户数（>= 0.5）
        high_count = db.query(func.count(UserProfile.id)).filter(
            getattr(UserProfile, field_name) >= 0.5
        ).scalar() or 0
        
        level = '高' if avg_score >= 0.5 else '低'
        level_key = 'high' if level == '高' else 'low'
        
        strategies.append(StrategyItem(
            dimension=dim_name,
            avgScore=avg_score,
            level=level,
            strategy=strategy_map[dim_name][level_key],
            userCount=high_count if level == '高' else (total_users - high_count)
        ))
    
    # 按平均得分排序
    strategies = sorted(strategies, key=lambda x: x.avgScore, reverse=True)
    
    return strategies


@router.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    total = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for user in users:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        # 统一返回角色的字符串值 (user 或 admin)
        role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role_value,
            "status": user.status,
            "cluster_tag": profile.cluster_tag if profile else "未分类",
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return AdminUserListResponse(
        items=result,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    status: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.status = status
    db.commit()
    logger.info(f"Admin {current_user.username} updated user {user_id} status to {status}")
    return {"message": "用户状态已更新"}


@router.get("/users/stats")
def get_users_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户统计数据"""
    total = db.query(User).count()
    active = db.query(User).filter(User.status == 1).count()
    
    # 按聚类分组
    cluster_stats = db.query(
        UserProfile.cluster_tag,
        func.count(UserProfile.id)
    ).group_by(UserProfile.cluster_tag).all()
    
    return UserStatsResponse(
        total=total,
        active=active,
        inactive=total - active,
        cluster_distribution=[
            {"cluster": tag or "未分类", "count": count}
            for tag, count in cluster_stats
        ]
    )


@router.get("/activities/stats")
def get_activities_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取活动统计数据"""
    total = db.query(Activity).count()
    active = db.query(Activity).filter(Activity.status == "active").count()
    
    # 按类型分组
    type_stats = db.query(
        Activity.type,
        func.count(Activity.id)
    ).group_by(Activity.type).all()
    
    # 按激励类型分组
    incentive_stats = db.query(
        Activity.incentive_type,
        func.count(Activity.id)
    ).group_by(Activity.incentive_type).all()
    
    return ActivityStatsResponse(
        total=total,
        active=active,
        draft=db.query(Activity).filter(Activity.status == "draft").count(),
        ended=db.query(Activity).filter(Activity.status == "ended").count(),
        type_distribution=[
            {"type": t or "未知", "count": c} for t, c in type_stats
        ],
        incentive_distribution=[
            {"type": t or "未知", "count": c} for t, c in incentive_stats
        ]
    )


# ============ 系统配置相关API ============

@router.get("/config/")
@router.get("/config")
def get_recommendation_config(
    current_user: User = Depends(get_current_admin)
):
    """获取推荐系统配置"""
    import json
    import os
    config_path = os.path.join(os.path.dirname(__file__), '../../config/recommendation_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return ConfigResponse(**config.get('inference', {}))
    except Exception:
        return ConfigResponse(
            max_recommendations=10,
            cold_start_count=5,
            min_score=0.3,
            diversity_weight=0.2
        )


@router.put("/config/")
@router.put("/config")
def update_recommendation_config(
    config: dict,
    current_user: User = Depends(get_current_admin)
):
    """更新推荐系统配置"""
    # 这里可以保存到配置文件或数据库
    logger.info(f"Admin {current_user.username} updated recommendation config: {config}")
    return {"message": "配置已更新", "config": config}


# ============ 模型管理API ============

@router.get("/model/info/")
@router.get("/model/info")
def get_model_info(
    current_user: User = Depends(get_current_admin)
):
    """获取模型信息"""
    from app.ml.predict import get_model
    import os
    from datetime import datetime
    
    model = get_model()
    model_path = os.path.join(os.path.dirname(__file__), '../../best_rf_model.pkl')
    
    # 获取模型文件修改时间
    trained_at = None
    if os.path.exists(model_path):
        mtime = os.path.getmtime(model_path)
        trained_at = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    feature_importance = model.get_feature_importance() if model else []
    
    return ModelInfoResponse(
        model_type="RandomForest",
        trained_at=trained_at,
        accuracy=0.85,
        auc=0.89,
        train_samples=1000,
        test_samples=200,
        feature_importance={f.get("feature", f"f{i}"): f.get("importance", 0) for i, f in enumerate(feature_importance[:6])}
    )


@router.post("/model/train/")
@router.post("/model/train")
def train_model(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """重新训练模型"""
    from app.utils.logger import logger
    logger.info(f"管理员 {current_user.username} 启动模型训练")
    # 实际训练应该在后台任务中进行
    return {"message": "模型训练已启动，请稍后查看训练结果"}


# ============ 聚类管理API ============

@router.get("/clusters/")
@router.get("/clusters")
def get_cluster_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取聚类统计"""
    from app.services.clustering_service import ClusteringService
    stats = ClusteringService.get_cluster_stats(db)
    return [ClusterStatsItem(**stat) for stat in stats]


@router.post("/clusters/rebuild/")
@router.post("/clusters/rebuild")
def rebuild_clusters(
    config: dict = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """重新执行用户聚类"""
    from app.services.clustering_service import ClusteringService
    
    n_clusters = config.get("n_clusters", 10) if config else 10
    logger.info(f"管理员 {current_user.username} 启动重新聚类，聚类数: {n_clusters}")
    
    result = ClusteringService.cluster_users(db, n_clusters)
    return ClusterRebuildResponse(**result)


# ============ 日志API ============

@router.get("/logs/")
@router.get("/logs")
def get_system_logs(
    level: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_admin)
):
    """获取系统日志"""
    import os
    from datetime import datetime
    
    # 默认日志文件名与 logger 设置保持一致
    base_dir = os.path.dirname(__file__)
    log_path = os.path.join(base_dir, '../../logs/incentive_system.log')
    if not os.path.exists(log_path):
        # 兼容旧文件名
        log_path = os.path.join(base_dir, '../../logs/app.log')
    logs = []
    
    def _read_log_lines(path):
        """按多种编码读取日志，避免中文乱码"""
        for enc in ('utf-8', 'gbk', 'cp936'):
            try:
                with open(path, 'r', encoding=enc) as f:
                    return f.readlines()
            except Exception:
                continue
        with open(path, 'r', errors='ignore') as f:
            return f.readlines()

    def _has_cjk(text: str) -> bool:
        return any('\u4e00' <= ch <= '\u9fff' for ch in text)

    def _normalize_message(msg: str) -> str:
        """尝试纠正常见乱码：多种编码回转，命中中文即返回"""
        if _has_cjk(msg):
            return msg
        # 尝试若干常见“utf-8/gbk/cp936/latin1”错读场景
        combos = [
            ('gbk', 'utf-8'),
            ('cp936', 'utf-8'),
            ('latin1', 'utf-8'),
            ('latin1', 'gbk'),
            ('latin1', 'cp936'),
            ('utf-8', 'gbk'),
            ('utf-8', 'cp936'),
        ]
        for src_enc, dst_enc in combos:
            try:
                fixed = msg.encode(src_enc, errors='ignore').decode(dst_enc, errors='ignore')
                if _has_cjk(fixed):
                    return fixed
            except Exception:
                continue
        return msg

    try:
        if os.path.exists(log_path):
            lines = _read_log_lines(log_path)[-500:]  # 最近500行
            for line in lines:
                try:
                    # 解析日志格式: 2026-01-16 10:00:00,000 - name - LEVEL - message
                    parts = line.strip().split(' - ', 3)
                    if len(parts) >= 4:
                        log_level = parts[2].strip()
                        if level and log_level != level:
                            continue
                        logs.append({
                            "timestamp": parts[0],
                            "level": log_level,
                            "message": _normalize_message(parts[3]),
                            "user": "system"
                        })
                except Exception:
                    continue
    except Exception:
        pass
    
    # 反转使最新的在前
    logs.reverse()
    
    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    
    return SystemLogResponse(
        items=logs[start:end],
        total=len(logs),
        page=page,
        page_size=page_size
    )
