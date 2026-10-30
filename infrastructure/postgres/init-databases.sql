-- ============================================================
-- Initialize separate databases for each microservice
-- This runs automatically when the PostgreSQL container starts
-- ============================================================

-- Create service databases
CREATE DATABASE user_db;
CREATE DATABASE product_db;
CREATE DATABASE cart_db;
CREATE DATABASE inventory_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE user_db TO ibrat;
GRANT ALL PRIVILEGES ON DATABASE product_db TO ibrat;
GRANT ALL PRIVILEGES ON DATABASE cart_db TO ibrat;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO ibrat;
