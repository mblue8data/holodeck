-- Create metabase user and analytics database (required by Metabase service)
CREATE USER metabase WITH PASSWORD 'metapass';
CREATE DATABASE analytics OWNER metabase;
GRANT ALL PRIVILEGES ON DATABASE analytics TO metabase;

-- Create training schemas in the default mydb database
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Sample raw table for training exercises
CREATE TABLE IF NOT EXISTS raw.transactions (
    id          SERIAL PRIMARY KEY,
    user_id     INT,
    amount      NUMERIC(10, 2),
    currency    VARCHAR(3),
    status      VARCHAR(20),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.customers (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    email       VARCHAR(100),
    country     VARCHAR(50),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Seed a small sample so learners have data on first boot
INSERT INTO raw.customers (name, email, country) VALUES
    ('Alice Nguyen',   'alice@example.com',   'US'),
    ('Bob Okafor',     'bob@example.com',     'NG'),
    ('Clara Müller',   'clara@example.com',   'DE'),
    ('David Kim',      'david@example.com',   'KR'),
    ('Eva Petrov',     'eva@example.com',     'RU');

INSERT INTO raw.transactions (user_id, amount, currency, status) VALUES
    (1, 120.50, 'USD', 'completed'),
    (2,  45.00, 'USD', 'completed'),
    (3, 300.00, 'EUR', 'pending'),
    (4,  15.99, 'KRW', 'failed'),
    (5,  89.00, 'USD', 'completed'),
    (1, 220.00, 'USD', 'completed'),
    (3,  60.00, 'EUR', 'completed');
