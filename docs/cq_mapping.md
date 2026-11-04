# Мапування компетентнісних питань та графової схеми

## 1. Опис міток вузлів та типів зв'язків
Схема містить 6 міток:
- `IndustrialEquipment` (загальний клас обладнання)
- `MachineTool` (верстати)
- `CNC16K20F3` (модель верстата ЧПК)
- `Spindle` (шпиндель)
- `Sensor` (датчики)
- `PLCController` (контролер ПЛК)

Типи зв'язків (8 штук):
1. `IS_SUBCLASS_OF` — ієрархія класів обладнання
2. `CONTROLS` — керування
3. `IS_CONTROLLED_BY` — зворотний зв'язок керування
4. `HAS_SPINDLE` — наявність шпинделя
5. `HAS_SENSOR` — підключення датчика
6. `MEASURES_TEMP` — вимірювання температури
7. `MEASURES_PRESSURE` — вимірювання тиску
8. `MEASURES_VIBRATION` — вимірювання вібрації

## 2. Компетентнісні питання (CQ) та шаблони Cypher-шляхів
1. **CQ1:** Який статус має конкретний верстат за його ID?
   - *Cypher:* `MATCH (m:CNC16K20F3 {id: $id}) RETURN m.status`
2. **CQ2:** Який ПЛК керує певним промисловим обладнанням?
   - *Cypher:* `MATCH (e:IndustrialEquipment {id: $id})-[:IS_CONTROLLED_BY]->(plc:PLCController) RETURN plc.id`
3. **CQ3:** Які шпинделі перебувають у стані перегріву (`overheated`)?
   - *Cypher:* `MATCH (s:Spindle {status: "overheated"}) RETURN s.id`
4. **CQ4:** Які датчики температури фіксують критичні значення ($>70^\circ\text{C}$)?
   - *Cypher:* `MATCH (ts:Sensor) WHERE ts.temperature > 70.0 RETURN ts.id, ts.temperature`
5. **CQ5:** Які верстати підпорядковані певній системі ПЛК через контролер?
   - *Cypher:* `MATCH (m:MachineTool)-[:IS_CONTROLLED_BY]->(p:PLCController {id: $plcId}) RETURN m.id`
6. **CQ6:** Яка середня температура зафіксована датчиками температури у системі?
   - *Cypher:* `MATCH (ts:Sensor) RETURN avg(ts.temperature) AS avgTemp`
7. **CQ7:** Яке обладнання пов'язане з датчиками вібрації, що мають перевищення норми ($>3.0$)?
   - *Cypher:* `MATCH (m:MachineTool)-[:HAS_SENSOR]->(vs:Sensor) WHERE vs.vibration > 3.0 RETURN m.id, vs.vibration`
8. **CQ8:** Яка структура ієрархії обладнання за допомогою шляхів змінної довжини?
   - *Cypher:* `MATCH path = (e:IndustrialEquipment)-[:IS_SUBCLASS_OF*1..2]->(sub:IndustrialEquipment) RETURN path`

## 3. Властивості походження на зв'язках
Для забезпечення простежуваності на кожному ребрі графа задаються властивості походження:
- `source`: джерело даних (наприклад, `"SCADA_Log_2026"`)
- `confidence`: рівень довіри (float, наприклад, `0.99`)
- `validFrom`: дата початку дії (string/datetime)

## 4. Порівняльна таблиця (RDF/OWL vs Neo4j LPG)
| Критерій порівняння | Онтологія (ЛР 7, RDF/OWL) | Графова база знань (ЛР 9, Neo4j LPG) |
| :--- | :--- | :--- |
| **Сутності моделі** | Класи та екземпляри | Метки вузлів та екземпляри вузлів |
| **Зв'язки** | Об'єктні властивості (тріплети) | Напрямлені ребра з типами |
| **Атрибути** | Властивості даних (Datatype Properties) | Властивості вузлів і ребер |
| **Припущення світу** | Відкритий світ (OWA) | Закритий світ (CWA) |
| **Механізм виведення** | Логічне моделювання та дедукція | Обхід графа та алгоритми шляхів (Cypher) |
