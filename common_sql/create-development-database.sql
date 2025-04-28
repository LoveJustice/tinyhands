-- Terminate all other connections to the database (DON'T DO THIS ON PROD!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'postgres' AND pid <> pg_backend_pid();

-- Create your development database. Replace with your last name and username.
CREATE DATABASE dev_wilson WITH TEMPLATE postgres OWNER nwilson;
