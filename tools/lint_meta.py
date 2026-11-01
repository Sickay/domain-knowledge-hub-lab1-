import os
import re
import sys
import glob

REQUIRED_FIELDS = ["id", "title", "author", "version", "date", "tags", "sensitivity"]
VALID_SENSITIVITY = ["public", "internal", "confidential"]
SEMVER_REGEX = r"^\d+\.\d+\.\d+$"
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


def parse_front_matter(content):
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    
    yaml_text = parts[1].strip()
    data = {}
    current_key = None
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if line.startswith("- ") and current_key:
            if not isinstance(data[current_key], list):
                data[current_key] = []
            data[current_key].append(line[2:].strip())
        elif ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            current_key = key
            if val:
                data[key] = val
            else:
                data[key] = []
                
    return data


def validate_file(filepath):
    errors = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    data = parse_front_matter(content)
    if data is None:
        return [f"{filepath}: Відсутній або пошкоджений YAML Front Matter (має починатися з '---')"]

    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            errors.append(f"{filepath}: Відсутнє обов'язкове поле '{field}'")

    if "version" in data and isinstance(data["version"], str):
        if not re.match(SEMVER_REGEX, data["version"]):
            errors.append(f"{filepath}: Некоректна версія '{data['version']}'. Очікується SemVer (наприклад 1.0.0)")

    if "date" in data and isinstance(data["date"], str):
        if not re.match(DATE_REGEX, data["date"]):
            errors.append(f"{filepath}: Некоректна дата '{data['date']}'. Очікується YYYY-MM-DD")

    if "sensitivity" in data and isinstance(data["sensitivity"], str):
        if data["sensitivity"] not in VALID_SENSITIVITY:
            errors.append(f"{filepath}: Некоректне значення sensitivity '{data['sensitivity']}'. Дозволені: {VALID_SENSITIVITY}")

    if "tags" in data:
        if not isinstance(data["tags"], list) or len(data["tags"]) == 0:
            errors.append(f"{filepath}: Поле 'tags' має бути непорожнім списком")

    return errors


def main():
    files = glob.glob("kb/*.md")
    if not files:
        print("Файли у папці kb/*.md не знайдені!")
        sys.exit(1)

    all_errors = []
    for filepath in files:
        errors = validate_file(filepath)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"[OK] {filepath}")

    if all_errors:
        print("\nВиявлено помилки валідації метаданих:")
        for err in all_errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("\nУсі файли знань успішно пройшли перевірку!")
        sys.exit(0)


if __name__ == "__main__":
    main()
