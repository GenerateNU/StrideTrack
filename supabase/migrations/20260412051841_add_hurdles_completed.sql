ALTER TABLE RUN ADD COLUMN hurdles_completed INTEGER DEFAULT NULL;
 
ALTER TABLE RUN ADD CONSTRAINT chk_hurdles_completed_values
    CHECK (hurdles_completed IS NULL OR hurdles_completed BETWEEN 1 AND 10);
 
