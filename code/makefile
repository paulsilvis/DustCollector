# List all the Python files you want to check here
PY_FILES = \
    timer.py \
    hardware/leddriver.py \
    hardware/relaydriver.py \
    hardware/switchdriver.py \
    hardware/switchdriver2.py \
    hardware/stepperdriver.py \
    hardware/steppercontroller.py \
    sensor.py \
    gate.py \
    tool.py \
    actuator.py \
    dustcontroller.py \
    mock/currentsensor.py hardware/currentsensor.py \
    mock/servo.py hardware/servo.py \
    mock/linearactuator.py hardware/linearactuator.py

HW_FILES = \
    timer.py \
    hardware/leddriver.py \
    hardware/relaydriver.py \
    hardware/switchdriver.py \
    hardware/switchdriver2.py \
    hardware/stepperdriver.py \
    hardware/steppercontroller.py \
    sensor.py \
    gate.py \
    tool.py \
    actuator.py \

# Declare 'check' as a phony target (no actual file named 'check')
.PHONY: check
.PHONY: listings
.PHONY: blackcheck
.PHONY: classes

# The default rule is 'check'
check:
	pycodestyle $(PY_FILES)
	flake8 $(PY_FILES)
	black -l 79 --check $(PY_FILES)



# Optionally, you can make 'all' point to 'check'
all: check

files:
	echo $(PY_FILES)

black:
	black -l 79 $(PY_FILES)

listings:
	cat -n $1 | lpr -p $(PY_FILES)

static:
	mypy $(PY_FILES)
	
	
classes:
	pyreverse -o png $(PY_FILES)
    
