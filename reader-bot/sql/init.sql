CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    status TEXT NOT NULL CHECK (status IN ('прочитано', 'читаю', 'в планах')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
