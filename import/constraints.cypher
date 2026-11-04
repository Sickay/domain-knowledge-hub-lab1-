// import/constraints.cypher
CREATE CONSTRAINT cnc_id_unique IF NOT EXISTS
FOR (m:CNC16K20F3) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT sensor_id_unique IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

CREATE INDEX sensor_temp_idx IF NOT EXISTS
FOR (s:Sensor) ON (s.temperature);

CREATE INDEX equipment_status_idx IF NOT EXISTS
FOR (e:IndustrialEquipment) ON (e.status);
