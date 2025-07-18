from flask import Flask, render_template_string
import serial
import struct

app = Flask(__name__)
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=2)

labels = [
    "PM1.0 (CF1)", "PM2.5 (CF1)", "PM10 (CF1)",
    "PM1.0 (ATM)", "PM2.5 (ATM)", "PM10 (ATM)",
    "0.3–0.5 μm", "0.5–1.0 μm", "1.0–2.5 μm",
    "2.5–5.0 μm", "5.0–10 μm", ">10 μm"
]

units = [
    "µg/m³", "µg/m³", "µg/m³",
    "µg/m³", "µg/m³", "µg/m³",
    "count/0.1L", "count/0.1L", "count/0.1L",
    "count/0.1L", "count/0.1L", "count/0.1L"
]

def read_pms1003():
    while True:
        if ser.read(1) == b'\x42':
            if ser.read(1) == b'\x4d':
                frame = ser.read(30)
                if len(frame) != 30:
                    continue
                data = struct.unpack('!HHHHHHHHHHHHHH', frame[:28])
                checksum = struct.unpack('!H', frame[28:30])[0]
                calc_checksum = 0x42 + 0x4D + sum(frame[:28])
                if checksum == (calc_checksum & 0xFFFF):
                    return data[:12]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PMS1003 Air Quality</title>
    <meta http-equiv="refresh" content="10">
    <link rel="icon" href="data:,">
    <style>
        body { font-family: sans-serif; padding: 1em; }
        table { border-collapse: collapse; margin-bottom: 2em; }
        th, td { border: 1px solid #666; padding: 0.5em; }

        .bar-container {
            display: flex;
            gap: 1em;
            align-items: flex-end;
            height: 200px;
            margin-top: 1em;
        }

        .bar {
            width: 60px;
            background-color: steelblue;
            text-align: center;
            color: white;
            font-weight: bold;
        }

        .bar-label {
            margin-top: 0.5em;
            text-align: center;
        }
    </style>
</head>
<body>
    <h2>Plantower PMS1003 Air Quality Readings</h2>

    <table>
        <tr>
            {% for label in labels %}
            <th>{{ label }}</th>
            {% endfor %}
        </tr>
        <tr>
            {% for value, unit in data %}
            <td>{{ value }} {{ unit }}</td>
            {% endfor %}
        </tr>
    </table>

    <h3>PM Concentration Bar Graph (ATM values)</h3>
    <div class="bar-container">
        {% set scale = [data[3][0], data[4][0], data[5][0]] %}
        {% set raw_max = scale | max %}
        {% set max_val = raw_max if raw_max > 50 else 50 %}
        {% set max_val = 1000 if max_val > 1000 else max_val %}
        {% set container_px = 200 %}

        {% for i in range(3) %}
            {% set height_px = (data[3+i][0] / max_val) * container_px %}
            <div style="height: {{ height_px|round(0, 'floor') }}px;"
                 class="bar"
                 title="{{ labels[3+i] }}: {{ data[3+i][0] }} µg/m³">
                {{ data[3+i][0] }}
            </div>
        {% endfor %}
    </div>

    <div class="bar-container">
        {% for i in range(3) %}
        <div class="bar-label">{{ labels[3+i].split()[0] }}</div>
        {% endfor %}
    </div>

    <p>Page auto-refreshes every 10 seconds.</p>
</body>
</html>
"""

@app.route("/")
def index():
    values = read_pms1003()
    table_data = list(zip(values, units))
    return render_template_string(HTML_TEMPLATE, labels=labels, data=table_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
