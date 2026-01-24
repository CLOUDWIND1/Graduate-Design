"""临时迁移脚本：为 activities.status 添加 paused 状态"""
import pymysql

# 从配置读取或使用默认值
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='recommendation_system'
)

try:
    with conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE activities 
            MODIFY COLUMN status ENUM('draft', 'active', 'paused', 'ended') 
            DEFAULT 'draft'
        """)
    conn.commit()
    print("✅ 成功：activities.status ENUM 已更新，现在支持 paused 状态")
except Exception as e:
    print(f"❌ 失败：{e}")
finally:
    conn.close()
