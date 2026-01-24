"""
SQL 用于创建 `activities` 表。保留原始 SQL 作为字符串，方便在迁移或初始化脚本中使用。
"""
create_activities_table_sql = """
CREATE TABLE `activities` (
    `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '活动ID',
    `title` VARCHAR(100) NOT NULL COMMENT '活动标题',
    `description` TEXT COMMENT '活动描述',
    `type` VARCHAR(50) COMMENT '活动类型：invite/quiz/share',
    `incentive_type` VARCHAR(50) COMMENT '激励类型：red_packet/points/coupon',
    `incentive_amount` DECIMAL(10,2) COMMENT '激励金额',
    `target_cluster` VARCHAR(50) COMMENT '目标用户群体',
    `start_time` DATETIME COMMENT '开始时间',
    `end_time` DATETIME COMMENT '结束时间',
    `status` ENUM('draft', 'active', 'paused', 'ended') DEFAULT 'draft' COMMENT '状态',
    `view_count` INT DEFAULT 0 COMMENT '浏览量',
    `participate_count` INT DEFAULT 0 COMMENT '参与量',
    `created_by` INT COMMENT '创建人ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_status` (`status`),
    INDEX `idx_time` (`end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动表';
"""

