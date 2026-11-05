// 1. Очищення бази 
MATCH (n) DETACH DELETE n;

// 2. Створення 15 ПЛК-контролерів 
UNWIND range(1, 15) AS i
CREATE (:PLCController {
  id: "PLC-" + substring("00" + toString(i), size(toString(i)))
});

// 3. Створення 35 верстатів ЧПК
UNWIND range(1, 35) AS i
CREATE (:CNC16K20F3:MachineTool:IndustrialEquipment {
  id: "CNC-" + substring("00" + toString(i), size(toString(i))),
  status: CASE WHEN i % 5 = 0 THEN "maintenance" ELSE "active" END,
  axisCount: 3 + (i % 3)
});

// 4. Створення 20 шпинделів 
UNWIND range(1, 20) AS i
CREATE (:Spindle {
  id: "SP-" + substring("00" + toString(i), size(toString(i))),
  status: CASE WHEN i % 7 = 0 THEN "overheated" ELSE "normal" END
});

// 5. Створення 35 датчиків 
UNWIND range(1, 35) AS i
CREATE (:Sensor {
  id: "TS-" + substring("00" + toString(i), size(toString(i))),
  temperature: 40.0 + (i * 1.5),
  pressure: 1.0 + (i * 0.1),
  vibration: 0.5 + (i * 0.1)
});

// -------------------------------------------------------------
// Створення ЗВ'ЯЗКІВ 
// -------------------------------------------------------------

// Зв'язки CONTROLS / IS_CONTROLLED_BY між ПЛК та верстатами 
MATCH (p:PLCController), (c:CNC16K20F3)
WHERE toInteger(substring(c.id, 4)) % 15 = toInteger(substring(p.id, 4)) % 15
CREATE (p)-[:CONTROLS {source: "SCADA_Config", confidence: 0.99, validFrom: "2026-01-01"}]->(c)
CREATE (c)-[:IS_CONTROLLED_BY {source: "SCADA_Config", confidence: 0.99, validFrom: "2026-01-01"}]->(p);

// Зв'язки HAS_SPINDLE між верстатами та шпинделями 
MATCH (c:CNC16K20F3), (sp:Spindle)
WHERE toInteger(substring(c.id, 4)) % 20 = toInteger(substring(sp.id, 3)) % 20
CREATE (c)-[:HAS_SPINDLE {source: "CAD_Assembly", confidence: 0.98, validFrom: "2026-01-01"}]->(sp);

// Зв'язки HAS_SENSOR між верстатами та датчиками 
MATCH (c:CNC16K20F3), (s:Sensor)
WHERE toInteger(substring(c.id, 4)) = toInteger(substring(s.id, 3))
CREATE (c)-[:HAS_SENSOR {source: "Wiring_Diagram", confidence: 0.95, validFrom: "2026-01-01"}]->(s);

// Зв'язки вимірювань MEASURES_TEMP 
MATCH (s:Sensor), (sp:Spindle)
WHERE toInteger(substring(s.id, 3)) % 20 = toInteger(substring(sp.id, 3)) % 20
CREATE (s)-[:MEASURES_TEMP {source: "Telemetry_Log", confidence: 0.92, validFrom: "2026-01-01"}]->(sp);

// Зв'язки вимірювань MEASURES_PRESSURE та MEASURES_VIBRATION 
MATCH (s:Sensor), (c:CNC16K20F3)
WHERE toInteger(substring(s.id, 3)) % 10 = toInteger(substring(c.id, 4)) % 10
CREATE (s)-[:MEASURES_PRESSURE {source: "Telemetry_Log", confidence: 0.91, validFrom: "2026-01-01"}]->(c)
CREATE (s)-[:MEASURES_VIBRATION {source: "Telemetry_Log", confidence: 0.94, validFrom: "2026-01-01"}]->(c);
