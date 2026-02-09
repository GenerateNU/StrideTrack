CREATE TABLE RUN_METRICS (
    metric_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT,
    start_time NUMERIC,
    end_time NUMERIC,
    foot TEXT,
    seq INTEGER,
    CONSTRAINT fk_run_metrics_run
        FOREIGN KEY (run_id)
        REFERENCES RUN(run_id)
        ON DELETE CASCADE
);