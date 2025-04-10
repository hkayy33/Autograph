CREATE TABLE autographs (
    id SERIAL PRIMARY KEY,
    instagram_url VARCHAR(500) UNIQUE NOT NULL,
    encrypted_code TEXT NOT NULL,
    raw_code VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert example record 1
INSERT INTO autographs (instagram_url, encrypted_code, raw_code, created_at)
VALUES (
    'https://instagram.com/p/test123',
    'gAAAAABjKbY5hBv7Jx8P3m2Qj4ZkLXRyM9pQHzV8KfL2nXJH7tU=',  -- Example encrypted value
    'TEST123',
    CURRENT_TIMESTAMP
);

-- Insert example record 2
INSERT INTO autographs (instagram_url, encrypted_code, raw_code, created_at)
VALUES (
    'https://instagram.com/p/celebritypost456',
    'gAAAAABjKbx4R2FvHgTy7LpMn3BzXw9s8vQkPz2HjKlM5bTrRvE=',  -- Example encrypted value
    'CELEB456',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
);

-- Insert example record 3
INSERT INTO autographs (instagram_url, encrypted_code, raw_code, created_at)
VALUES (
    'https://instagram.com/p/fashionbrand789',
    'gAAAAABjKcZ3WpL8sT6yRqNvFmKjHxG4z9DtBvCnQsSp7XyE1aA=',  -- Example encrypted value
    'BRAND789',
    CURRENT_TIMESTAMP - INTERVAL '5 days'
);