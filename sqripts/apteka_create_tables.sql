-- 1. Таблица suppliers (модель Supplier) :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
CREATE TABLE `suppliers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `CompName` VARCHAR(100) NOT NULL,
  `Address` VARCHAR(100) NOT NULL,
  `Number` VARCHAR(20) NOT NULL,
  `INN` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Таблица employees (модель Employee) :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
CREATE TABLE `employees` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `FName` VARCHAR(50) NOT NULL,
  `LName` VARCHAR(50) NOT NULL,
  `Number` VARCHAR(20) NOT NULL,
  `Position` VARCHAR(50) NOT NULL,
  `Login` VARCHAR(50) NOT NULL,
  `Pass` VARCHAR(255) NOT NULL,
  `DTB` DATE NOT NULL,
  `Admin` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Таблица medicines (модель Medicine) :contentReference[oaicite:4]{index=4}&#8203;:contentReference[oaicite:5]{index=5}
CREATE TABLE `medicines` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `MName` VARCHAR(100) NOT NULL,
  `Price` INT NOT NULL,
  `Count` INT NOT NULL,
  `Description` VARCHAR(255),
  `Category` VARCHAR(50),
  `BT` VARCHAR(50),
  `Supplier` INT,
  PRIMARY KEY (`id`),
  INDEX (`Supplier`),
  CONSTRAINT `fk_medicines_supplier`
    FOREIGN KEY (`Supplier`) REFERENCES `suppliers`(`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Таблица orders (модель Order) :contentReference[oaicite:6]{index=6}&#8203;:contentReference[oaicite:7]{index=7}
CREATE TABLE `orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `DateReg` DATE NOT NULL,
  `Amount` INT NOT NULL,
  `Status` TINYINT(1) NOT NULL,
  `Employee` INT NOT NULL,
  `Medicine` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX (`Employee`),
  INDEX (`Medicine`),
  CONSTRAINT `fk_orders_employee`
    FOREIGN KEY (`Employee`) REFERENCES `employees`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_medicine`
    FOREIGN KEY (`Medicine`) REFERENCES `medicines`(`id`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Таблица shipments (модель Shipment) :contentReference[oaicite:8]{index=8}&#8203;:contentReference[oaicite:9]{index=9}
CREATE TABLE `shipments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `DateReg` DATE NOT NULL,
  `Amount` INT NOT NULL,
  `Status` TINYINT(1) NOT NULL,
  `Supplier` INT NOT NULL,
  `Employee` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX (`Supplier`),
  INDEX (`Employee`),
  CONSTRAINT `fk_shipments_supplier`
    FOREIGN KEY (`Supplier`) REFERENCES `suppliers`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_shipments_employee`
    FOREIGN KEY (`Employee`) REFERENCES `employees`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Таблица shipmentitem (модель ShipmentItem) :contentReference[oaicite:10]{index=10}&#8203;:contentReference[oaicite:11]{index=11}
CREATE TABLE `shipmentitem` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Shipment` INT,
  `Medicine` INT,
  `Quantity` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX (`Shipment`),
  INDEX (`Medicine`),
  CONSTRAINT `fk_shipmentitem_shipment`
    FOREIGN KEY (`Shipment`) REFERENCES `shipments`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_shipmentitem_medicine`
    FOREIGN KEY (`Medicine`) REFERENCES `medicines`(`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
