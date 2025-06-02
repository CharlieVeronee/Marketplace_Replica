\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' CSV;
-- SELECT pg_catalog.setval('public.inventory_user_id_seq', (SELECT MAX(user_id) + 1 FROM Inventory), false);

\COPY Seller_Reviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.Seller_Reviews_id_seq',
                         (SELECT MAX(id)+1 FROM Seller_Reviews),
                         false);

\COPY Product_Reviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.Product_Reviews_id_seq',
                         (SELECT MAX(id)+1 FROM Product_Reviews),
                         false);

\COPY Cart(id, user_id, product_id, seller_id, quantity, saved, fulfilled, time_fulfilled) FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_id_seq',
                         (SELECT MAX(id)+1 FROM Cart),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                         (SELECT MAX(id)+1 FROM Orders),
                         false);

\COPY Balance FROM 'Balances.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.balances_id_seq',
                        --  (SELECT MAX(id)+1 FROM Balance),
                        --  false);
