"""
初始化测试数据
运行: E:\BaiduSyncdisk\python.exe init_test_data.py
"""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models import User, Activity, UserProfile, Reward
from app.utils.auth import get_password_hash

# 创建表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 1. 创建测试活动
    activities_data = [
        # 邀请类活动
        {
            "title": "邀请好友得红包",
            "description": "邀请1位好友注册，双方各得5元红包奖励",
            "type": "invite",
            "incentive_type": "red_packet",
            "incentive_amount": 5.00,
            "status": "active"
        },
        {
            "title": "邀请3人组队挑战",
            "description": "组建3人小队完成挑战任务，瓜分1000元奖金池",
            "type": "invite",
            "incentive_type": "red_packet",
            "incentive_amount": 100.00,
            "status": "active"
        },
        {
            "title": "老带新专属福利",
            "description": "邀请新用户首次消费，获得消费金额10%返现",
            "type": "invite",
            "incentive_type": "red_packet",
            "incentive_amount": 50.00,
            "status": "active"
        },
        # 签到类活动
        {
            "title": "每日签到领积分",
            "description": "连续签到7天可获得额外100积分奖励",
            "type": "checkin",
            "incentive_type": "points",
            "incentive_amount": 50.00,
            "status": "active"
        },
        {
            "title": "月度签到挑战",
            "description": "本月签到满20天，获得200积分大礼包",
            "type": "checkin",
            "incentive_type": "points",
            "incentive_amount": 200.00,
            "status": "active"
        },
        # 问卷/答题类活动
        {
            "title": "完成问卷调查",
            "description": "完成用户偏好问卷，帮助我们更好地为您推荐",
            "type": "quiz",
            "incentive_type": "points",
            "incentive_amount": 200.00,
            "status": "active"
        },
        {
            "title": "知识问答挑战",
            "description": "参与每日知识问答，答对5题获得50积分",
            "type": "quiz",
            "incentive_type": "points",
            "incentive_amount": 50.00,
            "status": "active"
        },
        {
            "title": "产品体验反馈",
            "description": "填写产品体验问卷，获得专属优惠券",
            "type": "quiz",
            "incentive_type": "coupon",
            "incentive_amount": 20.00,
            "status": "active"
        },
        # 分享类活动
        {
            "title": "分享活动到朋友圈",
            "description": "分享任意活动到朋友圈，截图上传即可获得奖励",
            "type": "share",
            "incentive_type": "points",
            "incentive_amount": 100.00,
            "status": "active"
        },
        {
            "title": "社交达人计划",
            "description": "分享商品到3个社交平台，获得额外红包奖励",
            "type": "share",
            "incentive_type": "red_packet",
            "incentive_amount": 15.00,
            "status": "active"
        },
        {
            "title": "晒单有礼",
            "description": "分享购物心得到社区，获得积分奖励",
            "type": "share",
            "incentive_type": "points",
            "incentive_amount": 80.00,
            "status": "active"
        },
        # 任务类活动
        {
            "title": "新手任务礼包",
            "description": "完成新手引导任务，领取专属礼包",
            "type": "task",
            "incentive_type": "coupon",
            "incentive_amount": 30.00,
            "status": "active"
        },
        {
            "title": "每周任务挑战",
            "description": "完成本周5个任务，获得神秘大奖",
            "type": "task",
            "incentive_type": "red_packet",
            "incentive_amount": 20.00,
            "status": "active"
        },
        {
            "title": "成长任务计划",
            "description": "完成成长任务升级会员等级，享受更多权益",
            "type": "task",
            "incentive_type": "points",
            "incentive_amount": 300.00,
            "status": "active"
        },
        # 学习类活动
        {
            "title": "观看教程视频",
            "description": "观看平台使用教程，了解更多功能",
            "type": "learn",
            "incentive_type": "points",
            "incentive_amount": 80.00,
            "status": "active"
        },
        {
            "title": "新功能体验官",
            "description": "学习并体验新功能，提交反馈获得奖励",
            "type": "learn",
            "incentive_type": "coupon",
            "incentive_amount": 25.00,
            "status": "active"
        },
        # 购买类活动
        {
            "title": "首次购买返现",
            "description": "首次购买任意商品，返现10%",
            "type": "purchase",
            "incentive_type": "red_packet",
            "incentive_amount": 10.00,
            "status": "active"
        },
        {
            "title": "满减优惠活动",
            "description": "单笔消费满100元，立减20元",
            "type": "purchase",
            "incentive_type": "coupon",
            "incentive_amount": 20.00,
            "status": "active"
        },
        {
            "title": "会员专享折扣",
            "description": "会员购买指定商品享8折优惠",
            "type": "purchase",
            "incentive_type": "coupon",
            "incentive_amount": 50.00,
            "status": "active"
        },
        # 评价类活动
        {
            "title": "评价商品得积分",
            "description": "对已购商品进行评价，每条评价得20积分",
            "type": "review",
            "incentive_type": "points",
            "incentive_amount": 20.00,
            "status": "active"
        },
        {
            "title": "优质评价奖励",
            "description": "发布带图评价，获得双倍积分奖励",
            "type": "review",
            "incentive_type": "points",
            "incentive_amount": 40.00,
            "status": "active"
        },
        {
            "title": "视频评价达人",
            "description": "发布视频评价，获得红包奖励",
            "type": "review",
            "incentive_type": "red_packet",
            "incentive_amount": 10.00,
            "status": "active"
        },
        # 抽奖类活动
        {
            "title": "参与抽奖活动",
            "description": "每日免费抽奖一次，有机会获得大奖",
            "type": "lottery",
            "incentive_type": "points",
            "incentive_amount": 10.00,
            "status": "active"
        },
        {
            "title": "幸运大转盘",
            "description": "消费满50元获得一次抽奖机会",
            "type": "lottery",
            "incentive_type": "red_packet",
            "incentive_amount": 88.00,
            "status": "active"
        },
        {
            "title": "周末惊喜抽奖",
            "description": "周末登录即可参与抽奖，100%中奖",
            "type": "lottery",
            "incentive_type": "coupon",
            "incentive_amount": 15.00,
            "status": "active"
        },
        # 社区互动类活动
        {
            "title": "社区互动达人",
            "description": "在社区发帖或评论，获得积分奖励",
            "type": "community",
            "incentive_type": "points",
            "incentive_amount": 30.00,
            "status": "active"
        },
        {
            "title": "话题讨论参与",
            "description": "参与热门话题讨论，优质回答获得红包",
            "type": "community",
            "incentive_type": "red_packet",
            "incentive_amount": 8.00,
            "status": "active"
        },
        # 会员专属活动
        {
            "title": "会员日专属福利",
            "description": "每月8号会员日，享受专属折扣和积分翻倍",
            "type": "member",
            "incentive_type": "points",
            "incentive_amount": 100.00,
            "status": "active"
        },
        {
            "title": "VIP升级礼包",
            "description": "升级VIP会员，获得专属大礼包",
            "type": "member",
            "incentive_type": "coupon",
            "incentive_amount": 100.00,
            "status": "active"
        },
        # 节日活动
        {
            "title": "新年红包雨",
            "description": "新年期间登录即可领取随机红包",
            "type": "festival",
            "incentive_type": "red_packet",
            "incentive_amount": 66.00,
            "status": "active"
        },
        {
            "title": "双十一狂欢",
            "description": "双十一期间消费满减，最高减200元",
            "type": "festival",
            "incentive_type": "coupon",
            "incentive_amount": 200.00,
            "status": "active"
        }
    ]
    
    # 检查是否已有活动
    existing_count = db.query(Activity).count()
    if existing_count < 20:  # 如果活动少于20个，添加新活动
        # 获取已存在的活动标题
        existing_titles = set(a.title for a in db.query(Activity).all())
        added_count = 0
        for data in activities_data:
            if data["title"] not in existing_titles:
                activity = Activity(**data)
                db.add(activity)
                added_count += 1
        db.commit()
        print(f"✅ 已添加 {added_count} 个新活动（原有 {existing_count} 个）")
    else:
        print(f"ℹ️ 数据库已有 {existing_count} 个活动，跳过创建")
    
    # 2. 创建管理员账户（如果不存在）
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            email="admin@example.com",
            role="ADMIN",
            status=1
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # 创建管理员画像
        admin_profile = UserProfile(
            user_id=admin.id,
            factor_social=0.8,
            factor_psych=0.7,
            factor_incent=0.6,
            factor_tech=0.9,
            factor_env=0.5,
            factor_personal=0.7,
            cluster_id=0
        )
        db.add(admin_profile)
        db.commit()
        print("✅ 已创建管理员账户: admin / admin123")
    else:
        print("ℹ️ 管理员账户已存在")
    
    # 3. 创建测试用户（如果不存在）
    test_user = db.query(User).filter(User.username == "test").first()
    if not test_user:
        test_user = User(
            username="test",
            password=get_password_hash("test123"),
            email="test@example.com",
            role="USER",
            status=1
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # 创建测试用户画像
        test_profile = UserProfile(
            user_id=test_user.id,
            factor_social=0.6,
            factor_psych=0.5,
            factor_incent=0.7,
            factor_tech=0.4,
            factor_env=0.6,
            factor_personal=0.5,
            cluster_id=1
        )
        db.add(test_profile)
        db.commit()
        print("✅ 已创建测试用户: test / test123")
    else:
        print("ℹ️ 测试用户已存在")
    
    # 4. 创建测试奖励数据
    test_user = db.query(User).filter(User.username == "test").first()
    existing_rewards = db.query(Reward).filter(Reward.user_id == test_user.id).count()
    if existing_rewards == 0:
        activities = db.query(Activity).limit(5).all()
        rewards_data = [
            {"reward_type": "red_packet", "amount": 5.00, "status": "completed"},
            {"reward_type": "points", "amount": 100, "status": "completed"},
            {"reward_type": "red_packet", "amount": 10.00, "status": "pending"},
            {"reward_type": "coupon", "amount": 30.00, "status": "pending"},
            {"reward_type": "points", "amount": 50, "status": "expired"},
        ]
        for i, data in enumerate(rewards_data):
            reward = Reward(
                user_id=test_user.id,
                activity_id=activities[i % len(activities)].id,
                **data
            )
            db.add(reward)
        db.commit()
        print(f"✅ 已创建 {len(rewards_data)} 条测试奖励记录")
    else:
        print(f"ℹ️ 测试用户已有 {existing_rewards} 条奖励记录")
    
    print("\n🎉 测试数据初始化完成！")
    print("现在可以用以下账户登录：")
    print("  管理员: admin / admin123")
    print("  普通用户: test / test123")

except Exception as e:
    print(f"❌ 错误: {e}")
    db.rollback()
finally:
    db.close()
