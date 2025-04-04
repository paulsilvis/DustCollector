# Python Project Naming Conventions

## 📁 Directories
- Use `snake_case`
- No spaces, hyphens, or uppercase letters
- Reflect logical grouping

**Examples:**
- `motor_drivers/`
- `limit_switches/`
- `sound_effects/`

---

## 🐍 Module Names (Filenames)
- Use `snake_case`
- Concise and descriptive

**Examples:**
- `actuator_base.py`
- `stepper_driver.py`
- `led_control.py`

---

## 🧱 Class Names
- Use `PascalCase` (CapWords)
- Singular nouns preferred

**Examples:**
- `LinearActuator`
- `MockSensor`
- `GateController`

---

## 🔧 Function & Method Names
- Use `snake_case`
- Verbs or verb phrases

**Examples:**
- `initialize_motor()`
- `open_gate()`
- `read_sensor_value()`

---

## 🔣 Variable Names
- Use `snake_case`
- Concise and self-descriptive

**Examples:**
- `gate_position`
- `sensor_triggered`
- `step_delay`

---

## 🧪 Constants
- Use `ALL_UPPERCASE_WITH_UNDERSCORES`

**Examples:**
- `MAX_CURRENT`
- `DEFAULT_TIMEOUT`
- `LED_PIN_GREEN`

---

## 🧪 Test Files
- Prefix with `test_`
- Same naming style as modules
- Keep in a `tests/` folder or alongside module

**Examples:**
- `test_gate_control.py`
- `test_sensor_mockup.py`

---

## ✅ Best Practices
- Be consistent
- Use meaningful names, not abbreviations unless widely known
- Prioritize clarity and readability
- Add docstrings and comments where needed

