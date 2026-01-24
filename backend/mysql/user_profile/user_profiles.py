"""
SQL 用于创建 `user_profiles` 表。保留原始 SQL 作为字符串，方便在迁移或初始化脚本中使用。
"""
create_user_profiles_table_sql = """
CREATE TABLE `user_profiles` (
    `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id` INT NOT NULL UNIQUE COMMENT '用户ID',
    `factor_social` DECIMAL(5,3) COMMENT '社会因素得分',
    `factor_psych` DECIMAL(5,3) COMMENT '心理因素得分',
    `factor_incent` DECIMAL(5,3) COMMENT '激励因素得分',
    `factor_tech` DECIMAL(5,3) COMMENT '技术因素得分',
    `factor_env` DECIMAL(5,3) COMMENT '环境因素得分',
    `factor_personal` DECIMAL(5,3) COMMENT '个人因素得分',
    `cluster_tag` VARCHAR(20) COMMENT '分群标签',
    `total_score` DECIMAL(5,3) COMMENT '综合接受度得分',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_cluster` (`cluster_tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户画像表';
"""