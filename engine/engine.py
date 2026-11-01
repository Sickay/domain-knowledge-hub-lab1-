class RuleEngine:
    def __init__(self):
        self.rules = []
        self.log = []

    def add_rule(self, rule_id, condition_func, action_func, priority=1):
        self.rules.append({
            "id": rule_id,
            "condition": condition_func,
            "action": action_func,
            "priority": priority
        })
        # Сортування за пріоритетом (стратегія конфліктів: найбільший пріоритет перший)
        self.rules.sort(key=lambda x: x["priority"], reverse=True)

    def run(self, facts):
        triggered_rules = []
        working_memory = dict(facts)
        
        fired = True
        while fired:
            fired = False
            for r in self.rules:
                if r["id"] not in triggered_rules:
                    if r["condition"](working_memory):
                        r["action"](working_memory)
                        triggered_rules.append(r["id"])
                        fired = True
                        break # Повернення до початку циклу висновку
        return working_memory, triggered_rules
