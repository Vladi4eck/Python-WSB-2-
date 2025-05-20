-- Drop tables
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments;
DROP TYPE IF EXISTS order_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

-- -- ENUM Types
CREATE TYPE order_status AS ENUM ('new', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'error');
CREATE TYPE user_role AS ENUM ('administrator', 'client');

-- Usery
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'client',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SELECT * FROM order_items;  

-- Produkty
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock INT NOT NULL CHECK (stock >= 0)
);

-- Zamówienia
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status order_status NOT NULL DEFAULT 'new'
);

-- Produkty w koszyku
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    PRIMARY KEY (order_id, product_id)
);

-- Płatności
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    status payment_status NOT NULL
);

-- Decrease stock
Create or replace function 	decrease_stock()
RETURNS TRIGGER AS $$
BEGIN 
	UPDATE products
	SET stock = stock - NEW.quantity
	WHERE id = NEW.product_id;

	RETURN NEW;
END;
$$Language plpgsql;

CREATE TRIGGER trg_descrease_stock
AFTER INSERT ON order_items
FOR EACH ROW 
EXECUTE FUNCTION decrease_stock();

-- Update order status
CREATE OR REPLACE FUNCTION update_order_status_after_payment()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'paid' THEN
    UPDATE orders
    SET status = 'processing'
    WHERE id = NEW.order_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_order_status
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION update_order_status_after_payment();
-- Inserts
INSERT INTO users (name, email, password, role) VALUES  ('Admin', 'admin@shop.com', 'HASHED_PASSWORD', 'administrator'), ('Piotr', 'piotr@example.com', 'HASHED_PASSWORD', 'client');
INSERT INTO products (name, description, price, stock) VALUES ('Item A', 'Description of item A', 10.00, 100) ,('Parasol','Description','30.42',30), ('B','Beescription','20','25');
INSERT INTO orders (user_id, status) VALUES (1, 'new')
RETURNING id;
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1,1,3,10.00);
INSERT INTO payments (order_id, payment_method, amount, status) VALUES (1, 'card', 10.00, 'paid');
-- select * from products
