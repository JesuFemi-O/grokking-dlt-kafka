-- Allow replication and logical decoding
ALTER SYSTEM SET wal_level = logical;

-- Reload configuration
SELECT pg_reload_conf();

create schema if not exists app;
set search_path = app, public;

-- customers
create table if not exists customers (
    id serial primary key,
    email text not null unique,
    full_name text not null,
    customer_type text not null check (customer_type in ('mobile','web','ussd')),
    created_at timestamptz not null default now()
);

-- products
create table if not exists products (
    id serial primary key,
    sku text not null unique,
    name text not null,
    price numeric(10,2) not null check (price >= 0),
    created_at timestamptz not null default now()
);

-- orders (single-product orders for simplicity)
create table if not exists orders (
    id serial primary key,
    customer_id integer not null references app.customers(id),
    product_id integer not null references app.products(id),
    quantity integer not null check (quantity > 0),
    status text not null check (status in ('pending','paid','shipped','cancelled')),
    order_total numeric(12,2) not null,
    created_at timestamptz not null default now()
);

-- seed customers
insert into customers (email, full_name, customer_type) values
('ada@example.com', 'ada okafor', 'web'),
('tunde@example.com', 'tunde adeyemi', 'mobile'),
('chi@example.com', 'chimamanda eze', 'ussd'),
('ibrahim@example.com', 'ibrahim bello', 'web'),
('lola@example.com', 'lola akinwale', 'mobile'),
('uche@example.com', 'uche ndukwe', 'web')
on conflict (email) do nothing;

-- seed products
insert into products (sku, name, price) values
('SKU-1001', 'wireless mouse', 24.99),
('SKU-1002', 'mechanical keyboard', 89.50),
('SKU-1003', 'usb-c hub 6-in-1', 39.00),
('SKU-1004', '27-inch monitor', 229.99),
('SKU-1005', 'noise-cancelling headphones', 149.00),
('SKU-1006', 'laptop stand', 34.50)
on conflict (sku) do nothing;

-- seed orders
insert into orders (customer_id, product_id, quantity, status, order_total) values
(1, 2, 1, 'paid',      89.50),
(1, 1, 2, 'shipped',   49.98),
(2, 4, 1, 'paid',     229.99),
(3, 3, 1, 'pending',   39.00),
(4, 5, 1, 'paid',     149.00),
(5, 6, 1, 'shipped',   34.50),
(6, 2, 1, 'paid',      89.50),
(2, 1, 1, 'cancelled', 24.99),
(3, 5, 2, 'paid',     298.00),
(4, 3, 3, 'paid',     117.00);

grant usage on schema app to postgres;
grant select, insert, update, delete on all tables in schema app to postgres;
alter default privileges in schema app grant select, insert, update, delete on tables to postgres;

-- notes for debezium:
-- 1) all tables have primary keys (required).
-- 2) if you later need before-image records for updates without pk changes, you can:
--    alter table app.orders replica identity full;