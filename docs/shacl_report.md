# Звіт з валідації SHACL

## 1. SHACL-форми та обмеження (C1)
У файлі `shapes/shapes.ttl` описано 5 форм (`EquipmentShape`, `CNC16K20F3Shape`, `TemperatureSensorShape`, `PressureSensorShape`, `StatusPatternShape`), які містять понад 8 типів обмежень (`minCount`, `datatype`, `minInclusive`, `maxInclusive`, `pattern`).

## 2. Результати запуску pySHACL (C2, C3)
Валідацію виконано за допомогою бібліотеки `pySHACL`:
- **Еталонний граф (`data/kb.ttl`):** `Conforms: True` (порушень не виявлено, усі дані відповідають формам).
- **Дефектний граф:** Створено тестовий набір із навмисним дефектом (датчик температури зі значенням `150.0`, що перевищує максимально допустиме значення `maxInclusive 120.0`).
- **Результат валідації дефектного графа:** `Conforms: False`. Успішно виявлено порушення (`Validation Report: 1 result` у компоненті `MaxInclusiveConstraintComponent`).

## 3. Порівняння SHACL та OWL (C4)
OWL базується на припущенні відкритого світу (Open World Assumption, OWA) і призначений для логічного виведення нових фактів та семантичної класифікації. Натомість SHACL працює за припущенням закритого світу (Closed World Assumption, CWA) і використовується саме для перевірки цілісності (integrity constraints), структури, типів та діапазонів даних.
