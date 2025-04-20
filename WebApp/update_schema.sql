-- Drop existing tables if they exist
DROP TABLE IF EXISTS autographs;
DROP TABLE IF EXISTS invite_codes;

-- Create autographs table
CREATE TABLE autographs (
    id SERIAL PRIMARY KEY,
    instagram_url VARCHAR(255) NOT NULL,
    encryption_code TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create invite_codes table
CREATE TABLE invite_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(32) NOT NULL UNIQUE,
    instagram_handle VARCHAR(80) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE
); 