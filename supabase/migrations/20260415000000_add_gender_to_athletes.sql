ALTER TABLE athletes
ADD COLUMN gender VARCHAR(10) NOT NULL
  CHECK (gender IN ('male', 'female', 'other'))
  DEFAULT 'other';
