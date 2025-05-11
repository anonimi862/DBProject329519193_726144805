
-- Insert sample data into Part
INSERT INTO Part (part_id, name, last_update) VALUES
(1, 'Brake Pad', '2025-01-01'),
(2, 'Engine Valve', '2025-02-15');

-- Insert sample data into employee
INSERT INTO employee (employee_id, name, role, start_date, last_training) VALUES
(1, 'Alice Cohen', 'Technician', '2023-06-01', '2024-12-01'),
(2, 'Bob Levy', 'Manager', '2022-04-15', '2024-11-10');

-- Insert sample data into Warehouse
INSERT INTO Warehouse (warehouse_id, location, capacity, open_date) VALUES
(1, 'Haifa', 1000, '2020-01-01'),
(2, 'Tel Aviv', 800, '2021-03-10');

-- Insert sample data into supplier
INSERT INTO supplier (supplier_id, name, phone) VALUES
(1, 'TrainSupplies Ltd.', '03-1234567'),
(2, 'Global Parts Inc.', '03-7654321');

-- Insert sample data into Costumer
INSERT INTO Costumer (costumer_id, phone, email, registration_date) VALUES
(1, '050-1111111', 'john@example.com', '2023-05-20'),
(2, '050-2222222', 'sara@example.com', '2023-08-30');

-- Insert sample data into WorksAt
INSERT INTO WorksAt (warehouse_id, employee_id) VALUES
(1, 1),
(2, 2);

-- Insert sample data into WarehouseParts
INSERT INTO WarehouseParts (wQuantity, last_updated, part_id, warehouse_id) VALUES
(100, '2025-04-01', 1, 1),
(50, '2025-03-15', 2, 2);

-- Insert sample data into SupplierParts
INSERT INTO SupplierParts (price, sQuantity, supplier_id, part_id) VALUES
(120.50, 300, 1, 1),
(250.00, 150, 2, 2);

-- Insert sample data into myorder
INSERT INTO myorder (order_id, amount, order_date, arrival_date, part_id, supplier_id, warehouse_id) VALUES
(1, 50, '2025-04-10', '2025-04-15', 1, 1, 1),
(2, 30, '2025-04-20', '2025-04-25', 2, 2, 2);

-- Insert sample data into CostumerWarehousStorage
INSERT INTO CostumerWarehousStorage (start_date, end_date, warehouse_id, costumer_id) VALUES
('2025-01-01', '2025-06-01', 1, 1),
('2025-02-01', '2025-07-01', 2, 2);

-- Insert sample data into Train
INSERT INTO Train (train_id, model, year, last_check, next_check, warehouse_id) VALUES
(1, 'Model A', 2020, '2025-01-10', '2025-07-10', 1),
(2, 'Model B', 2021, '2025-02-15', '2025-08-15', 2);
