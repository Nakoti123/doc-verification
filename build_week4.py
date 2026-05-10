import json

cells = []

def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s}

def code(s):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": s}

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""<div style="background:linear-gradient(135deg,#0D1B2A 0%,#1565C0 50%,#00838F 100%);padding:60px 45px 50px;border-radius:20px;text-align:center;font-family:'Segoe UI',sans-serif;">
  <p style="color:#B2EBF2;font-size:1em;margin:0 0 8px;letter-spacing:3px;">COMPLETE DATA ANALYTICS COURSE</p>
  <h1 style="font-size:3em;margin:0 0 10px;color:#ffffff;font-weight:700;">Week 4</h1>
  <h2 style="font-size:2em;margin:0 0 18px;color:#FFD54F;font-weight:600;">SQL & Database Analytics</h2>
  <p style="color:#90CAF9;font-size:1.1em;font-style:italic;margin:0 0 28px;">From Zero SQL Knowledge to Writing Production-Grade Queries</p>
  <div style="display:flex;justify-content:center;gap:20px;flex-wrap:wrap;">
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 22px;"><div style="font-size:2em;font-weight:700;color:#fff;">5</div><div style="color:#B2EBF2;">Days</div></div>
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 22px;"><div style="font-size:2em;font-weight:700;color:#fff;">50+</div><div style="color:#B2EBF2;">SQL Queries</div></div>
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 22px;"><div style="font-size:2em;font-weight:700;color:#fff;">1</div><div style="color:#B2EBF2;">Full DB</div></div>
    <div style="background:rgba(255,255,255,0.12);border-radius:10px;padding:14px 22px;"><div style="font-size:2em;font-weight:700;color:#fff;">100%</div><div style="color:#B2EBF2;">Hands-On</div></div>
  </div>
</div>"""
))

cells.append(md(
"""---
## Week 4 Learning Map

| Day | Topic | Key Concepts | Tools |
|-----|-------|-------------|-------|
| **Day 16** | SQL Foundations | SELECT, WHERE, GROUP BY, HAVING, ORDER BY, Aggregate Functions | SQLite / PostgreSQL |
| **Day 17** | Advanced SQL | All JOINs, Subqueries, CTEs, CASE WHEN, COALESCE, String/Date Functions | PostgreSQL |
| **Day 18** | Window Functions | ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, FIRST_VALUE, NTILE, PARTITION BY | PostgreSQL |
| **Day 19** | Query Optimisation | EXPLAIN ANALYZE, Indexes, Partitioning, Query Planning, Best Practices | PostgreSQL + pgAdmin |
| **Day 20** | NoSQL / MongoDB | CRUD, Aggregation Pipeline, Atlas, PyMongo, SQL vs NoSQL comparison | MongoDB + PyMongo |

---

## Setup Note
This notebook uses **SQLite** (built into Python — zero installation) and **PyMongo simulation** for MongoDB.
Every concept maps 1-to-1 to PostgreSQL / MySQL / MongoDB in real environments.

```python
import sqlite3
conn   = sqlite3.connect(':memory:')   # in-memory DB — fast, no file needed
cursor = conn.cursor()
```

> All queries, patterns and syntax you learn here work identically on PostgreSQL, MySQL, BigQuery and Snowflake with only minor dialect differences noted inline.
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE SETUP — shared across all days
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
## Database Setup — Run This First!
We create one realistic **E-Commerce Analytics Database** used across all 5 days.

### Schema Overview
```
CUSTOMERS ──< ORDERS ──< ORDER_ITEMS >── PRODUCTS
                              │
                         CATEGORIES
                         EMPLOYEES
                         REVIEWS
```
"""
))

cells.append(code(
"""import sqlite3, pandas as pd, warnings
warnings.filterwarnings('ignore')

conn   = sqlite3.connect(':memory:')
cur    = conn.cursor()

def Q(query, params=None):
    \"\"\"Run a SELECT query and return a pandas DataFrame.\"\"\"
    return pd.read_sql_query(query, conn, params=params)

def X(sql_script):
    \"\"\"Execute one or more SQL statements (DDL/DML).\"\"\"
    cur.executescript(sql_script)
    conn.commit()

# ── DDL: Create all tables ────────────────────────────────────────────────────
X('''
CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    parent_name   TEXT,
    commission_pct REAL   DEFAULT 5.0
);

CREATE TABLE customers (
    customer_id   TEXT    PRIMARY KEY,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE,
    phone         TEXT,
    city          TEXT,
    state         TEXT,
    pincode       TEXT,
    age           INTEGER CHECK(age > 0 AND age < 120),
    gender        TEXT    CHECK(gender IN ('M','F','Other')),
    joined_date   TEXT    NOT NULL,
    tier          TEXT    DEFAULT 'Regular'   CHECK(tier IN ('Regular','Silver','Gold','Platinum')),
    is_active     INTEGER DEFAULT 1
);

CREATE TABLE employees (
    emp_id        TEXT    PRIMARY KEY,
    name          TEXT    NOT NULL,
    department    TEXT,
    role          TEXT,
    manager_id    TEXT    REFERENCES employees(emp_id),
    city          TEXT,
    salary        REAL    CHECK(salary >= 0),
    hire_date     TEXT,
    is_active     INTEGER DEFAULT 1
);

CREATE TABLE products (
    product_id    TEXT    PRIMARY KEY,
    name          TEXT    NOT NULL,
    category_id   INTEGER REFERENCES categories(category_id),
    brand         TEXT,
    price         REAL    NOT NULL CHECK(price > 0),
    cost_price    REAL    CHECK(cost_price > 0),
    stock         INTEGER DEFAULT 0,
    rating        REAL    DEFAULT 0.0 CHECK(rating BETWEEN 0 AND 5),
    is_active     INTEGER DEFAULT 1
);

CREATE TABLE orders (
    order_id      TEXT    PRIMARY KEY,
    customer_id   TEXT    REFERENCES customers(customer_id),
    emp_id        TEXT    REFERENCES employees(emp_id),
    order_date    TEXT    NOT NULL,
    delivery_date TEXT,
    status        TEXT    DEFAULT 'Processing'
                          CHECK(status IN ('Processing','Shipped','Delivered','Cancelled','Returned')),
    payment       TEXT,
    city          TEXT
);

CREATE TABLE order_items (
    item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      TEXT    REFERENCES orders(order_id),
    product_id    TEXT    REFERENCES products(product_id),
    qty           INTEGER NOT NULL CHECK(qty > 0),
    unit_price    REAL    NOT NULL,
    discount_pct  REAL    DEFAULT 0
);

CREATE TABLE reviews (
    review_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id    TEXT    REFERENCES products(product_id),
    customer_id   TEXT    REFERENCES customers(customer_id),
    rating        INTEGER CHECK(rating BETWEEN 1 AND 5),
    review_text   TEXT,
    review_date   TEXT
);
''')

# ── DML: Insert data ──────────────────────────────────────────────────────────
cur.executemany("INSERT INTO categories(name,parent_name,commission_pct) VALUES(?,?,?)",[
    ('Electronics',None,8.0),('Mobiles','Electronics',6.0),
    ('Laptops','Electronics',5.0),('Accessories','Electronics',10.0),
    ('Furniture',None,7.0),('Books',None,4.0),
    ('Sports',None,6.0),('Beauty',None,9.0),('Fashion',None,8.0),
])

cur.executemany("INSERT INTO customers VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",[
    ('C001','Rahul Sharma','rahul@email.com','9876543210','Mumbai','Maharashtra','400001',28,'M','2021-03-15','Gold',1),
    ('C002','Priya Mehta','priya@email.com','8765432109','Delhi','Delhi','110001',31,'F','2019-06-01','Platinum',1),
    ('C003','Amit Kumar','amit@email.com','7654321098','Bengaluru','Karnataka','560001',26,'M','2020-09-10','Regular',1),
    ('C004','Sneha Joshi','sneha@email.com','6543210987','Chennai','Tamil Nadu','600001',34,'F','2022-01-20','Gold',1),
    ('C005','Karan Singh','karan@email.com','9543210876','Mumbai','Maharashtra','400002',29,'M','2017-11-05','Platinum',1),
    ('C006','Divya Nair','divya@email.com','8432109875','Delhi','Delhi','110002',38,'F','2019-04-22','Regular',1),
    ('C007','Ravi Verma','ravi@email.com','7321098764','Bengaluru','Karnataka','560002',24,'M','2021-07-30','Silver',1),
    ('C008','Meera Patel','meera@email.com','9210987653','Chennai','Tamil Nadu','600002',42,'F','2023-02-14','Gold',1),
    ('C009','Arjun Gupta','arjun@email.com','8109876542','Hyderabad','Telangana','500001',35,'M','2020-08-09','Platinum',1),
    ('C010','Anita Roy','anita@email.com','9098765431','Kolkata','West Bengal','700001',27,'F','2022-05-18','Regular',1),
    ('C011','Vikram Bose','vikram@email.com','7987654320','Mumbai','Maharashtra','400003',45,'M','2018-12-01','Platinum',1),
    ('C012','Pooja Sharma','pooja@email.com','8876543219','Delhi','Delhi','110003',22,'F','2023-09-10','Regular',1),
    ('C013','Nikhil Rao','nikhil@email.com','9765432108','Hyderabad','Telangana','500002',33,'M','2020-03-25','Silver',1),
    ('C014','Shruti Das','shruti@email.com','7654320987','Kolkata','West Bengal','700002',29,'F','2021-11-11','Gold',1),
    ('C015','Manish Tiwari','manish@email.com','8543219876','Pune','Maharashtra','411001',40,'M','2019-07-08','Regular',0),
])

cur.executemany("INSERT INTO employees VALUES(?,?,?,?,?,?,?,?,?)",[
    ('E001','Nandita Iyer','Sales','Manager',None,'Mumbai',120000,'2018-01-15',1),
    ('E002','Sanjay Mehta','Sales','Executive','E001','Delhi',65000,'2020-03-10',1),
    ('E003','Divya Pillai','Sales','Executive','E001','Bengaluru',68000,'2019-08-20',1),
    ('E004','Rohit Sharma','Tech','Manager',None,'Mumbai',150000,'2017-06-01',1),
    ('E005','Kavitha Nair','Tech','Developer','E004','Chennai',95000,'2021-02-15',1),
    ('E006','Arun Verma','Tech','Developer','E004','Hyderabad',92000,'2020-11-01',1),
    ('E007','Preethi Kumar','Finance','Manager',None,'Delhi',130000,'2016-09-10',1),
    ('E008','Harish Babu','Finance','Analyst','E007','Mumbai',75000,'2022-04-01',1),
    ('E009','Sunita Sharma','HR','Manager',None,'Delhi',110000,'2018-07-20',1),
    ('E010','Deepak Roy','Sales','Executive','E001','Kolkata',62000,'2023-01-05',1),
])

cur.executemany("INSERT INTO products(product_id,name,category_id,brand,price,cost_price,stock,rating) VALUES(?,?,?,?,?,?,?,?)",[
    ('P001','Laptop Pro 15',3,'TechMaster',85000,60000,50,4.5),
    ('P002','Wireless Mouse',4,'ClickPro',1299,600,350,4.2),
    ('P003','Office Chair',5,'ComfortSit',12500,7000,30,4.0),
    ('P004','Python for Data Analytics',6,'TechPress',599,200,500,4.8),
    ('P005','Standing Desk',5,'ErgoDesk',25000,15000,20,4.3),
    ('P006','USB-C Hub 7-in-1',4,'ConnectPro',2499,900,200,4.1),
    ('P007','Noise Cancelling Headphones',1,'SoundMax',8999,4000,80,4.6),
    ('P008','Premium Yoga Mat',7,'FlexFit',1499,500,150,4.4),
    ('P009','Stainless Water Bottle',7,'HydroMax',599,150,400,4.2),
    ('P010','Vitamin C Face Serum',8,'GlowUp',2999,800,120,4.7),
    ('P011','Running Shoes Pro',7,'SpeedRun',4999,2000,60,4.3),
    ('P012','LED Desk Lamp',5,'BrightWork',1799,700,90,4.0),
    ('P013','Samsung Galaxy S24',2,'Samsung',79999,58000,40,4.6),
    ('P014','AirPods Pro Max',4,'Apple',59999,42000,25,4.8),
    ('P015','Cotton Casual Shirt',9,'FashionHub',1299,400,200,3.9),
])

cur.executemany("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)",[
    ('ORD001','C001','E002','2024-01-05','2024-01-08','Delivered','UPI','Mumbai'),
    ('ORD002','C002','E003','2024-01-07','2024-01-10','Delivered','Credit Card','Delhi'),
    ('ORD003','C003','E002','2024-01-08','2024-01-11','Delivered','Debit Card','Bengaluru'),
    ('ORD004','C004','E003','2024-01-10',None,'Processing','EMI','Chennai'),
    ('ORD005','C005','E010','2024-01-12','2024-01-15','Delivered','Credit Card','Mumbai'),
    ('ORD006','C001','E002','2024-01-15','2024-01-18','Delivered','UPI','Mumbai'),
    ('ORD007','C006','E003','2024-01-18',None,'Cancelled','Debit Card','Delhi'),
    ('ORD008','C002','E002','2024-01-20','2024-01-24','Delivered','Credit Card','Delhi'),
    ('ORD009','C007','E010','2024-01-22','2024-01-26','Delivered','UPI','Bengaluru'),
    ('ORD010','C009','E003','2024-01-25','2024-01-29','Delivered','Net Banking','Hyderabad'),
    ('ORD011','C010','E002','2024-01-28','2024-02-01','Returned','UPI','Kolkata'),
    ('ORD012','C008','E003','2024-02-02','2024-02-05','Delivered','Credit Card','Chennai'),
    ('ORD013','C005','E010','2024-02-05','2024-02-08','Delivered','EMI','Mumbai'),
    ('ORD014','C003','E002','2024-02-08',None,'Processing','UPI','Bengaluru'),
    ('ORD015','C011','E003','2024-02-10','2024-02-13','Delivered','Credit Card','Mumbai'),
    ('ORD016','C012','E002','2024-02-14','2024-02-17','Delivered','UPI','Delhi'),
    ('ORD017','C001','E010','2024-02-18','2024-02-21','Delivered','UPI','Mumbai'),
    ('ORD018','C009','E003','2024-02-22','2024-02-25','Delivered','Net Banking','Hyderabad'),
    ('ORD019','C004','E002','2024-02-25',None,'Shipped','EMI','Chennai'),
    ('ORD020','C002','E003','2024-03-01','2024-03-04','Delivered','Credit Card','Delhi'),
    ('ORD021','C013','E010','2024-03-05','2024-03-08','Delivered','UPI','Hyderabad'),
    ('ORD022','C014','E002','2024-03-08','2024-03-11','Delivered','Debit Card','Kolkata'),
    ('ORD023','C007','E003','2024-03-10',None,'Cancelled','Credit Card','Bengaluru'),
    ('ORD024','C011','E010','2024-03-15','2024-03-18','Delivered','Net Banking','Mumbai'),
    ('ORD025','C015','E002','2024-03-20',None,'Processing','UPI','Pune'),
])

cur.executemany("INSERT INTO order_items(order_id,product_id,qty,unit_price,discount_pct) VALUES(?,?,?,?,?)",[
    ('ORD001','P001',1,85000,0),('ORD001','P002',1,1299,0),
    ('ORD002','P003',1,12500,0),('ORD002','P002',1,1299,0),
    ('ORD003','P004',2,599,10),('ORD003','P009',1,599,0),
    ('ORD004','P005',1,25000,5),('ORD004','P006',1,2499,0),
    ('ORD005','P001',1,85000,0),('ORD005','P007',1,8999,5),
    ('ORD006','P008',2,1499,0),('ORD006','P009',2,599,0),
    ('ORD007','P007',1,8999,0),('ORD007','P002',1,1299,20),
    ('ORD008','P001',1,85000,0),('ORD008','P006',1,2499,5),
    ('ORD009','P004',2,599,0),('ORD009','P009',3,599,10),
    ('ORD010','P005',1,25000,0),('ORD010','P012',1,1799,0),
    ('ORD011','P009',1,599,0),('ORD011','P004',1,599,0),
    ('ORD012','P003',1,12500,0),('ORD012','P012',1,1799,0),
    ('ORD013','P001',1,85000,5),('ORD013','P007',1,8999,0),
    ('ORD014','P010',1,2999,0),('ORD014','P004',1,599,0),
    ('ORD015','P005',1,25000,0),('ORD015','P006',1,2499,0),
    ('ORD016','P008',2,1499,0),('ORD016','P009',2,599,0),
    ('ORD017','P003',1,12500,0),
    ('ORD018','P007',1,8999,5),('ORD018','P006',1,2499,0),
    ('ORD019','P007',1,8999,0),
    ('ORD020','P001',1,85000,0),('ORD020','P002',2,1299,0),
    ('ORD021','P013',1,79999,3),
    ('ORD022','P010',2,2999,0),('ORD022','P008',1,1499,0),
    ('ORD023','P014',1,59999,0),
    ('ORD024','P013',1,79999,5),('ORD024','P002',1,1299,0),
    ('ORD025','P015',3,1299,0),
])

cur.executemany("INSERT INTO reviews(product_id,customer_id,rating,review_text,review_date) VALUES(?,?,?,?,?)",[
    ('P001','C001',5,'Excellent laptop, worth every rupee!','2024-01-10'),
    ('P001','C005',4,'Good performance, battery could be better','2024-01-16'),
    ('P001','C002',5,'Best laptop I have ever used','2024-01-25'),
    ('P002','C001',4,'Works well, comfortable grip','2024-01-09'),
    ('P003','C002',4,'Very comfortable, easy assembly','2024-01-12'),
    ('P004','C003',5,'Best Python book for beginners!','2024-01-12'),
    ('P007','C005',5,'Amazing sound quality, worth it','2024-01-16'),
    ('P007','C009',4,'Great headphones, slightly heavy','2024-01-30'),
    ('P010','C004',5,'Skin feels amazing after 2 weeks','2024-02-03'),
    ('P013','C009',5,'Best Android phone right now','2024-03-09'),
])
conn.commit()

print("=" * 55)
print("  E-COMMERCE DATABASE READY")
print("=" * 55)
for tbl in ['categories','customers','employees','products','orders','order_items','reviews']:
    n = Q(f"SELECT COUNT(*) AS n FROM {tbl}").iloc[0,0]
    print(f"  {tbl:<15} {n:>4} rows")
print("=" * 55)
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DAY 16 — SQL FOUNDATIONS
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(90deg,#1565C0,#0D47A1);padding:22px 32px;border-radius:12px;color:white;">
<h1 style="margin:0;font-size:2em;">Day 16 — SQL Foundations</h1>
<p style="margin:6px 0 0;color:#BBDEFB;font-size:1.1em;">SELECT · WHERE · ORDER BY · GROUP BY · HAVING · Aggregate Functions</p>
</div>
"""
))

cells.append(md(
"""## Why SQL is Non-Negotiable for Every Data Analyst

**SQL (Structured Query Language)** is the universal language of databases, invented at IBM in 1974 and still the number-one skill listed in data analyst job descriptions worldwide.

### Key Terminology Defined

| Term | Definition |
|------|-----------|
| **Database** | An organised collection of structured data managed by a DBMS |
| **Table** | A grid of data with rows and columns — like one Excel sheet |
| **Row / Record** | One complete data entry — e.g. one customer, one order |
| **Column / Field** | A property shared by every row — e.g. `name`, `price`, `date` |
| **Primary Key (PK)** | A column that uniquely identifies every row — no duplicates, no NULLs |
| **Foreign Key (FK)** | A column that points to another table's Primary Key — creates the relationship |
| **NULL** | A special marker meaning "no value known" — NOT zero, NOT empty string |
| **Schema** | The blueprint of a database — defines tables, columns, data types, and constraints |
| **Query** | A SQL statement that retrieves or manipulates data |
| **DDL** | Data Definition Language — `CREATE`, `ALTER`, `DROP` — define structure |
| **DML** | Data Manipulation Language — `INSERT`, `UPDATE`, `DELETE` — change data |
| **DQL** | Data Query Language — `SELECT` — read data |

### SQL Clause Execution Order

SQL is written in one order but executed in a different order. Understanding this prevents bugs:

```
WRITING ORDER:     SELECT  →  FROM  →  WHERE  →  GROUP BY  →  HAVING  →  ORDER BY  →  LIMIT
EXECUTION ORDER:   FROM    →  WHERE →  GROUP BY  →  HAVING  →  SELECT  →  ORDER BY  →  LIMIT
```

**Practical consequence:** You cannot use a SELECT alias inside WHERE (WHERE runs before SELECT).
"""
))

cells.append(code(
"""# All queries in Day 16 use the conn and Q() function defined in the setup cell above.
# Make sure you run the setup cell first!

print("=== SELECT — Retrieve specific columns ===")
print("Definition: SELECT specifies WHICH columns to include in the result.")
print("Always name your columns explicitly — avoid SELECT * in production code.")
print()
print(Q("""
    SELECT
        customer_id,
        name,
        city,
        tier,
        age
    FROM customers
    LIMIT 6
"""))

print()
print("=== DISTINCT — Remove duplicate values ===")
print("Definition: DISTINCT eliminates duplicate rows from the result set.")
print("Each unique combination of the selected columns appears only once.")
print()
print("Unique cities we serve:")
print(Q("SELECT DISTINCT city, state FROM customers ORDER BY state, city"))
"""
))

cells.append(code(
"""print("=== Column Aliases with AS ===")
print("Definition: AS assigns a temporary display name to a column or expression.")
print("The alias exists only in the output — it does not rename the actual table column.")
print()
print(Q("""
    SELECT
        name                                        AS product_name,
        price                                       AS selling_price,
        cost_price                                  AS cost,
        ROUND(price - cost_price, 0)                AS gross_profit,
        ROUND((price - cost_price) / price * 100, 1) AS margin_pct,
        stock                                       AS units_in_stock
    FROM products
    ORDER BY margin_pct DESC
"""))
"""
))

cells.append(code(
"""print("=== WHERE — Filter rows by condition ===")
print("Definition: WHERE keeps only rows where the condition evaluates to TRUE.")
print("NULL values are NOT equal to anything — use IS NULL / IS NOT NULL for them.")
print()

print("--- Comparison operators ---")
print("Electronics products under ₹10,000:")
print(Q("""
    SELECT name, price, stock
    FROM   products p
    JOIN   categories c ON p.category_id = c.category_id
    WHERE  c.name = 'Electronics'
      AND  price < 10000
    ORDER  BY price
"""))

print()
print("--- BETWEEN (inclusive on both ends) ---")
print("Definition: BETWEEN a AND b is equivalent to >= a AND <= b.")
print("Products priced between ₹1,000 and ₹15,000:")
print(Q("""
    SELECT name, price, brand
    FROM   products
    WHERE  price BETWEEN 1000 AND 15000
    ORDER  BY price
"""))

print()
print("--- IN — match any value in a list ---")
print("Definition: IN checks whether the column value is present in the provided list.")
print("Customers from major metros:")
print(Q("""
    SELECT name, city, tier
    FROM   customers
    WHERE  city IN ('Mumbai', 'Delhi', 'Bengaluru')
    ORDER  BY city
"""))

print()
print("--- LIKE — pattern matching ---")
print("% = any number of characters (including zero).")
print("_ = exactly one character.")
print("Customers whose name starts with 'R' or ends with 'ma':")
print(Q("""
    SELECT name, city
    FROM   customers
    WHERE  name LIKE 'R%'
       OR  name LIKE '%ma'
"""))

print()
print("--- IS NULL / IS NOT NULL ---")
print("Definition: NULL means the value is unknown or missing.")
print("Orders with no delivery date yet (not yet delivered):")
print(Q("""
    SELECT order_id, customer_id, order_date, status
    FROM   orders
    WHERE  delivery_date IS NULL
    ORDER  BY order_date
"""))
"""
))

cells.append(code(
"""print("=== Aggregate Functions — Definitions ===")
print()
print("COUNT(*)             → Count ALL rows, including NULLs")
print("COUNT(column)        → Count non-NULL values in that column")
print("COUNT(DISTINCT col)  → Count unique non-NULL values")
print("SUM(column)          → Total of all non-NULL values")
print("AVG(column)          → Mean of all non-NULL values (NULLs excluded from denominator!)")
print("MIN(column)          → Smallest value (works on text alphabetically)")
print("MAX(column)          → Largest value")
print()

print("=== Overall Business Metrics (no grouping) ===")
print(Q("""
    SELECT
        COUNT(*)                             AS total_orders,
        COUNT(DISTINCT customer_id)          AS unique_customers,
        ROUND(SUM(total_amount), 0)          AS gross_revenue,
        ROUND(AVG(total_amount), 0)          AS avg_order_value,
        MIN(order_date)                      AS first_order,
        MAX(order_date)                      AS latest_order
    FROM orders
    WHERE status NOT IN ('Cancelled', 'Returned')
"""))
"""
))

cells.append(code(
"""print("=== GROUP BY — Aggregate per group ===")
print("Definition: GROUP BY collapses rows with the same value into one summary row.")
print("RULE: Every column in SELECT must either be in GROUP BY or wrapped in an aggregate function.")
print()

print("--- Revenue and order count by order status ---")
print(Q("""
    SELECT
        status,
        COUNT(*)                      AS order_count,
        ROUND(SUM(total_amount), 0)   AS total_revenue,
        ROUND(AVG(total_amount), 0)   AS avg_order_value,
        MIN(total_amount)             AS smallest_order,
        MAX(total_amount)             AS largest_order
    FROM orders
    GROUP BY status
    ORDER BY total_revenue DESC
"""))

print()
print("--- GROUP BY multiple columns: city × payment method ---")
print(Q("""
    SELECT
        city,
        payment,
        COUNT(*)                     AS orders,
        ROUND(SUM(total_amount), 0)  AS revenue
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY city, payment
    ORDER BY city, revenue DESC
"""))

print()
print("=== HAVING — Filter groups (not individual rows) ===")
print("Definition: HAVING filters groups AFTER GROUP BY has run.")
print("Key difference: WHERE filters rows (before grouping), HAVING filters groups (after grouping).")
print("Only HAVING can use aggregate functions like SUM(), COUNT(), AVG().")
print()
print("Cities with more than 2 delivered orders:")
print(Q("""
    SELECT
        city,
        COUNT(*)                     AS delivered_orders,
        ROUND(SUM(total_amount), 0)  AS revenue
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY city
    HAVING COUNT(*) > 2
    ORDER BY revenue DESC
"""))
"""
))

cells.append(code(
"""print("=== ORDER BY — Sort results ===")
print("Definition: ORDER BY sorts the result set.")
print("ASC  = ascending  (smallest first, A→Z) — this is the DEFAULT.")
print("DESC = descending (largest first, Z→A) — must be written explicitly.")
print()

print("Top 10 most expensive products:")
print(Q("""
    SELECT name, brand, price, stock
    FROM   products
    ORDER  BY price DESC
    LIMIT  10
"""))

print()
print("=== LIMIT + OFFSET — Pagination ===")
print("LIMIT n   = return only n rows.")
print("OFFSET k  = skip the first k rows.")
print("Together they enable page-by-page navigation through large result sets.")
print()
print("Page 2 of products (5 per page):")
print(Q("""
    SELECT name, price
    FROM   products
    ORDER  BY price DESC
    LIMIT  5
    OFFSET 5
"""))

print()
print("=== Real-World Exercise: Full Product Profitability Report ===")
print(Q("""
    SELECT
        c.name                                          AS category,
        COUNT(p.product_id)                             AS products,
        ROUND(AVG(p.price), 0)                          AS avg_price,
        ROUND(AVG(p.cost_price), 0)                     AS avg_cost,
        ROUND(AVG(p.price - p.cost_price), 0)           AS avg_profit,
        ROUND(AVG((p.price-p.cost_price)/p.price*100), 1) AS avg_margin_pct,
        SUM(p.stock)                                    AS total_stock,
        ROUND(AVG(p.rating), 2)                         AS avg_rating
    FROM     products  p
    JOIN     categories c ON p.category_id = c.category_id
    GROUP BY c.name
    ORDER BY avg_margin_pct DESC
"""))
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DAY 17 — ADVANCED SQL
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(90deg,#4A148C,#6A1B9A);padding:22px 32px;border-radius:12px;color:white;">
<h1 style="margin:0;font-size:2em;">Day 17 — Advanced SQL</h1>
<p style="margin:6px 0 0;color:#E1BEE7;font-size:1.1em;">JOINs · Subqueries · CTEs · CASE WHEN · COALESCE · String & Date Functions</p>
</div>
"""
))

cells.append(md(
"""## JOIN Types — Complete Reference

### What is a JOIN?
A JOIN combines rows from two or more tables based on a related column between them. Real-world data is split across multiple tables — JOINs bring it back together.

### JOIN Type Definitions

| JOIN Type | Definition | Use Case |
|-----------|-----------|---------|
| `INNER JOIN` | Returns ONLY rows with a matching value in BOTH tables. Non-matching rows are excluded entirely. | The most common join — "show me orders WITH customers" |
| `LEFT JOIN` | Returns ALL rows from the LEFT table. Matching rows from the right table are included; non-matching right rows are NULL. | "Show me all customers, even those with no orders" |
| `RIGHT JOIN` | Returns ALL rows from the RIGHT table. Non-matching left rows are NULL. (Rarely used; rewrite as LEFT JOIN instead) | "Show me all products, even unsold ones" |
| `FULL OUTER JOIN` | Returns ALL rows from BOTH tables. NULLs fill where there is no match on either side. | Finding unmatched records on both sides |
| `CROSS JOIN` | Returns every possible combination of rows from both tables (Cartesian product). | Generating all size × colour combinations |
| `SELF JOIN` | Joins a table to itself using two aliases. | Employee–manager relationships, comparing rows within same table |

### JOIN Conditions — Key Terms

| Term | Definition |
|------|-----------|
| `ON clause` | The condition that links the two tables — usually matching a FK to a PK |
| `USING (col)` | Shorthand when both tables have the same column name |
| **Equi-join** | JOIN where condition uses `=` (most common type) |
| **Non-equi-join** | JOIN where condition uses `>`, `<`, `BETWEEN` etc. |
| **Table alias** | A short nickname for a table (e.g. `orders o`) — essential when joining a table to itself |
"""
))

cells.append(code(
"""print("=== INNER JOIN — only matching rows ===")
print("Rows that exist in BOTH tables are returned. Non-matching rows are dropped.")
print()
print(Q("""
    SELECT
        o.order_id,
        c.name           AS customer_name,
        c.city,
        c.tier,
        o.order_date,
        o.status,
        o.total_amount
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Delivered'
    ORDER BY o.total_amount DESC
    LIMIT 8
"""))
"""
))

cells.append(code(
"""print("=== LEFT JOIN — all rows from left table ===")
print("Every row from the left table appears. Right table columns are NULL when no match exists.")
print()
print("All customers, even those who have never ordered:")
print(Q("""
    SELECT
        c.customer_id,
        c.name,
        c.city,
        c.tier,
        COUNT(o.order_id)               AS total_orders,
        ROUND(COALESCE(SUM(o.total_amount), 0), 0) AS lifetime_value
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.city, c.tier
    ORDER BY lifetime_value DESC
"""))
"""
))

cells.append(code(
"""print("=== Three-Table JOIN — Orders + Customers + Employees ===")
print("Chain multiple JOINs to bring together all the data you need in one query.")
print()
print(Q("""
    SELECT
        o.order_id,
        c.name          AS customer,
        c.tier,
        e.name          AS handled_by,
        e.department,
        o.order_date,
        o.status,
        o.payment,
        ROUND(o.total_amount, 0) AS amount
    FROM   orders    o
    JOIN   customers c ON o.customer_id = c.customer_id
    JOIN   employees e ON o.emp_id      = e.emp_id
    WHERE  o.status = 'Delivered'
    ORDER  BY o.total_amount DESC
    LIMIT  10
"""))
"""
))

cells.append(code(
"""print("=== SELF JOIN — Employee hierarchy (Manager → Reports) ===")
print("Definition: Join a table to itself using two different aliases.")
print("Classic use case: org chart where manager_id references emp_id in the same table.")
print()
print(Q("""
    SELECT
        e.emp_id,
        e.name       AS employee,
        e.role,
        e.department,
        e.salary,
        m.name       AS manager,
        m.role       AS manager_role
    FROM employees e
    LEFT JOIN employees m ON e.manager_id = m.emp_id
    ORDER BY e.department, e.salary DESC
"""))
"""
))

cells.append(md(
"""## Subqueries — Definition and Types

A **subquery** (also called a nested query or inner query) is a SELECT statement written inside another SQL statement. The outer query uses the result of the inner query.

### Types of Subqueries

| Type | Definition | Returns | Example |
|------|-----------|---------|---------|
| **Scalar subquery** | Returns exactly ONE row and ONE column | A single value | `WHERE price > (SELECT AVG(price) FROM products)` |
| **Row subquery** | Returns ONE row with multiple columns | One row | `WHERE (city, tier) = (SELECT city, tier FROM ...)` |
| **Table subquery** | Returns multiple rows and columns — used in FROM clause | A virtual table | `FROM (SELECT ...) AS alias` |
| **Correlated subquery** | References a column from the OUTER query — runs once per outer row | Varies | `WHERE qty > (SELECT AVG(qty) FROM ... WHERE order_id = o.order_id)` |

### Subquery Operators

| Operator | Definition |
|----------|-----------|
| `IN (subquery)` | True if the value exists in the subquery's result set |
| `NOT IN (subquery)` | True if the value does NOT exist in the result set |
| `EXISTS (subquery)` | True if the subquery returns at least one row |
| `NOT EXISTS (subquery)` | True if the subquery returns zero rows |
| `= (subquery)` | True if the value equals the single value returned |
| `> ALL (subquery)` | True if the value is greater than every value in the list |
| `> ANY (subquery)` | True if the value is greater than at least one value in the list |
"""
))

cells.append(code(
"""print("=== Scalar Subquery — Single value comparison ===")
print("Products priced above the overall average price:")
print(Q("""
    SELECT
        name,
        price,
        ROUND(price - (SELECT AVG(price) FROM products), 0) AS above_avg_by
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC
"""))

print()
print("=== IN Subquery — customers who placed at least one delivered order ===")
print(Q("""
    SELECT customer_id, name, city, tier
    FROM   customers
    WHERE  customer_id IN (
        SELECT DISTINCT customer_id
        FROM   orders
        WHERE  status = 'Delivered'
    )
    ORDER BY tier, name
"""))

print()
print("=== NOT IN Subquery — customers who have NEVER ordered ===")
print(Q("""
    SELECT customer_id, name, city, tier, joined_date
    FROM   customers
    WHERE  customer_id NOT IN (
        SELECT DISTINCT customer_id FROM orders
    )
"""))

print()
print("=== Table Subquery in FROM clause — top spending customers ===")
print(Q("""
    SELECT
        sub.customer_id,
        c.name,
        c.tier,
        sub.order_count,
        sub.total_spent,
        sub.avg_order
    FROM (
        SELECT
            customer_id,
            COUNT(*)                     AS order_count,
            ROUND(SUM(total_amount), 0)  AS total_spent,
            ROUND(AVG(total_amount), 0)  AS avg_order
        FROM orders
        WHERE status NOT IN ('Cancelled', 'Returned')
        GROUP BY customer_id
    ) AS sub
    JOIN customers c ON sub.customer_id = c.customer_id
    ORDER BY total_spent DESC
"""))
"""
))

cells.append(md(
"""## CTEs — Common Table Expressions

### What is a CTE?
A **CTE (Common Table Expression)** is a named, temporary result set defined at the top of a query using the `WITH` keyword. It exists only for the duration of the query.

### CTE Definition and Syntax

```sql
WITH cte_name AS (
    SELECT ...        -- This is the CTE definition
),
another_cte AS (
    SELECT ... FROM cte_name ...   -- CTEs can reference each other
)
SELECT * FROM another_cte;         -- The main query uses the CTEs
```

### CTE vs Subquery — Key Differences

| Aspect | Subquery | CTE |
|--------|---------|-----|
| **Readability** | Can become deeply nested and hard to read | Named and structured — much easier to read |
| **Reuse** | Cannot be referenced more than once in the same query | Can be referenced multiple times |
| **Recursion** | Not supported | Supports recursive queries |
| **Debugging** | Hard to isolate and test | Run the CTE independently to debug |
| **Performance** | Usually the same | Usually the same (query planner optimises both) |

### When to Use CTEs
- Breaking complex queries into readable steps
- Reusing the same intermediate result multiple times
- Recursive queries (org charts, bill of materials)
- Making your code reviewable and maintainable
"""
))

cells.append(code(
"""print("=== CTE — Step-by-step revenue analysis ===")
print(Q("""
    WITH order_revenue AS (
        -- Step 1: Calculate net revenue per order item
        SELECT
            oi.order_id,
            oi.product_id,
            oi.qty,
            oi.unit_price,
            oi.discount_pct,
            ROUND(oi.qty * oi.unit_price * (1 - oi.discount_pct/100), 2) AS net_revenue
        FROM order_items oi
    ),
    product_summary AS (
        -- Step 2: Aggregate by product
        SELECT
            p.name               AS product_name,
            cat.name             AS category,
            COUNT(DISTINCT r.order_id)  AS orders,
            SUM(r.qty)           AS units_sold,
            ROUND(SUM(r.net_revenue), 0) AS total_revenue,
            ROUND(AVG(r.net_revenue), 0) AS avg_revenue_per_order
        FROM order_revenue r
        JOIN products   p   ON r.product_id    = p.product_id
        JOIN categories cat ON p.category_id   = cat.category_id
        GROUP BY p.product_id, p.name, cat.name
    )
    -- Step 3: Final query on the cleaned summary
    SELECT
        product_name,
        category,
        orders,
        units_sold,
        total_revenue,
        avg_revenue_per_order,
        ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 1) AS revenue_share_pct
    FROM product_summary
    ORDER BY total_revenue DESC
"""))
"""
))

cells.append(code(
"""print("=== CASE WHEN — Conditional logic inside SQL ===")
print("Definition: CASE WHEN is SQL's if-then-else. It evaluates conditions in order")
print("and returns the first THEN value whose WHEN condition is TRUE.")
print("ELSE handles all cases not matched above. Without ELSE, unmatched rows return NULL.")
print()

print("Customer segmentation using CASE WHEN:")
print(Q("""
    WITH customer_stats AS (
        SELECT
            c.customer_id,
            c.name,
            c.tier,
            COUNT(o.order_id)           AS order_count,
            ROUND(SUM(o.total_amount), 0) AS lifetime_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
                           AND o.status NOT IN ('Cancelled','Returned')
        GROUP BY c.customer_id, c.name, c.tier
    )
    SELECT
        customer_id,
        name,
        tier,
        order_count,
        lifetime_value,
        CASE
            WHEN lifetime_value >= 200000 THEN 'VIP Whale'
            WHEN lifetime_value >= 80000  THEN 'High Value'
            WHEN lifetime_value >= 20000  THEN 'Mid Value'
            WHEN lifetime_value >  0      THEN 'Low Value'
            ELSE 'Never Purchased'
        END AS segment,
        CASE
            WHEN order_count >= 5  THEN 'Loyal'
            WHEN order_count >= 2  THEN 'Returning'
            WHEN order_count  = 1  THEN 'New'
            ELSE 'Inactive'
        END AS purchase_behaviour
    FROM customer_stats
    ORDER BY lifetime_value DESC
"""))
"""
))

cells.append(code(
"""print("=== COALESCE — Handle NULL values gracefully ===")
print("Definition: COALESCE(a, b, c, ...) returns the FIRST non-NULL argument.")
print("It is the standard SQL way to provide default values when a column may be NULL.")
print()
print("COALESCE(delivery_date, 'Not yet delivered'):")
print(Q("""
    SELECT
        order_id,
        customer_id,
        order_date,
        COALESCE(delivery_date, 'Pending')    AS delivery_date,
        status,
        COALESCE(payment, 'Unknown')           AS payment_method,
        ROUND(total_amount, 0)                 AS amount
    FROM orders
    ORDER BY order_date
    LIMIT 10
"""))

print()
print("=== String Functions ===")
print("UPPER / LOWER / LENGTH / SUBSTR / REPLACE / TRIM / INSTR / PRINTF")
print(Q("""
    SELECT
        name                                AS original_name,
        UPPER(name)                         AS upper_name,
        LOWER(name)                         AS lower_name,
        LENGTH(name)                        AS name_length,
        SUBSTR(name, 1, INSTR(name,' ')-1) AS first_name,
        SUBSTR(name, INSTR(name,' ')+1)    AS last_name,
        REPLACE(email, '@email.com', '')    AS username,
        city || ', ' || state               AS location
    FROM customers
    LIMIT 8
"""))

print()
print("=== Date Functions ===")
print(Q("""
    SELECT
        order_id,
        order_date,
        delivery_date,
        SUBSTR(order_date, 1, 7)               AS order_month,
        SUBSTR(order_date, 1, 4)               AS order_year,
        CASE STRFTIME('%w', order_date)
            WHEN '0' THEN 'Sunday'
            WHEN '1' THEN 'Monday'
            WHEN '2' THEN 'Tuesday'
            WHEN '3' THEN 'Wednesday'
            WHEN '4' THEN 'Thursday'
            WHEN '5' THEN 'Friday'
            WHEN '6' THEN 'Saturday'
        END AS day_of_week,
        JULIANDAY(COALESCE(delivery_date, DATE('now'))) -
        JULIANDAY(order_date)                  AS days_to_deliver
    FROM orders
    WHERE delivery_date IS NOT NULL
    ORDER BY days_to_deliver DESC
    LIMIT 8
"""))
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DAY 18 — WINDOW FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(90deg,#1B5E20,#2E7D32);padding:22px 32px;border-radius:12px;color:white;">
<h1 style="margin:0;font-size:2em;">Day 18 — Window Functions</h1>
<p style="margin:6px 0 0;color:#C8E6C9;font-size:1.1em;">ROW_NUMBER · RANK · DENSE_RANK · LAG · LEAD · FIRST_VALUE · NTILE · PARTITION BY · OVER</p>
</div>
"""
))

cells.append(md(
"""## Window Functions — The Most Powerful SQL Feature for Analytics

### What is a Window Function?
A **window function** performs a calculation across a set of rows that are related to the current row — called a **window** — WITHOUT collapsing those rows into a single summary row (unlike GROUP BY).

```sql
function_name(column)  OVER (
    PARTITION BY group_column    -- divide rows into groups (optional)
    ORDER BY sort_column         -- order rows within each group
    ROWS BETWEEN ...             -- define the window frame (optional)
)
```

### Why Window Functions are Game-Changing

| Task | Without Window Functions | With Window Functions |
|------|--------------------------|----------------------|
| Rank products by sales | Complex self-join | `RANK() OVER (ORDER BY sales DESC)` |
| Month-over-month growth | Correlated subquery | `LAG(revenue, 1) OVER (ORDER BY month)` |
| Running total | Correlated subquery | `SUM(amount) OVER (ORDER BY date)` |
| Top N per category | Complex CTE + row numbering | `ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC)` |

### Window Function Reference — All Definitions

#### Ranking Functions
| Function | Definition | Tie Handling |
|----------|-----------|-------------|
| `ROW_NUMBER()` | Assigns a unique sequential integer to every row. Never repeats, never skips. | Ties get different numbers (arbitrary) |
| `RANK()` | Assigns the same rank to tied rows. The next rank after a tie skips numbers. | 1,2,2,4 — skips 3 |
| `DENSE_RANK()` | Same rank for ties, but the next rank does NOT skip. | 1,2,2,3 — no gaps |
| `NTILE(n)` | Divides rows into n equal-sized buckets (1 through n). | Unequal distribution when not divisible |
| `PERCENT_RANK()` | Relative rank as a proportion from 0.0 to 1.0 | — |
| `CUME_DIST()` | Cumulative distribution — fraction of rows with value ≤ current row | — |

#### Value/Offset Functions
| Function | Definition |
|----------|-----------|
| `LAG(col, n)` | Returns the value of `col` from n rows BEFORE the current row. NULL if no such row. |
| `LEAD(col, n)` | Returns the value of `col` from n rows AFTER the current row. NULL if no such row. |
| `FIRST_VALUE(col)` | Returns the value of `col` from the FIRST row of the window |
| `LAST_VALUE(col)` | Returns the value of `col` from the LAST row of the window |
| `NTH_VALUE(col, n)` | Returns the value from the nth row of the window |

#### Aggregate Window Functions
| Function | Definition |
|----------|-----------|
| `SUM(col) OVER (...)` | Running / cumulative sum within the window |
| `AVG(col) OVER (...)` | Running / moving average within the window |
| `COUNT(*) OVER (...)` | Cumulative or partition count |
| `MIN(col) OVER (...)` | Running minimum |
| `MAX(col) OVER (...)` | Running maximum |

#### Key Clauses
| Clause | Definition |
|--------|-----------|
| `OVER ()` | Empty OVER — the window is the entire result set |
| `PARTITION BY col` | Divides result into independent windows (groups) — like GROUP BY but keeps all rows |
| `ORDER BY col` | Orders rows within each partition for sequential functions |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | The default frame for running totals — from start of partition to current row |
| `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` | Moving average frame — current row + 2 rows before |
"""
))

cells.append(code(
"""print("=== ROW_NUMBER — Unique sequential rank ===")
print("Assigns 1, 2, 3... with no ties and no gaps.")
print("Most common use: get the top 1 (or top N) row per group.")
print()
print("Top product by revenue in each category:")
print(Q("""
    WITH product_sales AS (
        SELECT
            cat.name                                              AS category,
            p.name                                               AS product,
            ROUND(SUM(oi.qty * oi.unit_price * (1-oi.discount_pct/100)), 0) AS revenue
        FROM order_items oi
        JOIN products   p   ON oi.product_id  = p.product_id
        JOIN categories cat ON p.category_id  = cat.category_id
        GROUP BY cat.name, p.product_id, p.name
    ),
    ranked AS (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
        FROM product_sales
    )
    SELECT category, product, revenue
    FROM   ranked
    WHERE  rn = 1
    ORDER  BY revenue DESC
"""))
"""
))

cells.append(code(
"""print("=== RANK vs DENSE_RANK vs ROW_NUMBER — Side-by-side comparison ===")
print(Q("""
    WITH monthly_revenue AS (
        SELECT
            SUBSTR(order_date, 1, 7)           AS month,
            ROUND(SUM(total_amount), 0)         AS revenue
        FROM orders
        WHERE status NOT IN ('Cancelled','Returned')
        GROUP BY month
    )
    SELECT
        month,
        revenue,
        ROW_NUMBER()  OVER (ORDER BY revenue DESC) AS row_number,
        RANK()        OVER (ORDER BY revenue DESC) AS rank,
        DENSE_RANK()  OVER (ORDER BY revenue DESC) AS dense_rank,
        NTILE(3)      OVER (ORDER BY revenue DESC) AS quartile_bucket
    FROM monthly_revenue
    ORDER BY revenue DESC
"""))
print()
print("Explanation:")
print("  ROW_NUMBER → always unique: 1,2,3,4,5...")
print("  RANK       → ties share rank, next rank SKIPS: 1,2,2,4...")
print("  DENSE_RANK → ties share rank, next rank does NOT skip: 1,2,2,3...")
print("  NTILE(3)   → divides rows into 3 equal buckets (1=top third)")
"""
))

cells.append(code(
"""print("=== LAG and LEAD — Compare to previous/next rows ===")
print("LAG(col, n)  = value from n rows BEFORE current row (default n=1)")
print("LEAD(col, n) = value from n rows AFTER  current row (default n=1)")
print("Essential for: Month-over-Month growth, Day-over-Day comparison, churn detection")
print()
print("Monthly revenue with MoM growth:")
print(Q("""
    WITH monthly AS (
        SELECT
            SUBSTR(order_date, 1, 7)            AS month,
            ROUND(SUM(total_amount), 0)          AS revenue
        FROM orders
        WHERE status NOT IN ('Cancelled', 'Returned')
        GROUP BY month
        ORDER BY month
    )
    SELECT
        month,
        revenue                                                              AS current_revenue,
        LAG(revenue, 1)  OVER (ORDER BY month)                              AS prev_month_revenue,
        LEAD(revenue, 1) OVER (ORDER BY month)                              AS next_month_revenue,
        ROUND((revenue - LAG(revenue,1) OVER (ORDER BY month))
              / LAG(revenue,1) OVER (ORDER BY month) * 100, 1)              AS mom_growth_pct
    FROM monthly
"""))
"""
))

cells.append(code(
"""print("=== Running Totals and Cumulative Sums ===")
print("SUM() OVER (ORDER BY date) creates a cumulative total —")
print("each row shows the total from row 1 up to and including the current row.")
print()
print(Q("""
    WITH daily AS (
        SELECT
            order_date,
            COUNT(*)                    AS orders,
            ROUND(SUM(total_amount), 0) AS daily_revenue
        FROM orders
        WHERE status NOT IN ('Cancelled','Returned')
        GROUP BY order_date
    )
    SELECT
        order_date,
        orders,
        daily_revenue,
        SUM(daily_revenue) OVER (ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        ROUND(AVG(daily_revenue) OVER (ORDER BY order_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0)     AS moving_avg_3day,
        MAX(daily_revenue) OVER ()                            AS peak_day_revenue
    FROM daily
    ORDER BY order_date
"""))
"""
))

cells.append(code(
"""print("=== PARTITION BY — Per-group window calculations ===")
print("PARTITION BY divides the rows into independent windows (one per group).")
print("Unlike GROUP BY, all rows are kept in the output — only the calculation scope changes.")
print()
print("Each order's amount vs the customer's own average:")
print(Q("""
    SELECT
        o.order_id,
        c.name                                                         AS customer,
        c.tier,
        o.order_date,
        ROUND(o.total_amount, 0)                                       AS order_amount,
        ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 0) AS customer_avg,
        ROUND(SUM(o.total_amount) OVER (PARTITION BY o.customer_id
            ORDER BY o.order_date), 0)                                 AS customer_running_total,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id
            ORDER BY o.total_amount DESC)                              AS order_rank_for_customer
    FROM orders   o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status NOT IN ('Cancelled','Returned')
    ORDER BY c.name, o.order_date
"""))
"""
))

cells.append(code(
"""print("=== NTILE — Divide customers into spending quartiles ===")
print("NTILE(n) assigns each row to a bucket from 1 to n based on ORDER BY.")
print("If rows are not evenly divisible, earlier buckets get one extra row.")
print()
print(Q("""
    WITH customer_spend AS (
        SELECT
            c.customer_id,
            c.name,
            c.tier,
            c.city,
            ROUND(SUM(o.total_amount), 0)   AS total_spent,
            COUNT(o.order_id)                AS order_count
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
            AND o.status NOT IN ('Cancelled','Returned')
        GROUP BY c.customer_id, c.name, c.tier, c.city
    )
    SELECT
        name,
        tier,
        city,
        total_spent,
        order_count,
        NTILE(4) OVER (ORDER BY total_spent DESC) AS spending_quartile,
        CASE NTILE(4) OVER (ORDER BY total_spent DESC)
            WHEN 1 THEN 'Top 25% Spenders'
            WHEN 2 THEN 'Upper Mid Spenders'
            WHEN 3 THEN 'Lower Mid Spenders'
            WHEN 4 THEN 'Bottom 25% Spenders'
        END AS segment
    FROM customer_spend
    ORDER BY total_spent DESC
"""))
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DAY 19 — QUERY OPTIMISATION
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(90deg,#E65100,#BF360C);padding:22px 32px;border-radius:12px;color:white;">
<h1 style="margin:0;font-size:2em;">Day 19 — Query Optimisation</h1>
<p style="margin:6px 0 0;color:#FFCCBC;font-size:1.1em;">EXPLAIN ANALYZE · Indexes · Execution Plans · Best Practices · Anti-Patterns</p>
</div>
"""
))

cells.append(md(
"""## Query Optimisation — Making SQL Run Fast

### Why Optimisation Matters

A poorly written query on a 10-million-row table can take **minutes**. The same query, correctly optimised, runs in **milliseconds**. As a data analyst, you'll regularly query production databases where performance directly affects business operations.

### Core Concepts — Definitions

| Concept | Definition |
|---------|-----------|
| **Query Planner** | The database engine component that decides HOW to execute a query — which indexes to use, which tables to scan first, how to join |
| **Execution Plan** | The step-by-step plan the query planner creates before running a query |
| **EXPLAIN** | SQL command that shows the execution plan WITHOUT running the query |
| **EXPLAIN ANALYZE** | Shows the execution plan AND actually runs the query, reporting real timing |
| **Full Table Scan (Seq Scan)** | The database reads EVERY row in a table to find matches — slow on large tables |
| **Index Scan** | Uses an index to jump directly to matching rows — much faster |
| **Index** | A sorted data structure (like a book's index) that allows fast lookup by a specific column |
| **Selectivity** | How narrow a filter is — high selectivity (few matching rows) = indexes help a lot |
| **Cardinality** | Number of distinct values in a column — high cardinality (many distinct values) = better candidate for indexing |

### Types of Indexes — Definitions

| Index Type | Definition | Best For |
|-----------|-----------|---------|
| **B-Tree Index** | Default type. Balanced tree structure supporting equality, range, and ORDER BY | Most columns — equality and range queries |
| **Hash Index** | Hash table — only supports equality (`=`). Faster than B-Tree for exact match. | High-cardinality equality-only columns |
| **Partial Index** | Index built on a SUBSET of rows matching a condition | `WHERE is_active = 1` — index only active records |
| **Composite Index** | Index on multiple columns together | Multi-column WHERE / ORDER BY combinations |
| **Covering Index** | Index that contains ALL columns needed by a query — no table access needed | Read-heavy queries on specific column sets |
| **Unique Index** | Enforces uniqueness AND provides fast lookup | Primary keys, email columns |

### When Indexes Help vs When They Don't

| Index Helps | Index Does NOT Help (or hurts) |
|-------------|-------------------------------|
| High-selectivity WHERE clauses | Low-selectivity columns (e.g. `gender` with 2 values) |
| JOIN columns (FK → PK) | Columns used with functions: `WHERE UPPER(name) = 'RAHUL'` |
| ORDER BY on the indexed column | Very small tables (full scan is faster) |
| Columns frequently searched | Tables with heavy INSERT/UPDATE (indexes slow writes) |
"""
))

cells.append(code(
"""print("=== EXPLAIN in SQLite ===")
print("SQLite's EXPLAIN QUERY PLAN shows the query strategy without running it.")
print("Look for 'SCAN TABLE' (slow) vs 'SEARCH TABLE USING INDEX' (fast).")
print()

print("--- Query plan WITHOUT an index ---")
plan = Q("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 'C001'")
print(plan)

print()
print("--- Creating an index on customer_id ---")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
conn.commit()
print("Index created: idx_orders_customer on orders(customer_id)")

print()
print("--- Query plan AFTER index creation ---")
plan2 = Q("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 'C001'")
print(plan2)
print()
print("With an index, the database jumps directly to matching rows")
print("instead of scanning the entire table.")
"""
))

cells.append(code(
"""import time

print("=== Performance Comparison — with and without index ===")

# Drop index temporarily for fair comparison
cur.execute("DROP INDEX IF EXISTS idx_test")
conn.commit()

# Slow query — full scan simulation
slow_q = """
    SELECT order_id, customer_id, total_amount
    FROM orders
    WHERE customer_id IN ('C001','C002','C005','C009','C011')
      AND status = 'Delivered'
"""
t0 = time.perf_counter()
for _ in range(500): Q(slow_q)
t1 = time.perf_counter()
print(f"Without optimal index — 500 runs: {(t1-t0)*1000:.1f} ms")

# Create composite index
cur.execute("CREATE INDEX idx_test ON orders(customer_id, status)")
conn.commit()

t2 = time.perf_counter()
for _ in range(500): Q(slow_q)
t3 = time.perf_counter()
print(f"With composite index   — 500 runs: {(t3-t2)*1000:.1f} ms")
print()
print("Composite index on (customer_id, status) covers BOTH WHERE conditions.")
"""
))

cells.append(md(
"""## Query Optimisation Best Practices

### The 10 Rules of Fast SQL

| Rule | Bad Practice | Good Practice |
|------|-------------|---------------|
| **1. Avoid SELECT *** | `SELECT * FROM orders` | `SELECT order_id, amount FROM orders` |
| **2. Filter early with WHERE** | Filter after joining | Filter in WHERE or subquery first |
| **3. Use indexes on join columns** | Unindexed FK columns | `CREATE INDEX ON orders(customer_id)` |
| **4. Avoid functions on indexed columns** | `WHERE YEAR(date) = 2024` | `WHERE date BETWEEN '2024-01-01' AND '2024-12-31'` |
| **5. Use EXISTS over IN for large lists** | `WHERE id IN (SELECT id FROM ...)` | `WHERE EXISTS (SELECT 1 FROM ... WHERE ...)` |
| **6. Avoid DISTINCT if unnecessary** | Overuse of DISTINCT | Fix the query logic to avoid duplicates |
| **7. LIMIT during development** | `SELECT * FROM big_table` | `SELECT * FROM big_table LIMIT 100` |
| **8. Use CTEs for readability** | Nested 4-level subqueries | CTEs with meaningful names |
| **9. Profile before optimising** | Random guessing | Use EXPLAIN ANALYZE to find bottlenecks |
| **10. Index foreign keys** | Unindexed FK columns | Always index FK columns in child tables |
"""
))

cells.append(code(
"""print("=== Anti-Pattern 1: SELECT * (avoid in production) ===")
print("Bad: SELECT * retrieves all 15 columns even if you need only 3.")
print("Good: Name exactly what you need — reduces I/O and network transfer.")
print()
bad = Q("SELECT * FROM products LIMIT 3")
good = Q("SELECT product_id, name, price FROM products LIMIT 3")
print("Columns with SELECT *:", list(bad.columns))
print("Columns with named SELECT:", list(good.columns))

print()
print("=== Anti-Pattern 2: Function on indexed column in WHERE ===")
print("Bad: WHERE UPPER(name) = 'RAHUL SHARMA'  -- cannot use name index")
print("Good: WHERE name = 'Rahul Sharma'         -- uses name index")
print()
print("Bad pattern result:")
print(Q("SELECT name, city FROM customers WHERE UPPER(name) = 'RAHUL SHARMA'"))
print()
print("Good pattern result (exact case match):")
print(Q("SELECT name, city FROM customers WHERE name = 'Rahul Sharma'"))

print()
print("=== Anti-Pattern 3: Correlated subquery vs JOIN ===")
print("Bad: Correlated subquery runs once per outer row — O(n²) complexity")
print()
import time
t0 = time.perf_counter()
for _ in range(200):
    Q("""SELECT o.order_id, o.total_amount,
               (SELECT c.name FROM customers c WHERE c.customer_id = o.customer_id) AS cname
        FROM orders o LIMIT 10""")
t1 = time.perf_counter()
print(f"Correlated subquery 200x: {(t1-t0)*1000:.1f} ms")

t2 = time.perf_counter()
for _ in range(200):
    Q("""SELECT o.order_id, o.total_amount, c.name AS cname
        FROM orders o JOIN customers c ON o.customer_id = c.customer_id
        LIMIT 10""")
t3 = time.perf_counter()
print(f"JOIN (better)       200x: {(t3-t2)*1000:.1f} ms")

print()
print("=== Anti-Pattern 4: OR can disable index usage ===")
print("Bad: WHERE city='Mumbai' OR city='Delhi'")
plan_or = Q("EXPLAIN QUERY PLAN SELECT * FROM customers WHERE city='Mumbai' OR city='Delhi'")
print("OR plan:", plan_or.to_string(index=False))
print()
print("Better: WHERE city IN ('Mumbai','Delhi')  -- same result, often faster")
"""
))

cells.append(code(
"""print("=== Real-World Optimisation Example ===")
print("Scenario: Marketing team wants the top 3 customers by revenue per city.")
print()
print("Naive approach — full table analysis then filter in Python:")
import time
t0 = time.perf_counter()
result = Q("""
    SELECT c.city, c.name, c.tier,
           ROUND(SUM(o.total_amount),0) AS revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.city, c.customer_id, c.name, c.tier
    ORDER BY c.city, revenue DESC
""")
top3_naive = result.groupby('city').head(3).reset_index(drop=True)
t1 = time.perf_counter()
print(f"Naive approach: {(t1-t0)*1000:.2f} ms")
print(top3_naive)

print()
print("Optimised: Use window function in SQL — no Python post-processing:")
t2 = time.perf_counter()
top3_sql = Q("""
    WITH ranked AS (
        SELECT
            c.city, c.name, c.tier,
            ROUND(SUM(o.total_amount),0)                              AS revenue,
            DENSE_RANK() OVER (PARTITION BY c.city
                               ORDER BY SUM(o.total_amount) DESC)    AS rank_in_city
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
            AND o.status = 'Delivered'
        GROUP BY c.city, c.customer_id, c.name, c.tier
    )
    SELECT city, name, tier, revenue, rank_in_city
    FROM ranked
    WHERE rank_in_city <= 3
    ORDER BY city, rank_in_city
""")
t3 = time.perf_counter()
print(f"Optimised SQL: {(t3-t2)*1000:.2f} ms")
print(top3_sql)
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# DAY 20 — NoSQL / MongoDB
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(90deg,#1B5E20,#33691E);padding:22px 32px;border-radius:12px;color:white;">
<h1 style="margin:0;font-size:2em;">Day 20 — NoSQL & MongoDB</h1>
<p style="margin:6px 0 0;color:#C8E6C9;font-size:1.1em;">Document Model · CRUD Operations · Aggregation Pipeline · PyMongo · SQL vs NoSQL</p>
</div>
"""
))

cells.append(md(
"""## NoSQL — When Relational Databases Are Not the Right Tool

### What is NoSQL?
**NoSQL (Not Only SQL)** refers to a family of database management systems that store data in formats other than traditional relational tables. The term "Not Only SQL" reflects that these systems are complementary to, not replacements for, SQL databases.

### NoSQL Database Types — Definitions

| Type | Definition | Examples | Ideal For |
|------|-----------|---------|----------|
| **Document** | Stores data as flexible JSON-like documents. Each document can have different fields. | MongoDB, CouchDB, Firestore | Catalogues, user profiles, content management |
| **Key-Value** | Stores data as simple key → value pairs. Extremely fast reads. | Redis, DynamoDB, Memcached | Sessions, caching, leaderboards |
| **Column-Family** | Stores data in columns rather than rows. Optimised for aggregate queries over many rows. | Cassandra, HBase, BigTable | IoT, time-series, analytics at scale |
| **Graph** | Stores data as nodes and edges (relationships). Native relationship traversal. | Neo4j, Amazon Neptune | Social networks, recommendation engines |

### SQL vs NoSQL — Detailed Comparison

| Aspect | SQL (Relational) | NoSQL (Document — MongoDB) |
|--------|-----------------|--------------------------|
| **Data Model** | Tables with rows and columns — rigid schema | JSON-like documents — flexible schema |
| **Schema** | Fixed schema — must define before inserting | Dynamic schema — fields can differ per document |
| **Relationships** | Foreign keys + JOINs | Embedding or references (manual) |
| **Scaling** | Vertical (bigger server) | Horizontal (more servers — sharding) |
| **Consistency** | ACID guaranteed | BASE (eventual consistency by default) |
| **Query Language** | SQL (standardised) | MongoDB Query Language (MQL) |
| **Joins** | Native, optimised | `$lookup` — less performant |
| **Transactions** | Mature, fully supported | Supported from MongoDB 4.0+ |
| **Best For** | Structured data, complex queries, reporting | Flexible/nested data, high write volume, rapid iteration |

### MongoDB Key Terminology

| Term | Definition |
|------|-----------|
| **Document** | A single record stored as BSON (Binary JSON). Equivalent to one row in SQL. |
| **Collection** | A group of documents. Equivalent to a SQL table. No fixed schema required. |
| **Database** | A container for collections. Equivalent to a SQL database. |
| **Field** | A key-value pair within a document. Equivalent to a SQL column. |
| **_id** | Mandatory unique identifier field in every document. Auto-generated as ObjectId if not provided. |
| **BSON** | Binary JSON — MongoDB's internal storage format. Supports more data types than JSON (e.g. dates, binary). |
| **Embedded Document** | A document nested inside another document — avoids JOINs. |
| **Reference** | Storing the _id of another document to create a relationship (like a FK). |
| **Index** | Works same as SQL — speeds up query performance on specific fields. |
| **Aggregation Pipeline** | A sequence of data transformation stages (like SQL GROUP BY + JOIN + HAVING in one pipeline). |
| **Replica Set** | A group of MongoDB servers with one primary and multiple secondaries — provides high availability. |
| **Sharding** | Horizontal partitioning — distributing data across multiple servers for scale. |

### MongoDB CRUD Operations — Reference

| Operation | MongoDB | SQL Equivalent |
|-----------|---------|---------------|
| **Create (Insert)** | `db.collection.insertOne({})` / `insertMany([])` | `INSERT INTO table VALUES (...)` |
| **Read (Find)** | `db.collection.find({})` | `SELECT * FROM table WHERE ...` |
| **Update** | `db.collection.updateOne({filter}, {$set: {}})` | `UPDATE table SET col=val WHERE ...` |
| **Delete** | `db.collection.deleteOne({filter})` | `DELETE FROM table WHERE ...` |

### Query Operators — Definitions

| Operator | Definition | SQL Equivalent |
|----------|-----------|---------------|
| `{ field: value }` | Equality match | `WHERE field = value` |
| `$gt`, `$gte` | Greater than, greater than or equal | `>`, `>=` |
| `$lt`, `$lte` | Less than, less than or equal | `<`, `<=` |
| `$ne` | Not equal | `!= ` |
| `$in: [a,b]` | Value is one of the listed values | `IN (a, b)` |
| `$nin: [a,b]` | Value is NOT in the listed values | `NOT IN (a, b)` |
| `$and: [...]` | All conditions must be true | `AND` |
| `$or: [...]` | At least one condition must be true | `OR` |
| `$not: {...}` | Condition must be false | `NOT` |
| `$exists: true` | Field exists in the document | `IS NOT NULL` |
| `$regex: pattern` | Field matches a regular expression | `LIKE` |
| `$elemMatch` | Array contains at least one element matching the condition | No direct equivalent |
"""
))

cells.append(code(
"""# We simulate MongoDB using Python dictionaries — same logic as real PyMongo
# In production: pip install pymongo, then:
# from pymongo import MongoClient
# client = MongoClient('mongodb://localhost:27017/')
# db = client['shopfast']

print("=== MongoDB Simulation using Python (same API as PyMongo) ===")
print("In production, replace this with:")
print("  from pymongo import MongoClient")
print("  client = MongoClient('mongodb://localhost:27017/')")
print("  db = client['shopfast']")
print()

# ── Simulate a MongoDB collection using a Python class ────────────────────────
import json
from datetime import datetime

class MockCollection:
    def __init__(self): self._docs = []

    def insertOne(self, doc):
        if '_id' not in doc: doc['_id'] = len(self._docs) + 1
        self._docs.append(doc.copy()); return doc['_id']

    def insertMany(self, docs):
        ids = [self.insertOne(d) for d in docs]; return ids

    def find(self, query=None, projection=None, sort=None, limit=None):
        results = [d.copy() for d in self._docs if self._match(d, query or {})]
        if sort:
            for field, direction in reversed(sort):
                results.sort(key=lambda x: x.get(field, 0), reverse=(direction == -1))
        if limit: results = results[:limit]
        if projection:
            include = {k for k,v in projection.items() if v}
            exclude = {k for k,v in projection.items() if not v}
            if include:
                results = [{k: d.get(k) for k in include | {'_id'}} for d in results]
            if exclude:
                results = [{k:v for k,v in d.items() if k not in exclude} for d in results]
        return results

    def findOne(self, query):
        r = self.find(query); return r[0] if r else None

    def updateOne(self, query, update):
        for i, d in enumerate(self._docs):
            if self._match(d, query):
                if '$set' in update:   d.update(update['$set'])
                if '$inc' in update:
                    for f, v in update['$inc'].items(): d[f] = d.get(f,0) + v
                if '$push' in update:
                    for f, v in update['$push'].items():
                        if f not in d: d[f] = []
                        d[f].append(v)
                return True
        return False

    def deleteOne(self, query):
        for i, d in enumerate(self._docs):
            if self._match(d, query): self._docs.pop(i); return True
        return False

    def countDocuments(self, query=None): return len(self.find(query or {}))

    def _match(self, doc, query):
        for key, val in query.items():
            dval = doc.get(key)
            if isinstance(val, dict):
                for op, opval in val.items():
                    if op == '$gt'  and not (dval is not None and dval > opval):  return False
                    if op == '$gte' and not (dval is not None and dval >= opval): return False
                    if op == '$lt'  and not (dval is not None and dval < opval):  return False
                    if op == '$lte' and not (dval is not None and dval <= opval): return False
                    if op == '$ne'  and not (dval != opval):                      return False
                    if op == '$in'  and not (dval in opval):                      return False
                    if op == '$nin' and not (dval not in opval):                  return False
                    if op == '$exists' and opval and dval is None: return False
            elif val != dval: return False
        return True

    def aggregate(self, pipeline):
        import copy, statistics as st
        results = [copy.deepcopy(d) for d in self._docs]
        for stage in pipeline:
            if '$match' in stage:
                results = [d for d in results if self._match(d, stage['$match'])]
            elif '$project' in stage:
                proj = stage['$project']
                inc = {k for k,v in proj.items() if v == 1}
                exc = {k for k,v in proj.items() if v == 0}
                if inc:
                    results = [{k: d.get(k) for k in inc | {'_id'}} for d in results]
                else:
                    results = [{k:v for k,v in d.items() if k not in exc} for d in results]
            elif '$sort' in stage:
                for field, direction in reversed(list(stage['$sort'].items())):
                    results.sort(key=lambda x: x.get(field) or 0, reverse=(direction==-1))
            elif '$limit' in stage:
                results = results[:stage['$limit']]
            elif '$group' in stage:
                grp_spec = stage['$group']
                id_field  = grp_spec.get('_id')
                groups = {}
                for d in results:
                    key = d.get(id_field.lstrip('$'), id_field) if isinstance(id_field, str) and id_field.startswith('$') else id_field
                    if key not in groups: groups[key] = []
                    groups[key].append(d)
                new_results = []
                for key, grp in groups.items():
                    row = {'_id': key}
                    for out_field, agg in grp_spec.items():
                        if out_field == '_id': continue
                        if isinstance(agg, dict):
                            for op, field in agg.items():
                                fname = field.lstrip('$') if isinstance(field, str) and field.startswith('$') else field
                                vals = [d.get(fname) for d in grp if d.get(fname) is not None]
                                if op == '$sum':   row[out_field] = sum(vals) if vals else 0
                                elif op == '$avg': row[out_field] = round(sum(vals)/len(vals),2) if vals else 0
                                elif op == '$max': row[out_field] = max(vals) if vals else None
                                elif op == '$min': row[out_field] = min(vals) if vals else None
                                elif op == '$count': row[out_field] = len(grp)
                    new_results.append(row)
                results = new_results
            elif '$unwind' in stage:
                field = stage['$unwind'].lstrip('$')
                new_results = []
                for d in results:
                    arr = d.get(field, [])
                    if isinstance(arr, list):
                        for item in arr:
                            nd = d.copy(); nd[field] = item; new_results.append(nd)
                    else: new_results.append(d)
                results = new_results
        return results

class MockDB:
    def __init__(self):
        self._cols = {}
    def __getitem__(self, name):
        if name not in self._cols: self._cols[name] = MockCollection()
        return self._cols[name]
    def __getattr__(self, name):
        return self[name]
    def list_collection_names(self):
        return list(self._cols.keys())

db = MockDB()
print("✅ MongoDB simulation ready (db object created)")
print("   All methods mirror PyMongo exactly:")
print("   db.products.insertOne({...})")
print("   db.products.find({'category': 'Electronics'})")
print("   db.products.aggregate([{...}])")
"""
))

cells.append(code(
"""# ── INSERT operations ─────────────────────────────────────────────────────────
print("=== INSERT — insertOne() and insertMany() ===")
print("Definition: insertOne() adds one document. insertMany() adds multiple.")
print("Documents are flexible JSON-like objects — each can have different fields.")
print()

# In MongoDB, related data can be EMBEDDED in one document — no JOINs needed!
products_mongo = [
    {
        "product_id": "P001",
        "name": "Laptop Pro 15",
        "brand": "TechMaster",
        "category": "Laptops",
        "price": 85000,
        "cost_price": 60000,
        "stock": 50,
        "rating": 4.5,
        "specs": {                        # Embedded document
            "processor": "Intel i7 13th Gen",
            "ram_gb": 16,
            "storage_gb": 512,
            "display_inch": 15.6
        },
        "tags": ["work", "programming", "premium"],   # Array field
        "is_active": True
    },
    {
        "product_id": "P002",
        "name": "Wireless Mouse",
        "brand": "ClickPro",
        "category": "Accessories",
        "price": 1299,
        "cost_price": 600,
        "stock": 350,
        "rating": 4.2,
        "specs": {"connectivity": "USB Receiver", "battery_life_months": 12},
        "tags": ["wireless", "ergonomic"],
        "is_active": True
    },
    {
        "product_id": "P003",
        "name": "Python for Data Analytics",
        "brand": "TechPress",
        "category": "Books",
        "price": 599,
        "cost_price": 200,
        "stock": 500,
        "rating": 4.8,
        "specs": {"pages": 450, "language": "English", "edition": 3},
        "tags": ["python", "learning", "beginner"],
        "is_active": True
    },
    {
        "product_id": "P004",
        "name": "Noise Cancelling Headphones",
        "brand": "SoundMax",
        "category": "Electronics",
        "price": 8999,
        "cost_price": 4000,
        "stock": 80,
        "rating": 4.6,
        "specs": {"driver_mm": 40, "battery_hours": 30, "bluetooth_version": 5.2},
        "tags": ["music", "travel", "premium"],
        "is_active": True
    },
    {
        "product_id": "P005",
        "name": "Premium Yoga Mat",
        "brand": "FlexFit",
        "category": "Sports",
        "price": 1499,
        "cost_price": 500,
        "stock": 150,
        "rating": 4.4,
        "specs": {"thickness_mm": 6, "material": "TPE", "size_cm": "183x61"},
        "tags": ["yoga", "fitness", "eco-friendly"],
        "is_active": True
    },
    {
        "product_id": "P006",
        "name": "Samsung Galaxy S24",
        "brand": "Samsung",
        "category": "Mobiles",
        "price": 79999,
        "cost_price": 58000,
        "stock": 40,
        "rating": 4.6,
        "specs": {"ram_gb": 8, "storage_gb": 256, "camera_mp": 50},
        "tags": ["smartphone", "5G", "android"],
        "is_active": True
    },
]

ids = db.products.insertMany(products_mongo)
print(f"Inserted {len(ids)} products")
print()

# Show one document
p = db.products.findOne({"product_id": "P001"})
print("Full document structure for Laptop Pro 15:")
print(json.dumps(p, indent=2, default=str))
"""
))

cells.append(code(
"""print("=== FIND — Query documents ===")
print("db.collection.find(query, projection, sort, limit)")
print("  query      : filter conditions (like SQL WHERE)")
print("  projection : which fields to include/exclude (like SQL SELECT)")
print("  sort       : field + direction 1=ASC, -1=DESC")
print("  limit      : max number of results")
print()

print("--- Find all products (no filter) ---")
all_products = db.products.find()
for p in all_products:
    print(f"  {p['product_id']} | {p['name']:<35} | ₹{p['price']:>6,} | Rating: {p['rating']}")

print()
print("--- Filter: Electronics or Mobiles under ₹50,000 ---")
budget_electronics = db.products.find(
    {"category": {"$in": ["Electronics","Mobiles"]}, "price": {"$lt": 50000}},
    sort=[("price", -1)]
)
for p in budget_electronics:
    print(f"  {p['name']:<35} ₹{p['price']:>6,}  ({p['category']})")

print()
print("--- Projection: Only name, price, and category ---")
projected = db.products.find(
    {"is_active": True},
    projection={"name": 1, "price": 1, "category": 1},
    sort=[("price", -1)]
)
for p in projected:
    print(f"  {p.get('name',''):<35} ₹{p.get('price',0):>6,}  {p.get('category','')}")

print()
print("--- Range filter: products priced ₹1,000–₹10,000 ---")
mid_range = db.products.find(
    {"price": {"$gte": 1000, "$lte": 10000}},
    sort=[("rating", -1)]
)
for p in mid_range:
    margin = round((p['price']-p['cost_price'])/p['price']*100, 1)
    print(f"  {p['name']:<35} ₹{p['price']:>6,}  Rating:{p['rating']}  Margin:{margin}%")
"""
))

cells.append(code(
"""print("=== UPDATE operations ===")
print("updateOne(filter, update_operators) — modify the first matching document")
print()
print("$set    : Set field to a new value")
print("$inc    : Increment a numeric field by a value")
print("$push   : Append a value to an array field")
print("$pull   : Remove a value from an array field")
print("$unset  : Remove a field from a document")
print()

# Show before
before = db.products.findOne({"product_id": "P001"})
print(f"BEFORE update — P001 price: ₹{before['price']:,}, stock: {before['stock']}")

# Apply a 5% price reduction
db.products.updateOne(
    {"product_id": "P001"},
    {"$set": {"price": round(before['price'] * 0.95)},
     "$inc": {"stock": -5}}
)
after = db.products.findOne({"product_id": "P001"})
print(f"AFTER  update — P001 price: ₹{after['price']:,}, stock: {after['stock']}")

print()
# Add a tag to the tags array
db.products.updateOne({"product_id": "P001"}, {"$push": {"tags": "sale"}})
updated = db.products.findOne({"product_id": "P001"})
print(f"Tags after $push 'sale': {updated['tags']}")

print()
print("=== DELETE operations ===")
print("deleteOne(filter) — remove first matching document")
print("deleteMany(filter) — remove all matching documents")
print()
print(f"Products before delete: {db.products.countDocuments()}")
# Add a temp document then delete it
db.products.insertOne({"product_id":"TEMP","name":"To Delete","price":100,"category":"Test","cost_price":50,"stock":0,"rating":0,"specs":{},"tags":[],"is_active":False})
print(f"After inserting TEMP:   {db.products.countDocuments()}")
db.products.deleteOne({"product_id": "TEMP"})
print(f"After deleting TEMP:    {db.products.countDocuments()}")
"""
))

cells.append(md(
"""## MongoDB Aggregation Pipeline

### What is the Aggregation Pipeline?
The **aggregation pipeline** is MongoDB's equivalent of SQL's `SELECT + JOIN + GROUP BY + HAVING + ORDER BY` — all in one flexible sequence of transformation stages.

Each stage transforms the documents and passes the result to the next stage.

### Pipeline Stages — Definitions

| Stage | Definition | SQL Equivalent |
|-------|-----------|---------------|
| `$match` | Filter documents — keep only those matching the condition | `WHERE` |
| `$project` | Reshape documents — include, exclude, or compute new fields | `SELECT` |
| `$group` | Group documents by a key and compute aggregates | `GROUP BY + aggregates` |
| `$sort` | Sort the resulting documents | `ORDER BY` |
| `$limit` | Keep only the first n documents | `LIMIT` |
| `$skip` | Skip the first n documents | `OFFSET` |
| `$lookup` | Join data from another collection | `JOIN` |
| `$unwind` | Deconstruct an array field — one document per array element | `JOIN` on array |
| `$addFields` | Add new computed fields to documents | Computed columns in `SELECT` |
| `$count` | Count documents in the pipeline | `COUNT(*)` |
| `$facet` | Run multiple sub-pipelines in parallel and combine results | Multiple GROUP BY queries |

### Aggregation Operators — Definitions

| Operator | Definition |
|----------|-----------|
| `$sum` | Sum of values (or count with `$sum: 1`) |
| `$avg` | Average of values |
| `$max` | Maximum value |
| `$min` | Minimum value |
| `$push` | Collect values into an array |
| `$addToSet` | Collect unique values into an array |
| `$first` | First value in the group |
| `$last` | Last value in the group |
"""
))

cells.append(code(
"""print("=== Aggregation Pipeline — Category Revenue Summary ===")
print("Equivalent to: SELECT category, COUNT(*), AVG(price) GROUP BY category")
print()

# First add orders data to MongoDB
orders_mongo = [
    {"order_id":"O001","product_id":"P001","customer":"Rahul","qty":1,"amount":85000,"date":"2024-01-05","city":"Mumbai"},
    {"order_id":"O002","product_id":"P004","customer":"Priya","qty":2,"amount":1198, "date":"2024-01-07","city":"Delhi"},
    {"order_id":"O003","product_id":"P006","customer":"Karan","qty":1,"amount":79999,"date":"2024-01-10","city":"Mumbai"},
    {"order_id":"O004","product_id":"P002","customer":"Amit","qty":1,"amount":1299, "date":"2024-01-12","city":"Bengaluru"},
    {"order_id":"O005","product_id":"P001","customer":"Vikram","qty":1,"amount":85000,"date":"2024-02-05","city":"Mumbai"},
    {"order_id":"O006","product_id":"P004","customer":"Sneha","qty":3,"amount":1797, "date":"2024-02-08","city":"Chennai"},
    {"order_id":"O007","product_id":"P005","customer":"Rahul","qty":1,"amount":1499, "date":"2024-02-14","city":"Mumbai"},
    {"order_id":"O008","product_id":"P006","customer":"Arjun","qty":1,"amount":79999,"date":"2024-03-01","city":"Hyderabad"},
    {"order_id":"O009","product_id":"P003","customer":"Divya","qty":1,"amount":8999, "date":"2024-03-05","city":"Delhi"},
    {"order_id":"O010","product_id":"P001","customer":"Meera","qty":1,"amount":85000,"date":"2024-03-10","city":"Chennai"},
]
db.orders.insertMany(orders_mongo)

pipeline_1 = [
    {"$match": {"amount": {"$gt": 0}}},           # Stage 1: filter
    {"$group": {
        "_id": "$city",
        "total_revenue": {"$sum": "$amount"},
        "order_count":   {"$sum": 1},
        "avg_order":     {"$avg": "$amount"},
    }},
    {"$sort": {"total_revenue": -1}},               # Stage 3: sort
]

results = db.orders.aggregate(pipeline_1)
print(f"{'City':<15} {'Orders':>6} {'Revenue':>12} {'Avg Order':>12}")
print("-" * 48)
for r in results:
    print(f"{r['_id']:<15} {r['order_count']:>6} ₹{r['total_revenue']:>10,} ₹{r['avg_order']:>10,.0f}")
"""
))

cells.append(code(
"""print("=== Product Performance Pipeline ===")
print("Multi-stage pipeline with match, group, sort, limit")
print()

product_pipeline = [
    {"$match": {"amount": {"$gt": 0}}},
    {"$group": {
        "_id":          "$product_id",
        "total_orders": {"$sum": 1},
        "total_qty":    {"$sum": "$qty"},
        "total_revenue":{"$sum": "$amount"},
        "avg_order":    {"$avg": "$amount"},
        "customers":    {"$push": "$customer"},
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 6},
]

results = db.orders.aggregate(product_pipeline)
print(f"{'Product':<8} {'Orders':>7} {'Total Qty':>10} {'Revenue':>12}")
print("-" * 44)
for r in results:
    print(f"{r['_id']:<8} {r['total_orders']:>7} {r['total_qty']:>10} ₹{r['total_revenue']:>10,}")

print()
print("=== $unwind — Flatten tags array, find top tags ===")
print("Definition: $unwind takes an array field and creates one document per element.")
tag_pipeline = [
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "product_count": {"$sum": 1}}},
    {"$sort": {"product_count": -1}},
]
tags = db.products.aggregate(tag_pipeline)
print("Most common product tags:")
for t in tags:
    bar = "█" * t["product_count"]
    print(f"  {t['_id']:<15} {t['product_count']} {bar}")
"""
))

cells.append(md(
"""## SQL vs NoSQL — When to Choose What

### Decision Framework

```
START HERE
    │
    ▼
Is the data highly relational (lots of JOINs needed)?
    │ YES → Use SQL (PostgreSQL, MySQL)
    │ NO  ↓
Is the schema fixed and unlikely to change?
    │ YES → Use SQL
    │ NO  ↓
Do you need massive horizontal scaling (millions of writes/sec)?
    │ YES → Use NoSQL (Cassandra, MongoDB)
    │ NO  ↓
Is the data naturally hierarchical / nested?
    │ YES → Use Document DB (MongoDB)
    │ NO  ↓
Is it simple key lookups with ultra-low latency?
    │ YES → Use Key-Value (Redis)
    │ NO  ↓
Is it relationship-heavy (social graph, recommendations)?
    │ YES → Use Graph DB (Neo4j)
    │ NO  → Default to SQL
```

### Real Industry Usage

| Company | SQL Use Case | NoSQL Use Case |
|---------|-------------|---------------|
| **Amazon** | Order history, inventory | Product catalogue (DynamoDB) |
| **Netflix** | Billing, subscriptions | User profiles, viewing history (Cassandra) |
| **Zomato** | Financial transactions | Restaurant menus, user sessions (MongoDB) |
| **LinkedIn** | Billing, HR data | Social graph (custom graph DB) |
| **Uber** | Payment records | Geolocation data (Redis) |
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# WEEK 4 CAPSTONE
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
<div style="background:linear-gradient(135deg,#0D1B2A 0%,#1565C0 50%,#00838F 100%);padding:28px 35px;border-radius:14px;color:white;">
<h1 style="margin:0;font-size:2em;">Week 4 Capstone — SQL Analytics Deep Dive</h1>
<p style="margin:8px 0 0;color:#A5D6A7;font-size:1.1em;">Combining SQL Foundations + Advanced SQL + Window Functions into one full business report</p>
</div>
"""
))

cells.append(code(
"""import pandas as pd

print("=" * 65)
print("   SHOPFAST E-COMMERCE — QUARTERLY ANALYTICS REPORT")
print("   Powered by SQL — Window Functions + CTEs + Advanced Joins")
print("=" * 65)

print()
print("━" * 65)
print("1. EXECUTIVE REVENUE SUMMARY")
print("━" * 65)
print(Q("""
    SELECT
        SUBSTR(order_date, 1, 7)                               AS month,
        COUNT(*)                                               AS total_orders,
        COUNT(CASE WHEN status='Delivered' THEN 1 END)         AS delivered,
        COUNT(CASE WHEN status='Cancelled' THEN 1 END)         AS cancelled,
        ROUND(SUM(CASE WHEN status='Delivered'
                  THEN total_amount ELSE 0 END), 0)            AS delivered_revenue,
        ROUND(AVG(CASE WHEN status='Delivered'
                  THEN total_amount END), 0)                   AS avg_order_value,
        ROUND(COUNT(CASE WHEN status='Cancelled' THEN 1 END)
              * 100.0 / COUNT(*), 1)                           AS cancellation_pct
    FROM orders
    GROUP BY month
    ORDER BY month
"""))

print()
print("━" * 65)
print("2. CUSTOMER VALUE SEGMENTATION (RFM-lite using Window Functions)")
print("━" * 65)
print(Q("""
    WITH customer_metrics AS (
        SELECT
            c.customer_id,
            c.name,
            c.tier,
            c.city,
            COUNT(DISTINCT o.order_id)                AS frequency,
            ROUND(SUM(o.total_amount), 0)             AS monetary,
            MAX(o.order_date)                         AS last_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
            AND o.status NOT IN ('Cancelled','Returned')
        GROUP BY c.customer_id, c.name, c.tier, c.city
    ),
    ranked AS (
        SELECT
            *,
            NTILE(4) OVER (ORDER BY monetary DESC)    AS monetary_quartile,
            NTILE(4) OVER (ORDER BY frequency DESC)   AS frequency_quartile,
            DENSE_RANK() OVER (ORDER BY monetary DESC) AS revenue_rank
        FROM customer_metrics
    )
    SELECT
        revenue_rank AS rank,
        name, tier, city,
        frequency   AS orders,
        monetary    AS lifetime_value,
        CASE
            WHEN monetary_quartile = 1 AND frequency_quartile = 1 THEN 'Champion'
            WHEN monetary_quartile <= 2 AND frequency_quartile <= 2 THEN 'Loyal'
            WHEN monetary_quartile = 1 THEN 'Big Spender'
            WHEN frequency_quartile = 1 THEN 'Frequent Buyer'
            WHEN monetary = 0 THEN 'Dormant'
            ELSE 'Regular'
        END AS segment
    FROM ranked
    ORDER BY monetary DESC
"""))

print()
print("━" * 65)
print("3. PRODUCT PERFORMANCE WITH WINDOW FUNCTIONS")
print("━" * 65)
print(Q("""
    WITH product_revenue AS (
        SELECT
            p.name                                                   AS product,
            cat.name                                                 AS category,
            SUM(oi.qty)                                              AS units_sold,
            ROUND(SUM(oi.qty * oi.unit_price*(1-oi.discount_pct/100)), 0) AS net_revenue,
            ROUND(AVG(p.rating), 2)                                  AS avg_rating
        FROM order_items oi
        JOIN products   p   ON oi.product_id  = p.product_id
        JOIN categories cat ON p.category_id  = cat.category_id
        GROUP BY p.product_id, p.name, cat.name
    )
    SELECT
        product,
        category,
        units_sold,
        net_revenue,
        avg_rating,
        RANK()       OVER (ORDER BY net_revenue DESC)                         AS overall_rank,
        RANK()       OVER (PARTITION BY category ORDER BY net_revenue DESC)   AS rank_in_category,
        ROUND(net_revenue * 100.0 / SUM(net_revenue) OVER (), 1)              AS revenue_share_pct,
        ROUND(SUM(net_revenue) OVER (ORDER BY net_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            * 100.0 / SUM(net_revenue) OVER (), 1)                            AS cumulative_share_pct
    FROM product_revenue
    ORDER BY net_revenue DESC
"""))

print()
print("━" * 65)
print("4. EMPLOYEE PERFORMANCE REPORT")
print("━" * 65)
print(Q("""
    SELECT
        e.name                                  AS employee,
        e.role,
        e.department,
        m.name                                  AS manager,
        COUNT(o.order_id)                       AS orders_handled,
        COUNT(CASE WHEN o.status='Delivered' THEN 1 END) AS delivered,
        ROUND(SUM(CASE WHEN o.status='Delivered'
                  THEN o.total_amount ELSE 0 END), 0)    AS revenue_generated,
        ROUND(COUNT(CASE WHEN o.status='Delivered' THEN 1 END)
              * 100.0 / NULLIF(COUNT(o.order_id),0), 1)  AS delivery_success_pct,
        DENSE_RANK() OVER (ORDER BY
            SUM(CASE WHEN o.status='Delivered' THEN o.total_amount ELSE 0 END) DESC) AS revenue_rank
    FROM employees e
    LEFT JOIN orders o ON e.emp_id = o.emp_id
    LEFT JOIN employees m ON e.manager_id = m.emp_id
    GROUP BY e.emp_id, e.name, e.role, e.department, m.name
    ORDER BY revenue_generated DESC
"""))

print()
print("━" * 65)
print("5. MONTH-OVER-MONTH GROWTH ANALYSIS")
print("━" * 65)
print(Q("""
    WITH monthly AS (
        SELECT
            SUBSTR(order_date, 1, 7)             AS month,
            COUNT(*)                              AS orders,
            COUNT(DISTINCT customer_id)           AS unique_customers,
            ROUND(SUM(CASE WHEN status='Delivered' THEN total_amount ELSE 0 END), 0) AS revenue
        FROM orders
        GROUP BY month
    )
    SELECT
        month,
        orders,
        unique_customers,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY month)    AS prev_revenue,
        ROUND((revenue - LAG(revenue,1) OVER (ORDER BY month))
            / NULLIF(LAG(revenue,1) OVER (ORDER BY month), 0) * 100, 1) AS mom_growth_pct,
        SUM(revenue) OVER (ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
    FROM monthly
    ORDER BY month
"""))

print()
print("=" * 65)
print("Report complete. All queries powered by Week 4 SQL skills.")
print("=" * 65)
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# WRAP-UP & GLOSSARY
# ══════════════════════════════════════════════════════════════════════════════
cells.append(md(
"""---
## Week 4 — Complete Mastery Checklist

### Day 16 — SQL Foundations
- [ ] Understand what SQL is and why every analyst needs it
- [ ] Know all key database terms: table, row, column, PK, FK, NULL, schema
- [ ] Use DDL: `CREATE TABLE` with constraints (NOT NULL, UNIQUE, CHECK, DEFAULT, REFERENCES)
- [ ] Use DML: `INSERT`, `UPDATE`, `DELETE` safely with WHERE
- [ ] Write `SELECT` with specific columns, aliases (AS), and DISTINCT
- [ ] Filter rows with `WHERE`, `AND/OR`, `BETWEEN`, `IN`, `LIKE`, `IS NULL`
- [ ] Sort results with `ORDER BY ASC/DESC` and paginate with `LIMIT/OFFSET`
- [ ] Use aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- [ ] Group data with `GROUP BY` and filter groups with `HAVING`

### Day 17 — Advanced SQL
- [ ] Write INNER, LEFT, RIGHT, and FULL OUTER JOINs
- [ ] Use SELF JOIN for hierarchical data (org charts)
- [ ] Write scalar, row, table, and correlated subqueries
- [ ] Use `IN`, `NOT IN`, `EXISTS`, `NOT EXISTS`
- [ ] Simplify complex queries with CTEs (`WITH ... AS (...)`)
- [ ] Apply conditional logic with `CASE WHEN ... THEN ... ELSE ... END`
- [ ] Handle NULLs gracefully with `COALESCE` and `NULLIF`
- [ ] Use string functions: `UPPER`, `LOWER`, `SUBSTR`, `REPLACE`, `LENGTH`
- [ ] Use date functions: `STRFTIME`, `JULIANDAY`, `DATE`

### Day 18 — Window Functions
- [ ] Explain the difference between window functions and GROUP BY
- [ ] Use `ROW_NUMBER()` to get the top-N row per group
- [ ] Distinguish `RANK()` vs `DENSE_RANK()` vs `ROW_NUMBER()`
- [ ] Use `LAG()` and `LEAD()` for period-over-period comparison
- [ ] Calculate running totals with `SUM() OVER (ORDER BY ...)`
- [ ] Create moving averages with `ROWS BETWEEN n PRECEDING AND CURRENT ROW`
- [ ] Segment data into equal buckets with `NTILE(n)`
- [ ] Partition window calculations per group with `PARTITION BY`

### Day 19 — Query Optimisation
- [ ] Read and interpret `EXPLAIN QUERY PLAN` output
- [ ] Create B-Tree and composite indexes on the right columns
- [ ] Avoid common anti-patterns: `SELECT *`, functions on indexed columns
- [ ] Choose `JOIN` over correlated subqueries for performance
- [ ] Use `EXISTS` instead of `IN` for large subquery result sets
- [ ] Follow the 10 rules of fast SQL

### Day 20 — NoSQL / MongoDB
- [ ] Explain the difference between SQL and NoSQL databases
- [ ] Know all 4 NoSQL types: document, key-value, column-family, graph
- [ ] Understand MongoDB terminology: document, collection, _id, BSON
- [ ] Perform CRUD: `insertOne`, `find`, `updateOne`, `deleteOne`
- [ ] Use query operators: `$gt`, `$in`, `$or`, `$exists`, `$regex`
- [ ] Use update operators: `$set`, `$inc`, `$push`, `$pull`
- [ ] Build aggregation pipelines: `$match → $group → $sort → $limit`
- [ ] Use `$unwind` for array fields and `$lookup` for joining collections
- [ ] Know when to use SQL vs NoSQL for a given use case

---

## Complete Week 4 Glossary

| Term | Definition |
|------|-----------|
| **ACID** | Atomicity, Consistency, Isolation, Durability — guarantees of relational DB transactions |
| **Aggregation Pipeline** | MongoDB's multi-stage data transformation and analysis framework |
| **Alias (AS)** | A temporary name given to a column or table in a query |
| **B-Tree Index** | Balanced tree index structure supporting equality and range queries |
| **BSON** | Binary JSON — MongoDB's internal binary document storage format |
| **Cardinality** | Number of distinct values in a column |
| **CTE** | Common Table Expression — a named temporary result set defined with WITH |
| **Correlated Subquery** | A subquery that references columns from the outer query — runs once per outer row |
| **COALESCE** | Returns the first non-NULL value from a list of arguments |
| **Collection** | MongoDB's equivalent of a SQL table — a group of documents |
| **Composite Index** | An index built on two or more columns together |
| **DENSE_RANK()** | Window function — rank with no gaps after ties |
| **Document** | MongoDB's basic unit of data — a JSON-like flexible record |
| **DDL** | Data Definition Language — SQL for defining structure (CREATE, ALTER, DROP) |
| **DML** | Data Manipulation Language — SQL for changing data (INSERT, UPDATE, DELETE) |
| **Execution Plan** | The database's step-by-step plan for executing a query |
| **EXPLAIN** | SQL command that shows the execution plan |
| **FIRST_VALUE()** | Window function — value from the first row of the window |
| **Full Table Scan** | Reading every row in a table — slow on large tables |
| **HAVING** | Filters groups after GROUP BY — can use aggregate functions |
| **Index** | A sorted data structure that enables fast row lookup |
| **INNER JOIN** | Returns only rows with matches in both tables |
| **LAG()** | Window function — value from n rows before the current row |
| **LEAD()** | Window function — value from n rows after the current row |
| **LEFT JOIN** | Returns all rows from the left table, NULLs for unmatched right rows |
| **NoSQL** | Not Only SQL — database systems using non-tabular storage formats |
| **NTILE(n)** | Window function — divides rows into n equal-sized buckets |
| **NULL** | A special marker meaning "value unknown or missing" |
| **NULLIF(a,b)** | Returns NULL if a equals b; otherwise returns a (prevents division by zero) |
| **OVER()** | Defines the window for a window function |
| **PARTITION BY** | Divides rows into independent windows — like GROUP BY but keeps all rows |
| **Primary Key** | A column (or set) that uniquely identifies every row in a table |
| **Query Planner** | Database engine component that decides how to execute a query |
| **RANK()** | Window function — same rank for ties, skips next rank |
| **ROW_NUMBER()** | Window function — unique sequential integer per row |
| **Schema** | The blueprint of a database — tables, columns, types, constraints |
| **Self Join** | Joining a table to itself using two aliases |
| **Selectivity** | How narrow a filter is — high selectivity means fewer rows match |
| **Subquery** | A SELECT statement nested inside another SQL statement |
| **WINDOW FUNCTION** | A function that computes across related rows without collapsing them |

---
*Week 4 Complete Notebook · Data Analytics Professional Course · 60-Day Program*  
*Days 16–20 · SQL Foundations → Advanced → Window Functions → Optimisation → MongoDB*
"""
))

# ══════════════════════════════════════════════════════════════════════════════
# WRITE NOTEBOOK
# ══════════════════════════════════════════════════════════════════════════════
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "version": "3.10.0"
        }
    },
    "cells": cells
}

output_path = "/mnt/user-data/outputs/Week4_SQL_Database_Analytics_Complete.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

import os
md_n   = sum(1 for c in cells if c["cell_type"] == "markdown")
code_n = sum(1 for c in cells if c["cell_type"] == "code")
lines  = sum(len(c["source"].split("\n")) for c in cells)
size   = os.path.getsize(output_path) / 1024

print(f"Notebook  : {output_path}")
print(f"Total cells: {len(cells)}  (markdown={md_n}, code={code_n})")
print(f"Total lines: {lines:,}")
print(f"File size  : {size:.0f} KB")
