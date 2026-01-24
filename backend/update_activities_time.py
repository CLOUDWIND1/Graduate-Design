"""
更新活动时间
运行: E:\BaiduSyncdisk\python.exe update_activities_time.py
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Activity

db = SessionLocal()

try:
    activities = db.query(Activity).all()
    now = datetime.now()
    
    updated = 0
    for i, activity in enumerate(activities):
        if activity.start_time is None or activity.end_time is None:
            # 设置开始时间为今天，结束时间为30-90天后（随机分布）
            days_offset = (i % 3) * 30  # 0, 30, 60天
            activity.start_time = now - timedelta(days=days_offset)
            activity.end_time = now + timedelta(days=30 + (i % 60))
            updated += 1
    
    db.commit()
    print(f"已更新 {updated} 个活动的时间")
    
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
