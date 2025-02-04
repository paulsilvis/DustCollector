# List all the Python files you want to check here
PY_FILES = \
    timer.py \
    sensor.py \
    gate.py \
    tool.py \
    actuator.py \
    mock/currentsensor.py hardware/currentsensor.py \
    mock/servo.py hardware/servo.py
    
    
    
# Declare 'check' as a phony target (no actual file named 'check')
.PHONY: check
.PHONY: listings
.PHONY: blackcheck

# The default rule is 'check'
check: 
	pycodestyle $(PY_FILES)
	flake8 $(PY_FILES)
	black --check $(PY_FILES)	
	


# Optionally, you can make 'all' point to 'check'
all: check
	
black:
	black $(PY_FILES)

listings:
	cat -n $1 | lpr -p $(PY_FILES)
	

