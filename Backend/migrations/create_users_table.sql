-- Migration: Create users table for authentication
-- Date: 2025-10-25
-- Description: Create users table with proper authentication fields

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'operator')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
-- Hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'admin',
    'admin@flexo104.com',
    '$2b$12$LQv3c1yqBw2RFjgzIH9B6.JQEcYm8M8KzYU1VfkFcXeM7YM6j8rKq',
    'System Administrator',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Insert default operator user (password: operator123)
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'operator',
    'operator@flexo104.com',
    '$2b$12$8XF7gYn9ZqMK4L2vP6tR8.Qwe5rt6YuH7K8jP9LmN3qR5sT7vW2Xy',
    'Machine Operator',
    'operator'
) ON CONFLICT (username) DO NOTHING;

-- Create sessions table for session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Create index for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts for system authentication and authorization';
COMMENT ON COLUMN users.username IS 'Unique username for login';
COMMENT ON COLUMN users.email IS 'User email address';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN users.role IS 'User role: admin, user, or operator';
COMMENT ON COLUMN users.is_active IS 'Whether user account is active';
COMMENT ON COLUMN users.login_attempts IS 'Number of failed login attempts';
COMMENT ON COLUMN users.locked_until IS 'Account locked until this timestamp';

COMMENT ON TABLE user_sessions IS 'Active user sessions for authentication';
COMMENT ON COLUMN user_sessions.session_token IS 'Unique session token for authentication';
COMMENT ON COLUMN user_sessions.expires_at IS 'Session expiration timestamp';

-- Verify the migration
SELECT 
    'users' as table_name,
    COUNT(*) as total_users,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin_users,
    COUNT(CASE WHEN role = 'operator' THEN 1 END) as operator_users,
    COUNT(CASE WHEN is_active = true THEN 1 END) as active_users
FROM users
UNION ALL
SELECT 
    'user_sessions' as table_name,
    COUNT(*) as total_sessions,
    NULL as admin_users,
    NULL as operator_users,
    COUNT(CASE WHEN expires_at > CURRENT_TIMESTAMP THEN 1 END) as active_sessions
FROM user_sessions;