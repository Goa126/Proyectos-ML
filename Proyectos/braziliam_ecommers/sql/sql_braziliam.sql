-- === 1. DEFINICIÓN DE LLAVES PRIMARIAS (PK) ===
ALTER TABLE olist_customers ADD PRIMARY KEY (customer_id);
ALTER TABLE olist_orders ADD PRIMARY KEY (order_id);
ALTER TABLE olist_order_items ADD PRIMARY KEY (order_id, order_item_id);
ALTER TABLE olist_order_payments ADD PRIMARY KEY (order_id, payment_sequential);
ALTER TABLE olist_products ADD PRIMARY KEY (product_id);
ALTER TABLE olist_sellers ADD PRIMARY KEY (seller_id);
ALTER TABLE product_category_name_translation ADD PRIMARY KEY (product_category_name);

DELETE FROM olist_order_reviews WHERE ctid NOT IN (SELECT MIN(ctid) FROM olist_order_reviews GROUP BY review_id);
ALTER TABLE olist_order_reviews ADD PRIMARY KEY (review_id);

-- === 2. DEFINICIÓN DE LLAVES FORÁNEAS (FK) ===
-- Conecta Pedidos con Clientes
ALTER TABLE olist_orders
ADD CONSTRAINT fk_orders_customers
FOREIGN KEY (customer_id) REFERENCES olist_customers (customer_id);

-- Conecta Items con Pedidos
ALTER TABLE olist_order_items
ADD CONSTRAINT fk_items_orders -- Agregué esta que faltaba en tu código
FOREIGN KEY (order_id) REFERENCES olist_orders (order_id);

-- Conecta Items con Productos
ALTER TABLE olist_order_items
ADD CONSTRAINT fk_items_products
FOREIGN KEY (product_id) REFERENCES olist_products (product_id);

-- Conecta Items con Vendedores
ALTER TABLE olist_order_items
ADD CONSTRAINT fk_items_sellers
FOREIGN KEY (seller_id) REFERENCES olist_sellers (seller_id);

-- Conecta Pagos con Pedidos
ALTER TABLE olist_order_payments
ADD CONSTRAINT fk_payments_orders
FOREIGN KEY (order_id) REFERENCES olist_orders (order_id);

-- agregamos la categoria sin traducción y verificamos que no falte otra categoria
INSERT INTO product_category_name_translation (product_category_name, product_category_name_english)
VALUES ('pc_gamer', 'pc_gamer'),
       ('portateis_cozinha_e_preparadores_de_alimentos', 'kitchen_portables_and_food_preparators')
ON CONFLICT (product_category_name) DO NOTHING;

SELECT DISTINCT p.product_category_name
FROM olist_products p
LEFT JOIN product_category_name_translation t 
  ON p.product_category_name = t.product_category_name
WHERE t.product_category_name IS NULL 
  AND p.product_category_name IS NOT NULL;

-- Conecta Productos con su Traducción
ALTER TABLE olist_products
ADD CONSTRAINT fk_products_category
FOREIGN KEY (product_category_name)
REFERENCES product_category_name_translation (product_category_name);

-- Conectar Reseñas con Pedidos
ALTER TABLE olist_order_reviews
ADD CONSTRAINT fk_reviews_orders
FOREIGN KEY (order_id) REFERENCES olist_orders (order_id);

-- Creamos la vista
CREATE OR REPLACE VIEW vista_entrenamiento_ml AS
SELECT 
    o.order_id,
    c.customer_city,
    pct.product_category_name_english, 
    oi.price,
    r.review_score
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_products p ON oi.product_id = p.product_id
JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id;

SELECT * FROM vista_entrenamiento_ml LIMIT 5;

-- Análisis de series temporales
SELECT 
    COUNT(order_purchase_timestamp) AS compras,
    COUNT(order_approved_at) AS aprobaciones,
    COUNT(order_delivered_customer_date) AS entregas_reales,
    COUNT(order_estimated_delivery_date) AS entregas_estimadas
FROM olist_orders;

SELECT 
    DATE_TRUNC('month', order_purchase_timestamp::timestamp) AS mes,
    COUNT(*) AS total_pedidos
FROM olist_orders
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW ds_enriquecido_ml AS
SELECT 
    o.order_id,
    -- Tiempos (Series Temporales)
    o.order_purchase_timestamp::timestamp AS fecha_compra,
    EXTRACT(DAY FROM (o.order_delivered_customer_date::timestamp - o.order_purchase_timestamp::timestamp)) AS dias_entrega_real,
    
    -- Características del Producto (Features)
    p.product_weight_g,
    p.product_length_cm * p.product_height_cm * p.product_width_cm AS volumen_cm3,
    pct.product_category_name_english AS categoria,
    
    -- Características del Pago y Venta
    oi.price,
    oi.freight_value, -- El costo del flete suele ser un gran predictor de tiempo
    
    -- Geografía
    c.customer_state,
    
    -- Target de satisfacción (para modelos híbridos)
    r.review_score
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_products p ON oi.product_id = p.product_id
JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered';

-- Diversidad de Categorías y Precios
SELECT 
    pct.product_category_name_english AS categoria,
    COUNT(oi.product_id) AS cantidad_vendida,
    ROUND(AVG(oi.price)::numeric, 2) AS precio_promedio,
    MIN(oi.price) AS precio_min,
    MAX(oi.price) AS precio_max
FROM olist_order_items oi
JOIN olist_products p ON oi.product_id = p.product_id
JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
GROUP BY 1
ORDER BY cantidad_vendida DESC;

-- Recomendación de productos
CREATE OR REPLACE VIEW v_recom_data AS
SELECT 
    c.customer_unique_id,
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    o.order_id,
    o.order_purchase_timestamp,
    oi.price,
    COALESCE(r.review_score, 0) AS review_score
FROM olist_customers c
JOIN olist_orders o ON c.customer_id = o.customer_id
JOIN olist_order_items oi ON o.order_id = oi.order_id
JOIN olist_products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id;