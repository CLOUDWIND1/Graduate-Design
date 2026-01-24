"""
SQL 用于创建 `recommendations` 表。保留原始 SQL 作为字符串，方便在迁移或初始化脚本中使用。
"""
create_recommendations_table_sql = """
CREATE TABLE `recommendations` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `activity_id` INT NOT NULL COMMENT '活动ID',
    `score` DECIMAL(5,4) COMMENT '接受概率评分',
    `reason` TEXT COMMENT '推荐理由',
    `features` JSON COMMENT '特征重要性数据',
    `is_clicked` TINYINT DEFAULT 0 COMMENT '是否点击',
    `is_accepted` TINYINT DEFAULT 0 COMMENT '是否接受',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`activity_id`) REFERENCES `activities`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_time` (`user_id`, `created_at`),
    INDEX `idx_activity` (`activity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推荐记录表';
"""
