DB_SCHEMA = """
-- Down
DROP TABLE IF EXISTS orderdetails CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS offices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS productlines CASCADE;

-- Tables
CREATE TABLE productlines ("productLine" VARCHAR(50) PRIMARY KEY, "textDescription" VARCHAR(4000), "htmlDescription" TEXT, "image" BYTEA);
CREATE TABLE products ("productCode" VARCHAR(15) PRIMARY KEY, "productName" VARCHAR(70) NOT NULL, "productLine" VARCHAR(50) NOT NULL, "productScale" VARCHAR(10) NOT NULL, "productVendor" VARCHAR(50) NOT NULL, "productDescription" TEXT NOT NULL, "quantityInStock" INTEGER NOT NULL, "buyPrice" NUMERIC(10,2) NOT NULL, "MSRP" NUMERIC(10,2) NOT NULL, FOREIGN KEY ("productLine") REFERENCES productlines("productLine"));
CREATE TABLE offices ("officeCode" VARCHAR(10) PRIMARY KEY, "city" VARCHAR(50) NOT NULL, "phone" VARCHAR(50) NOT NULL, "addressLine1" VARCHAR(50) NOT NULL, "addressLine2" VARCHAR(50), "state" VARCHAR(50), "country" VARCHAR(50) NOT NULL, "postalCode" VARCHAR(15) NOT NULL, "territory" VARCHAR(10) NOT NULL);
CREATE TABLE employees ("employeeNumber" INTEGER PRIMARY KEY, "lastName" VARCHAR(50) NOT NULL, "firstName" VARCHAR(50) NOT NULL, "extension" VARCHAR(10) NOT NULL, "email" VARCHAR(100) NOT NULL, "officeCode" VARCHAR(10) NOT NULL, "reportsTo" INTEGER, "jobTitle" VARCHAR(50) NOT NULL, FOREIGN KEY ("reportsTo") REFERENCES employees("employeeNumber"), FOREIGN KEY ("officeCode") REFERENCES offices("officeCode"));
CREATE TABLE customers ("customerNumber" INTEGER PRIMARY KEY, "customerName" VARCHAR(50) NOT NULL, "contactLastName" VARCHAR(50) NOT NULL, "contactFirstName" VARCHAR(50) NOT NULL, "phone" VARCHAR(50) NOT NULL, "addressLine1" VARCHAR(50) NOT NULL, "addressLine2" VARCHAR(50), "city" VARCHAR(50) NOT NULL, "state" VARCHAR(50), "postalCode" VARCHAR(15), "country" VARCHAR(50) NOT NULL, "salesRepEmployeeNumber" INTEGER, "creditLimit" NUMERIC(10,2), FOREIGN KEY ("salesRepEmployeeNumber") REFERENCES employees("employeeNumber"));
CREATE TABLE payments ("customerNumber" INTEGER, "checkNumber" VARCHAR(50), "paymentDate" DATE NOT NULL, "amount" NUMERIC(10,2) NOT NULL, PRIMARY KEY ("customerNumber", "checkNumber"), FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber"));
CREATE TABLE orders ("orderNumber" INTEGER PRIMARY KEY, "orderDate" DATE NOT NULL, "requiredDate" DATE NOT NULL, "shippedDate" DATE, "status" VARCHAR(15) NOT NULL, "comments" TEXT, "customerNumber" INTEGER NOT NULL, FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber"));
CREATE TABLE orderdetails ("orderNumber" INTEGER, "productCode" VARCHAR(15), "quantityOrdered" INTEGER NOT NULL, "priceEach" NUMERIC(10,2) NOT NULL, "orderLineNumber" SMALLINT NOT NULL, PRIMARY KEY ("orderNumber", "productCode"), FOREIGN KEY ("orderNumber") REFERENCES orders("orderNumber"), FOREIGN KEY ("productCode") REFERENCES products("productCode"));
"""

DECOMPOSITION_PROMPT = """You are a database engineering assistant. 
Your job is to break down the user's natural language question into structured components based ONLY on the provided schema.

Database Schema:
{DB_SCHEMA}

User Question: {query}

Instructions:
1. Return ONLY a valid JSON object. Do not include markdown formatting or explanations.
2. The JSON must have exactly these keys: "Intent", "Tables", "Columns", "Filters", "Joins".
3. Use the exact table and column names from the schema.
"""

GENERATION_PROMPT = """You are an expert PostgreSQL developer.
Your ONLY job is to translate structured JSON decomposition into a valid, executable PostgreSQL query.

Database Schema:
{schema}

Decomposition Data:
{decomposition}

STRICT RULES:
1. Return ONLY the raw SQL query. No explanations, no markdown formatting (do not use ```sql).
2. CRITICAL: Because the schema uses mixed-case column names, you MUST wrap ALL table names and column names in double quotes (e.g., SELECT "productCode" FROM products;). If you fail to use double quotes, the query will crash.
3. Only write SELECT queries. Do not write DELETE, UPDATE, or INSERT.
4. End your query with a semicolon (;).
"""

FIX_PROMPT = """You are an expert PostgreSQL debugger. 
An automated system tried to run a SQL query, but the database rejected it with an error. 

Database Schema:
{schema}

The Failed SQL Query:
{bad_sql}

The Database Error Message:
{error_msg}

Your job is to fix the SQL query so that it executes successfully.
CRITICAL RULE: Remember that all table names and column names MUST be enclosed in double quotes (e.g., "customerNumber") according to the schema.

Return ONLY the corrected raw SQL query. Do not include markdown formatting, apologies, or explanations. Just the code.
"""