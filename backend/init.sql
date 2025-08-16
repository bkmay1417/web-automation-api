CREATE TABLE IF NOT EXISTS tasks (
    job_id UUID PRIMARY KEY,
    status VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES tasks(job_id),
    name TEXT,
    price TEXT,
    description TEXT,
    image_url TEXT
);
