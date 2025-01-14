import pandas as pd
import sqlite3

path = 'app/data.csv'
data = pd.read_csv(path,sep=',')

data['quantity'] = pd.to_numeric(data['quantity'],errors='coerce') 
data['price'] = pd.to_numeric(data['price'],errors='coerce')
data['date'] = pd.to_datetime(data['date'], errors='coerce')
data = data.dropna(subset=['quantity', 'price'], how='all')
data['quantity'] = data['quantity'].fillna(0.0)
data['price'] = data.groupby('category')['price'].transform(lambda x: x.fillna(x.median()))

data['total_sales'] = data['quantity']*data['price']
data['day_of_week'] = data['date'].dt.day_name()
data['high_volume'] = data['quantity'] > 10

con = sqlite3.connect("test.db")
cur = con.cursor()

table_name = 'sales'
data.to_sql(table_name, con, if_exists='replace', index=False)

cur.execute("BEGIN TRANSACTION;")

cur.execute(f"DROP TABLE IF EXISTS average_product;")
cur.execute(f"DROP TABLE IF EXISTS total_sales;")
cur.execute(f"DROP TABLE IF EXISTS best_sales_day;")
cur.execute(f"DROP TABLE IF EXISTS outliers;")

cur.execute(f"""
CREATE TABLE average_product AS 
SELECT category, product, AVG(price) AS average_price, SUM(price) total_sales
FROM {table_name} 
GROUP BY category, product;
""")

cur.execute(f"""
CREATE TABLE total_sales AS 
SELECT category, SUM(price) AS total_sales 
FROM {table_name} 
GROUP BY category;
""")

cur.execute(f"""
CREATE TABLE IF NOT EXISTS average_price AS
SELECT
    category,
    AVG(price) AS average_price
FROM {table_name} 
GROUP BY category;
""")

cur.execute(f"""
CREATE TABLE best_sales_day AS 
WITH total_sales_by_day AS (
    SELECT category, date, SUM(total_sales) AS daily_sales
    FROM {table_name}
    GROUP BY category, date
)
SELECT ts.category, ts.date, ts.daily_sales
FROM total_sales_by_day ts
JOIN (
    SELECT category, MAX(daily_sales) AS max_sales
    FROM total_sales_by_day
    GROUP BY category
) max_sales_per_category
ON ts.category = max_sales_per_category.category
AND ts.daily_sales = max_sales_per_category.max_sales;
""")

cur.execute(f"""
CREATE TABLE outliers AS
WITH category_stats AS (
    SELECT category, AVG(quantity) AS mean_quantity, COUNT(quantity) AS count_quantity
    FROM {table_name}
    GROUP BY category
),
category_deviation AS (
    SELECT t.transaction_id, t.date, t.category, t.product, t.quantity, t.price,
           t.total_sales, t.day_of_week, t.high_volume, cs.mean_quantity,
           cs.count_quantity, (t.quantity - cs.mean_quantity) AS quantity_diff
    FROM {table_name} t
    JOIN category_stats cs ON t.category = cs.category
)
SELECT transaction_id, date, category, product, quantity, price, total_sales,
       day_of_week, high_volume, mean_quantity, count_quantity, quantity_diff,
       SQRT(SUM(quantity_diff * quantity_diff) / count_quantity) AS std_quantity
FROM category_deviation
GROUP BY category, product
HAVING ABS(quantity_diff) > (2 * std_quantity);
""")

cur.execute(f"ALTER TABLE {table_name} ADD COLUMN outliers BOOLEAN;")

cur.execute(f"""
UPDATE {table_name}
SET outliers = 1
WHERE transaction_id IN (SELECT transaction_id FROM outliers);
""")

cur.execute(f"""
UPDATE {table_name}
SET outliers = 0
WHERE outliers IS NULL;
""")

con.commit()

tables_query = "SELECT * FROM best_sales_day;"
average = pd.read_sql(tables_query, con)

con.close()
print("sale per product")
print(average)