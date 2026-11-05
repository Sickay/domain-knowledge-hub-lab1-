// ==========================================
// Аналітичні запити Cypher
// ==========================================

// 1. Пошук усіх датчиків та шпинделів, пов'язаних із конкретним верстатом
MATCH (c:CNC16K20F3 {id: "CNC-001"})-[:HAS_SPINDLE]->(sp:Spindle)
MATCH (c)-[:HAS_SENSOR]->(s:Sensor)
RETURN c.id AS CNC, sp.id AS Spindle, collect(s.id) AS Sensors;


// 2. Аналіз шляхів змінної довжини (Variable-length paths) від ПЛК до датчиків через обладнання
MATCH path = (p:PLCController)-[:CONTROLS]->(e:IndustrialEquipment)-[:HAS_SENSOR]->(s:Sensor)
RETURN path
LIMIT 10;


// 3. Знаходження найкоротшого шляху між ПЛК та конкретним датчиком (shortestPath)
MATCH p = shortestPath((plc:PLCController {id: "PLC-001"})-[:CONTROLS*..3]-(s:Sensor {id: "TS-001"}))
RETURN p;


// 4. Агрегація та статистика температур: середнє, максимальне та мінімальне значення по датчиках
MATCH (s:Sensor)
RETURN avg(s.temperature) AS avgTemp, max(s.temperature) AS maxTemp, min(s.temperature) AS minTemp;


// 5. Пошук верстатів, які перебувають у стані "maintenance" та керовані певними ПЛК
MATCH (p:PLCController)-[:CONTROLS]->(c:CNC16K20F3 {status: "maintenance"})
RETURN p.id AS PLC, c.id AS CNC, c.axisCount AS Axes;


// 6. Аналіз метаданих походження (Provenance): перевірка джерел та коефіцієнтів достовірності (confidence)
MATCH (c:CNC16K20F3)-[r:HAS_SPINDLE]->(sp:Spindle)
RETURN c.id AS CNC, sp.id AS Spindle, r.source AS Source, r.confidence AS Confidence, r.validFrom AS ValidFrom
LIMIT 5;


// 7. Знаходження «перевантажених» або критичних датчиків за значенням вібрації та тиску
MATCH (s:Sensor)
WHERE s.vibration > 1.5 OR s.pressure > 2.0
RETURN s.id AS SensorID, s.vibration AS Vibration, s.pressure AS Pressure;


// 8. Підрахунок кількості різних типів зв'язків у базі даних (структурний аналіз графа)
MATCH ()-[r]->()
RETURN type(r) AS RelationshipType, count(r) AS Count;
