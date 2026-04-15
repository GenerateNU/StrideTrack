ALTER TABLE athletes
ADD COLUMN gender VARCHAR(10) CHECK (gender IN ('male', 'female')) DEFAULT NULL;