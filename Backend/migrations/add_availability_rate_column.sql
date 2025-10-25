-- Migration: Add availability_rate column to machine_logs table
-- Date: 2025-10-25
-- Description: Add availability_rate column to track machine availability in OEE calculations

ALTER TABLE machine_logs 
ADD COLUMN availability_rate REAL DEFAULT 0.0;

-- Add comment for documentation
COMMENT ON COLUMN machine_logs.availability_rate IS 'Machine availability rate in percentage (0-100). Part of OEE calculation.';

-- Update any existing records to have default availability_rate based on machine_status
UPDATE machine_logs 
SET availability_rate = CASE 
    WHEN machine_status = 'Running' THEN 85.0
    ELSE 0.0
END
WHERE availability_rate IS NULL;

-- Verify the migration
SELECT 
    COUNT(*) as total_records,
    AVG(availability_rate) as avg_availability,
    COUNT(CASE WHEN availability_rate = 0 THEN 1 END) as zero_availability_count,
    COUNT(CASE WHEN availability_rate > 0 THEN 1 END) as positive_availability_count
FROM machine_logs;