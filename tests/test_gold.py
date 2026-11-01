import pytest
from engine.engine import RuleEngine


@pytest.fixture
def standard_engine():
    engine = RuleEngine()
    
    # RULE-001 (Високий пріоритет)
    engine.add_rule(
        "RULE-001",
        lambda f: f.get("lubrication_level") == "low",
        lambda f: f.update({"status": "blocked", "error": "Low lubrication"}),
        priority=10
    )
    
    # RULE-002 (Високий пріоритет)
    engine.add_rule(
        "RULE-002",
        lambda f: f.get("spindle_temp", 25) > 75,
        lambda f: f.update({"status": "emergency_stop", "cooling": "max"}),
        priority=10
    )
    
    # RULE-003 (Середній пріоритет)
    engine.add_rule(
        "RULE-003",
        lambda f: f.get("air_pressure", 0.55) < 0.45 or f.get("air_pressure", 0.55) > 0.65,
        lambda f: f.update({"pneumatic_alert": True, "operation_allowed": False}),
        priority=5
    )
    
    # RULE-004 (Середній пріоритет)
    engine.add_rule(
        "RULE-004",
        lambda f: f.get("coolant_flow", "normal") == "low",
        lambda f: f.update({"feed_modifier": 0.5, "warning": "Low coolant"}),
        priority=5
    )
    
    return engine


# 1. Позитивні тести (стандартні кейси)
def val_test_1(standard_engine):
    mem, chain = standard_engine.run({"lubrication_level": "low"})
    assert mem.get("status") == "blocked"
    assert "RULE-001" in chain

def val_test_2(standard_engine):
    mem, chain = standard_engine.run({"spindle_temp": 80.0})
    assert mem.get("status") == "emergency_stop"
    assert "RULE-002" in chain

def val_test_3(standard_engine):
    mem, chain = standard_engine.run({"air_pressure": 0.40})
    assert mem.get("pneumatic_alert") is True

def val_test_4(standard_engine):
    mem, chain = standard_engine.run({"coolant_flow": "low"})
    assert mem.get("feed_modifier") == 0.5

def val_test_5(standard_engine):
    mem, chain = standard_engine.run({"lubrication_level": "low", "spindle_temp": 80.0})
    assert "RULE-001" in chain
    assert "RULE-002" in chain


# 2. Граничні тести (Boundary tests - $\ge 3$)
def val_test_6_boundary_temp(standard_engine):
    # Ровно на межі 75.0 (не повинно спрацьовувати за умовою > 75)
    mem, chain = standard_engine.run({"spindle_temp": 75.0})
    assert "RULE-002" not in chain

def val_test_7_boundary_temp_over(standard_engine):
    # Одразу за межею 75.1 (має спрацювати)
    mem, chain = standard_engine.run({"spindle_temp": 75.1})
    assert "RULE-002" in chain

def val_test_8_boundary_pressure(standard_engine):
    # Ровно в межах номи 0.50 (не спрацьовує)
    mem, chain = standard_engine.run({"air_pressure": 0.50})
    assert "pneumatic_alert" not in chain


# 3. Негативні тести / Жодне правило не спрацьовує ($\ge 2$)
def val_test_9_negative_normal_state(standard_engine):
    mem, chain = standard_engine.run({"lubrication_level": "normal", "spindle_temp": 40.0, "air_pressure": 0.55})
    assert len(chain) == 0

def val_test_10_negative_empty_facts(standard_engine):
    mem, chain = standard_engine.run({})
    assert len(chain) == 0


# 4. Додаткові тестові випадки до 15+
def val_test_11(standard_engine):
    mem, chain = standard_engine.run({"lubrication_level": "normal", "spindle_temp": 76.0})
    assert "RULE-002" in chain

def val_test_12(standard_engine):
    mem, chain = standard_engine.run({"air_pressure": 0.70})
    assert mem.get("operation_allowed") is False

def val_test_13(standard_engine):
    mem, chain = standard_engine.run({"coolant_flow": "low", "air_pressure": 0.40})
    assert "RULE-004" in chain
    assert "RULE-003" in chain

def val_test_14(standard_engine):
    mem, chain = standard_engine.run({"lubrication_level": "low", "coolant_flow": "low"})
    assert "RULE-001" in chain
    assert "RULE-004" in chain

def val_test_15(standard_engine):
    mem, chain = standard_engine.run({"spindle_temp": 30.0, "lubrication_level": "normal"})
    assert len(chain) == 0
