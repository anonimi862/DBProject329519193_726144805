CREATE TABLE Train (
    train_id INT PRIMARY KEY,
    model VARCHAR2(50),
    year INT,
    last_check DATE,
    next_check DATE
);

CREATE TABLE Part (
    part_id INT PRIMARY KEY,
    name VARCHAR2(100),
    quantity INT,
    last_update DATE
);

CREATE TABLE Employee (
    employee_id INT PRIMARY KEY,
    name VARCHAR2(100),
    role VARCHAR2(50),
    start_date DATE,
    last_training DATE
);

CREATE TABLE Warehouse (
    warehouse_id INT PRIMARY KEY,
    location VARCHAR2(100),
    capacity INT,
    open_date DATE
);

CREATE TABLE Supplier (
    supplier_id INT PRIMARY KEY,
    name VARCHAR2(100),
    phone VARCHAR2(20),
    contract_date DATE
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    part_id INT,
    amount INT,
    order_date DATE,
    arrival_date DATE,
    FOREIGN KEY (part_id) REFERENCES Part(part_id)
);
