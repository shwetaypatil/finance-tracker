BEGIN;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(200) NOT NULL,
  profile_pic VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  theme TEXT DEFAULT 'light',
  language TEXT DEFAULT 'en'
);

CREATE TABLE user_settings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  theme TEXT DEFAULT 'light' CHECK (theme IN ('light','dark')),
  language VARCHAR(10) DEFAULT 'en',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE budget (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount NUMERIC(10,2) NOT NULL,
  month INTEGER NOT NULL,
  year INTEGER NOT NULL,
  UNIQUE (user_id, month, year)
);

CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(10) NOT NULL CHECK (type IN ('Income','Expense')),
  category VARCHAR(50) NOT NULL,
  amount NUMERIC(10,2) NOT NULL,
  date DATE NOT NULL,
  note VARCHAR(255),
  title VARCHAR(255) NOT NULL
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_settings_set_updated_at
BEFORE UPDATE ON user_settings
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO users (id, username, first_name, last_name, email, password, profile_pic, created_at, theme, language) VALUES
(5, 'John Doe', 'John', 'Doe', 'johndoe01@gmail.com', '$2b$12$E/o7E11dhudUEYccpBtvweL8MESirI9FTuUhZatV1Di0DHq1ykbTm', NULL, '2026-03-11 06:55:10', 'light', 'en'),
(6, 'Alex Miller', 'Alex', 'Miller', 'alexmiller12@gmail.com', '$2b$12$ZLbw9spSqpKhQ0Ec.GpP9.gom0wqRVVJr05Oy/kjn5GJnPdj52aTO', NULL, '2026-03-11 06:56:16', 'light', 'en');

INSERT INTO budget (id, user_id, amount, month, year) VALUES
(5, 6, 800.00, 3, 2026);

INSERT INTO transactions (id, user_id, type, category, amount, date, note, title) VALUES
(14, 6, 'Income', 'salary', 3000.00, '2026-03-11', '', 'stipend'),
(15, 6, 'Expense', 'transport', 40.00, '2026-03-11', '', 'bus fair'),
(16, 6, 'Expense', 'groceries', 40.00, '2026-03-13', '', 'coffee'),
(17, 6, 'Expense', 'groceries', 30.00, '2026-03-13', '', 'Tea');

INSERT INTO user_settings (id, user_id, theme, language, created_at, updated_at) VALUES
(4, 5, 'light', 'en', '2026-03-11 06:55:10', '2026-03-11 06:55:10'),
(5, 6, 'light', 'en', '2026-03-11 06:56:16', '2026-03-11 06:56:16');

SELECT setval(pg_get_serial_sequence('users','id'), (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('budget','id'), (SELECT MAX(id) FROM budget));
SELECT setval(pg_get_serial_sequence('transactions','id'), (SELECT MAX(id) FROM transactions));
SELECT setval(pg_get_serial_sequence('user_settings','id'), (SELECT MAX(id) FROM user_settings));

COMMIT;
