ALTER TABLE RUN ADD COLUMN target_event VARCHAR(20) DEFAULT NULL;
 
ALTER TABLE RUN ADD CONSTRAINT chk_target_event_values
    CHECK (target_event IS NULL OR target_event IN ('hurdles_60m', 'hurdles_110m', 'hurdles_100m', 'hurdles_400m'));
 
ALTER TABLE RUN ADD CONSTRAINT chk_partial_requires_target
    CHECK (
        (event_type != 'hurdles_partial') OR
        (event_type = 'hurdles_partial' AND target_event IS NOT NULL)
    );
 