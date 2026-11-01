from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IndustrialEquipment:
    id: str
    name: str
    status: str = "active"
    sensitivity: str = "internal"


@dataclass
class MachineTool(IndustrialEquipment):
    max_rpm: int = 3000
    current_rpm: int = 0
    spindle_temp: float = 25.0
    lubrication_level: str = "normal"


@dataclass
class CNC16K20F3(MachineTool):
    model_type: str = "Lathe"
    axis_count: int = 2
    coolant_flow: str = "normal"


@dataclass
class Sensor(IndustrialEquipment):
    sensor_type: str = "generic"
    calibration_days: int = 0
    accuracy_class: float = 0.5


@dataclass
class TemperatureSensor(Sensor):
    sensor_type: str = "thermocouple"
    last_calibrated_days: int = 30


# 10 екземплярів для тестів
instances = [
    CNC16K20F3(id="CNC-01", name="Верстат 16К20Ф3 Цех №1", max_rpm=3000, current_rpm=1500, spindle_temp=65.0, lubrication_level="normal", coolant_flow="normal"),
    CNC16K20F3(id="CNC-02", name="Верстат 16К20Ф3 Цех №2", max_rpm=3000, current_rpm=2800, spindle_temp=78.5, lubrication_level="normal", coolant_flow="normal"),  # Перегрів!
    CNC16K20F3(id="CNC-03", name="Верстат резервний", max_rpm=2500, current_rpm=0, spindle_temp=22.0, lubrication_level="low", coolant_flow="normal"),       # Низьке мастило!
    CNC16K20F3(id="CNC-04", name="Токарний автомат 4", max_rpm=3000, current_rpm=1200, spindle_temp=40.0, lubrication_level="normal", coolant_flow="low"),      # Низька ЗОР!
    TemperatureSensor(id="TS-01", name="Термопара шпинделя 1", sensor_type="thermocouple", calibration_days=45, accuracy_class=0.2),
    TemperatureSensor(id="TS-02", name="Термопара гідростанції", sensor_type="thermocouple", calibration_days=190, accuracy_class=0.5), # Прострочено калібрування!
    Sensor(id="PR-01", name="Датчик тиску повітря", sensor_type="pneumatic", calibration_days=30, accuracy_class=0.5),
    Sensor(id="VB-01", name="Вибродатчик головний", sensor_type="vibration", calibration_days=10, accuracy_class=0.1),
    CNC16K20F3(id="CNC-05", name="Верстат випробувальний", max_rpm=3000, current_rpm=500, spindle_temp=30.0, lubrication_level="normal", coolant_flow="normal"),
    TemperatureSensor(id="TS-03", name="Термопара щитової", sensor_type="thermocouple", calibration_days=60, accuracy_class=0.5)
]


def evaluate_rule_with_frames(machine: CNC16K20F3):
    """Демонстрація зв'язку правил та слотів фрейму"""
    actions = []
    # RULE-002: spindle_temp > 75
    if machine.spindle_temp > 75.0:
        actions.append("EMERGENCY_STOP: ТЕМПЕРАТУРА ШПИНДЕЛЯ ПЕРЕВИЩУЄ 75°C")
    # RULE-001: lubrication_level == 'low'
    if machine.lubrication_level == "low":
        actions.append("MACHINE_BLOCKED: НИЗЬКИЙ РІВЕНЬ МАС ТИЛА")
    return actions


if __name__ == "__main__":
    print(f"Створено фреймів: 5 класів, ініціалізовано екземплярів: {len(instances)}")
    for inst in instances:
        if isinstance(inst, CNC16K20F3):
            res = evaluate_rule_with_frames(inst)
            if res:
                print(f"Об'єкт {inst.id} ({inst.name}): спрацювали правила -> {res}")
