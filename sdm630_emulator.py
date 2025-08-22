import paho.mqtt.client as mqtt
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.server.sync import StartTcpServer
from pymodbus.payload import BinaryPayloadBuilder, Endian
import threading

# Speicher für Modbus-Register (Input Register Bereich)
store = ModbusSlaveContext(
    ir=ModbusSequentialDataBlock(0, [0]*200),  # Input Registers
    zero_mode=True
)
context = ModbusServerContext(slaves=store, single=True)

def set_float(context, address, value):
    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
    builder.add_32bit_float(value)
    registers = builder.to_registers()
    context[0].setValues(4, address, registers)  # 4 = Input Register

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        value = float(msg.payload.decode())
        set_float(context, 52, value)  # SDM630 Active Power
        print(f"MQTT -> Modbus: {value} W geschrieben in Register 52")
    except Exception as e:
        print("Fehler MQTT Payload:", e)

def mqtt_loop():
    client = mqtt.Client()
    client.connect("core-mosquitto", 1883, 60)
    client.subscribe("homeassistant/sensor/go_econtroller_910332_grid_power/state")
    client.on_message = on_message
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

# Modbus Server starten
print("Starte SDM630 Emulator auf Port 5020...")
StartTcpServer(context, address=("0.0.0.0", 5020))