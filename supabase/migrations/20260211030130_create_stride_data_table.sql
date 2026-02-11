-- Create stride_data table
CREATE TABLE IF NOT EXISTS stride_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stride_num INTEGER NOT NULL,
    foot VARCHAR(10) NOT NULL CHECK (foot IN ('left', 'right')),
    ic_time INTEGER NOT NULL CHECK (ic_time >= 0),
    to_time INTEGER NOT NULL CHECK (to_time >= 0),
    next_ic_time INTEGER NOT NULL CHECK (next_ic_time >= 0),
    gct_ms INTEGER NOT NULL CHECK (gct_ms >= 0),
    flight_ms INTEGER NOT NULL CHECK (flight_ms >= 0),
    step_time_ms INTEGER NOT NULL CHECK (step_time_ms >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
-- Add indexes for common queries
CREATE INDEX idx_stride_data_stride_num ON stride_data(stride_num);
CREATE INDEX idx_stride_data_foot ON stride_data(foot);