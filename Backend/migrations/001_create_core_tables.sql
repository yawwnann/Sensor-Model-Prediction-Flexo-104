
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'user', 'operator'))
);

-- Indexes
CREATE INDEX idx_users_username ON public.users (username);
CREATE INDEX idx_users_email ON public.users (email);
CREATE INDEX idx_users_role ON public.users (role);
CREATE INDEX idx_users_is_active ON public.users (is_active);

-- Trigger to update updated_at automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ======================================
-- 2️⃣  TABLE: user_sessions
-- ======================================
CREATE TABLE public.user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON public.user_sessions (user_id);
CREATE INDEX idx_sessions_token ON public.user_sessions (session_token);
CREATE INDEX idx_sessions_expires_at ON public.user_sessions (expires_at);


-- ======================================
-- 3️⃣  TABLE: machine_logs
-- ======================================
CREATE TABLE public.machine_logs (
    id SERIAL PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL,
    machine_status VARCHAR(50),
    performance_rate REAL,
    quality_rate REAL,
    cumulative_production INTEGER DEFAULT 0,
    cumulative_defects INTEGER DEFAULT 0,
    availability_rate REAL DEFAULT 0.0
);

-- Indexes
CREATE INDEX idx_machine_logs_timestamp_desc ON public.machine_logs ("timestamp" DESC);
CREATE INDEX idx_machine_logs_cumulative ON public.machine_logs (cumulative_production, cumulative_defects);


-- ======================================
-- 4️⃣  TABLE: components
-- ======================================
CREATE TABLE public.components (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    rpn_value INTEGER NOT NULL
);

-- End of migration
