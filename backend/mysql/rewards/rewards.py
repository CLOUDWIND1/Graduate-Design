"""
SQL 用于创建 `rewards` 表。保留原始 SQL 作为字符串，方便在迁移或初始化脚本中使用。
"""
create_rewards_table_sql = """
CREATE TABLE `rewards` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `activity_id` INT COMMENT '关联活动ID',
    `type` VARCHAR(50) COMMENT '奖励类型：red_packet/points/coupon',
    `amount` DECIMAL(10,2) NOT NULL COMMENT '奖励金额',
    `status` ENUM('pending', 'issued', 'failed') DEFAULT 'pending' COMMENT '状态',
    `description` TEXT COMMENT '奖励说明',
    `issued_at` DATETIME COMMENT '发放时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='奖励记录表';
"""
