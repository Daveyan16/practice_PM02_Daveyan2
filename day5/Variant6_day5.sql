-- ФИО: Давеян Эльмира Гайковна
-- Группа: 24-ИС
-- Вариант 6. Интернет-магазин

-- Задание 1
DROP DATABASE IF EXISTS Variant6_day5;
CREATE DATABASE Variant6_day5;
USE Variant6_day5;

-- Задание 2. Products
CREATE TABLE Products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL
);

-- Задание 3. Categories
CREATE TABLE Categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Задание 4. ProductCategories
CREATE TABLE ProductCategories (
    product_id INT,
    category_id INT,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES Products(id),
    FOREIGN KEY (category_id) REFERENCES Categories(id)
);

-- Задание 5. Customers, Orders, OrderItems, Reviews
CREATE TABLE Customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
);

CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
);

CREATE TABLE OrderItems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

CREATE TABLE Reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    review_text TEXT,
    rating INT,
    review_date DATE,
    FOREIGN KEY (product_id) REFERENCES Products(id),
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
);

-- Задание 6. Товары
INSERT INTO Products (name, price, stock) VALUES
('Ноутбук', 75000, 10),
('Мышь', 1200, 50),
('Клавиатура', 3500, 30),
('Монитор', 18000, 15),
('Колонки', 4500, 20);

-- Задание 7. Категории
INSERT INTO Categories (name) VALUES
('Электроника'),
('Периферия'),
('Аксессуары');

-- Задание 8. Связать товары и категории
INSERT INTO ProductCategories VALUES
(1,1),
(2,2),
(2,3),
(3,2),
(4,1),
(5,3);

-- Задание 9. Покупатели
INSERT INTO Customers (full_name, phone) VALUES
('Иванов Иван Иванович', '89991111111'),
('Петров Петр Петрович', '89992222222'),
('Сидоров Сергей Сергеевич', '89993333333');

-- Задание 10. Заказы
INSERT INTO Orders (customer_id, order_date, status) VALUES
(1, '2025-04-01', 'Выполнен'),
(2, '2025-04-02', 'Отменён');

-- Задание 11. Позиции заказов
INSERT INTO OrderItems (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1);

-- Задание 12. Отзывы
INSERT INTO Reviews (product_id, customer_id, review_text, rating, review_date) VALUES
(1, 1, 'Отличный ноутбук', 5, '2025-04-05'),
(1, 2, 'Хороший товар', 4, '2025-04-06'),
(2, 3, 'Удобная мышь', 5, '2025-04-07');

-- Задание 13
SELECT *
FROM Products
WHERE price > 5000;

-- Задание 14
SELECT o.id,
       o.order_date,
       o.status,
       c.full_name
FROM Orders o
JOIN Customers c
ON o.customer_id = c.id
WHERE c.full_name LIKE '%Петров%';

-- Задание 15
SELECT *
FROM Products
ORDER BY stock DESC;

-- Задание 16
SELECT AVG(r.rating) AS avg_rating
FROM Reviews r
JOIN Products p
ON r.product_id = p.id
WHERE p.name = 'Ноутбук';

-- Задание 17
SELECT oi.order_id,
       SUM(p.price * oi.quantity) AS total_sum
FROM OrderItems oi
JOIN Products p
ON oi.product_id = p.id
WHERE oi.order_id = 1
GROUP BY oi.order_id;

-- Задание 18
SELECT c.name,
       COUNT(pc.product_id) AS product_count
FROM Categories c
LEFT JOIN ProductCategories pc
ON c.id = pc.category_id
GROUP BY c.id, c.name;

-- Задание 19
SELECT c.name,
       COUNT(pc.product_id) AS product_count
FROM Categories c
JOIN ProductCategories pc
ON c.id = pc.category_id
GROUP BY c.id, c.name
HAVING COUNT(pc.product_id) > 2;

-- Задание 20
SELECT p.*
FROM Products p
LEFT JOIN Reviews r
ON p.id = r.product_id
WHERE r.id IS NULL;

-- Задание 21
UPDATE Products p
JOIN ProductCategories pc
ON p.id = pc.product_id
JOIN Categories c
ON pc.category_id = c.id
SET p.price = p.price* 1.10
WHERE c.name = 'Электроника';

-- Задание 22
DELETE FROM Orders
WHERE status = 'Отменён';

-- Задание 23
ALTER TABLE Products
ADD discount INT;

-- Задание 24
CREATE VIEW ProductRatings AS
SELECT p.name,
       AVG(r.rating) AS avg_rating
FROM Products p
LEFT JOIN Reviews r
ON p.id = r.product_id
GROUP BY p.id, p.name;

SELECT * FROM ProductRatings;

-- Задание 25
SELECT
    c.full_name,
    SUM(p.price * oi.quantity) AS total_orders_sum,
    SUM(oi.quantity) AS total_products_count,
    AVG(r.rating) AS average_rating
FROM Customers c
LEFT JOIN Orders o
ON c.id = o.customer_id
LEFT JOIN OrderItems oi
ON o.id = oi.order_id
LEFT JOIN Products p
ON oi.product_id = p.id
LEFT JOIN Reviews r
ON c.id = r.customer_id
GROUP BY c.id, c.full_name;