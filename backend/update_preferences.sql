-- Add preference columns to user_profiles table
ALTER TABLE user_profiles 
ADD COLUMN preference_frequency VARCHAR(20) DEFAULT 'daily',
ADD COLUMN preference_activity_types VARCHAR(255) DEFAULT 'invite,quiz,share',
ADD COLUMN preference_incentive_types VARCHAR(255) DEFAULT 'red_packet,points,coupon';
