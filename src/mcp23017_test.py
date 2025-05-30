import time
from mcp23017_in import MCP23017_in

def main():
    mcp = MCP23017_in()

    while True:
        active = []
        for i in range(16):
            if mcp.read_pin(i):
                active.append(str(i))
        if active:
            print("Pins HIGH:", ", ".join(active))
        else:
            print("No pins HIGH.")
        time.sleep(0.05)  # ~50 ms delay

if __name__ == "__main__":
    main()
