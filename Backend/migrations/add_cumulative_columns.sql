-- Migration: Add cumulative production and defects columns to machine_logs table
-- Purpose: Store cumulative production data from sensor simulator for accurate auto-prediction
-- Date: 2025

-- Add new columns
ALTER TABLE machine_logs
ADD COLUMN IF NOT EXISTS cumulative_production INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS cumulative_defects INTEGER DEFAULT 0;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_machine_logs_timestamp_desc 
ON machine_logs (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machine_logs_cumulative 
ON machine_logs (cumulative_production, cumulative_defects);

-- Add comments for documentation
COMMENT ON COLUMN machine_logs.cumulative_production IS 
'Cumulative production count (pcs) for current shift (8 hours)';

COMMENT ON COLUMN machine_logs.cumulative_defects IS 
'Cumulative defects count (pcs) for current shift (8 hours)';

-- Verify the changes
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'machine_logs'
ORDER BY ordinal_position;
