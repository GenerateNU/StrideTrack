-- Create role enum
CREATE TYPE role_enum AS ENUM ('coach', 'athlete');

-- Create profiles table
CREATE TABLE profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    auth_user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role role_enum NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Add profile_id to coaches
ALTER TABLE coaches
ADD COLUMN profile_id UUID REFERENCES profiles(profile_id);

-- Drop name from coaches (now in profiles)
ALTER TABLE coaches
DROP COLUMN name;

-- Create index for profile lookups by auth_user_id
CREATE INDEX idx_profiles_auth_user_id ON profiles(auth_user_id);