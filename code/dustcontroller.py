import asyncio
from enum import Enum
from aioconsole import ainput
import time


# Enums for states
class MachineState(Enum):
    """Represents the possible states of a machine."""

    ON = "ON"
    OFF = "OFF"


class GateState(Enum):
    """Represents the possible states of a gate."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class OperatingState(Enum):
    """Represents the different operational states of a gate-machine system."""

    S0 = "MACHINE_OFF_GATE_CLOSED_MOTOR_OFF"
    S1 = "MACHINE_ON_GATE_OPEN_MOTOR_ON"
    S2 = "MACHINE_OFF_GATE_OPEN_MOTOR_ON_WAITING"


# Define the Timer
GLOBAL_TIMER = None
TIMEOUT = 10  # delay in seconds


# Motor control
def set_motor(state):
    """Sets the motor state and prints the change."""
    global Motor
    Motor = state
    print("Motor is ", state)


class Timer:
    """Manages timing operations for gate control."""

    def __init__(self):
        self.timer = None

    def clear_timer(self):
        """Clears the timer."""
        if self.timer:
            print("Timer cleared")
        self.timer = None

    def set_timer(self):
        """Sets the timer to the current time."""
        self.timer = time.time()
        print("Timer set")

    def check_timer_expired(self):
        """Checks if the timer has expired."""
        if self.timer and (time.time() - self.timer >= TIMEOUT):
            self.clear_timer()
            return True
        return False


class Sensor:
    """Base class for sensors."""

    def __init__(self):
        pass

    def read(self):
        """Should be overridden in subclasses."""
        print("\n\n\n\n****** should never get here")
        return self.MachineState.OFF


class CurrentSensor(Sensor):
    """Represents a current sensor for detecting machine state."""

    def __init__(self, id):
        super().__init__()
        self.id = id
        self.state = MachineState.OFF

    def read(self):
        """Returns the current state of the sensor."""
        return self.state


class Gate:
    """Represents a gate in the system."""

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.state = GateState.CLOSED
        self.op_state = OperatingState.S0
        self.machine = Machine(self, CurrentSensor(id))
        self.timer = Timer()

    def close(self):
        """Closes the gate and updates the state."""
        self.state = GateState.CLOSED
        print(f"Gate {self.name} closed")

    def open(self):
        """Opens the gate and updates the state."""
        self.state = GateState.OPEN
        print(f"Gate {self.name} opened")


class Machine:
    """Represents a machine associated with a gate and sensor."""

    def __init__(self, gate, sensor):
        self.gate = gate
        self.sensor = sensor
        self.state = MachineState.OFF

    def get_state(self):
        """Updates and returns the machine state based on sensor reading."""
        self.state = self.sensor.read()
        return self.state


# Initialization
Gates = [
    Gate(0, "saw"),
    Gate(1, "drillpress"),
    Gate(2, "lathe"),
    Gate(3, "router"),
]
print("Gates: ", Gates)

Motor = MachineState.OFF
set_motor(MachineState.OFF)

for g in Gates:
    g.close()


async def gateController():
    """Main loop controlling the gate operations based on machine states."""
    print("starting main loop of gate controller")
    while True:
        # Update all machine states
        for g in Gates:
            g.machine.get_state()

        # Run gate control state machine for each gate
        for g in Gates:
            if g.op_state == OperatingState.S0:
                if g.machine.state == MachineState.ON:
                    g.op_state = OperatingState.S1
                    print("g", g.id, "going to S1")
                    g.open()
                    set_motor(MachineState.ON)
                    g.timer.clear_timer()
            elif g.op_state == OperatingState.S1:
                if g.machine.state == MachineState.OFF:
                    g.op_state = OperatingState.S2
                    print("g", g.id, "going to S2")
                    g.timer.set_timer()
                else:
                    g.timer.clear_timer()
            elif g.op_state == OperatingState.S2:
                if g.machine.state == MachineState.ON:
                    g.op_state = OperatingState.S1
                    g.timer.clear_timer()
                elif g.timer.check_timer_expired():
                    g.close()
                    g.op_state = OperatingState.S0
                    print("g", g.id, "going to S0")
            else:
                raise ValueError(f"Invalid state {g.op_state}")

        stop_motor = True
        for g in Gates:
            if g.state == GateState.OPEN:
                stop_motor = False

        if stop_motor and Motor == MachineState.ON:
            print("no gates open, killing motor")
            set_motor(MachineState.OFF)  # Turn off motor directly here

        await asyncio.sleep(1)  # Add delay for simulation


async def read_states():
    """Simulate machine state changes, display current gate states."""
    while True:
        line = await ainput()
        parts = line.split()

        if len(parts) and parts[0] == "?":
            for g in Gates:
                print(
                    "id",
                    g.id,
                    "op_state",
                    g.op_state,
                    "machine",
                    g.machine.state,
                    "gate",
                    g.state,
                )
            continue
        channel = 0
        value = 0
        if len(parts) != 2:
            print("try again")
        else:
            try:
                channel = int(parts[0])
                value = int(parts[1])
                if channel < 0 or channel >= len(Gates):
                    print("invalid channel")
                    continue
            except ValueError:
                print("Invalid input. Please enter two integers")
                continue
            if value == 0:
                Gates[channel].machine.sensor.state = MachineState.OFF
            else:
                Gates[channel].machine.sensor.state = MachineState.ON


async def main():
    """Runs the gate controller and input reader concurrently."""
    await asyncio.gather(read_states(), gateController())


# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())
