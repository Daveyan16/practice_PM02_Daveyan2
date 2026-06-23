USE myprojectdb;

DELETE FROM Пользователи;

INSERT INTO Пользователи (логин, пароль_hash, роль) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYrMfQvS5uy', 'admin'),
('worker', '$2b$12$fVb7YhYqZ5jKpLmR2nXqQeVZqWxYtUjMkLpO9iKjHnMvBcXzZaCq', 'worker');