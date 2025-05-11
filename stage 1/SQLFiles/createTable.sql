CREATE TABLE Part
(
  part_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  last_update DATE NOT NULL,
  PRIMARY KEY (part_id)
);

CREATE TABLE employee
(
  employee_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  role VARCHAR(50) NOT NULL,
  start_date DATE NOT NULL,
  last_training DATE NOT NULL,
  PRIMARY KEY (employee_id)
);

CREATE TABLE Warehouse
(
  warehouse_id INT NOT NULL,
  location VARCHAR(100) NOT NULL,
  capacity INT NOT NULL,
  open_date DATE NOT NULL,
  PRIMARY KEY (warehouse_id)
);

CREATE TABLE supplier
(
  supplier_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  PRIMARY KEY (supplier_id)
);

CREATE TABLE Costumer
(
  costumer_id INT NOT NULL,
  phone VARCHAR(20) NOT NULL,
  email VARCHAR(100) NOT NULL,
  registration_date DATE NOT NULL,
  PRIMARY KEY (costumer_id)
);

CREATE TABLE WorksAt
(
  warehouse_id INT NOT NULL,
  employee_id INT NOT NULL,
  PRIMARY KEY (warehouse_id, employee_id),
  FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
  FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

CREATE TABLE WarehouseParts
(
  wQuantity INT NOT NULL,
  last_updated DATE NOT NULL,
  part_id INT NOT NULL,
  warehouse_id INT NOT NULL,
  PRIMARY KEY (part_id, warehouse_id),
  FOREIGN KEY (part_id) REFERENCES Part(part_id),
  FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

CREATE TABLE SupplierParts
(
  price DECIMAL(10,2) NOT NULL,
  sQuantity INT NOT NULL,
  supplier_id INT NOT NULL,
  part_id INT NOT NULL,
  PRIMARY KEY (supplier_id, part_id),
  FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id),
  FOREIGN KEY (part_id) REFERENCES Part(part_id)
);

CREATE TABLE myorder
(
  order_id INT NOT NULL,
  amount INT NOT NULL,
  order_date DATE NOT NULL,
  arrival_date DATE NOT NULL,
  part_id INT NOT NULL,
  supplier_id INT NOT NULL,
  warehouse_id INT NOT NULL,
  PRIMARY KEY (order_id),
  FOREIGN KEY (part_id) REFERENCES Part(part_id),
  FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
  FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);


CREATE TABLE CostumerWarehousStorage
(
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  warehouse_id INT NOT NULL,
  costumer_id INT NOT NULL,
  PRIMARY KEY (warehouse_id, costumer_id),
  FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
  FOREIGN KEY (costumer_id) REFERENCES Costumer(costumer_id)
);

CREATE TABLE Train
(
  train_id INT NOT NULL,
  model VARCHAR(50) NOT NULL,
  year INT NOT NULL,
  last_check DATE NOT NULL,
  next_check DATE NOT NULL,
  warehouse_id INT NOT NULL,
  PRIMARY KEY (train_id),
  FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);
