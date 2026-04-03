-- Backfill any NULL elapsed_ms with the max next_ic_time from run metrics
UPDATE RUN
SET elapsed_ms = sub.max_time
FROM (
    SELECT run_id, MAX(next_ic_time) AS max_time
    FROM RUN_METRICS
    GROUP BY run_id
) sub
WHERE RUN.run_id = sub.run_id
  AND RUN.elapsed_ms IS NULL;

-- Make elapsed_ms required
ALTER TABLE RUN ALTER COLUMN elapsed_ms SET NOT NULL;
