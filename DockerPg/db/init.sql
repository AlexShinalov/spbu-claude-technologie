CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO items (name) VALUES
('First item'),
('Second item'),
('Third item');
