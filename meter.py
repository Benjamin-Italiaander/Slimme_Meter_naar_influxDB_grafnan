
import serial
import sys
import datetime
import pytz
from influxdb import InfluxDBClient
from datetime import datetime
import influxdb
from influxdb.line_protocol import _get_unicode, quote_ident, _is_float, text_type
import socket


current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# connect to influxdb 
client = InfluxDBClient(host='localhost', port=8086, username='power', password='energieAAA')
client.switch_database('power')

def show_error():
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
#    print("Fout type: %s" % ft)
#    print("Fout waarde: %s" % fv)
    return



# Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20
ser.port = "/dev/ttyUSB0"

# Open COM port
try:
    ser.open()
except:
    sys.exit("Fout bij het openen van %s. Programma afgebroken." % ser.name)


# Initialize
# stack is mijn list met de 26 regeltjes.
p1_teller = 0
stack = []

while p1_teller < 100:
    p1_line = ''
# Read 1 line
    try:
        p1_raw = ser.readline()
    except:
        sys.exit(
            "Seriele poort %s kan niet gelezen worden. Programma afgebroken." % ser.name)
    p1_str=str(p1_raw, "utf-8")
    p1_line = p1_str.strip()
    stack.append(p1_line)
    p1_teller = p1_teller + 1

stack_teller=0
while stack_teller < 75:

    if stack[stack_teller][0:9] == "1-0:1.8.1":
        geleverd_tarief_1 = stack[stack_teller][10:20]
    elif stack[stack_teller][0:9] == "1-0:1.8.2":
       geleverd_tarief_2 = stack[stack_teller][10:20]
    elif stack[stack_teller][0:10] == "1-0:32.7.0":
        vl1 = stack[stack_teller][11:16]
    elif stack[stack_teller][0:10] == "1-0:52.7.0":
        vl2 = stack[stack_teller][11:16]
    elif stack[stack_teller][0:10] == "1-0:72.7.0":
        vl3 = stack[stack_teller][11:16]
    elif stack[stack_teller][0:9] == "1-0:1.7.0":
        actueel_verbruik = stack[stack_teller][10:16]
    elif stack[stack_teller][0:9] == "1-0:2.7.0":
        actueel_terug = stack[stack_teller][10:16]


    elif stack[stack_teller][0:8] == "1-0:21.7":
        vermogen_verbruik_l1 = stack[stack_teller][11:17]
    elif stack[stack_teller][0:8] == "1-0:22.7":
        vermogen_terug_l1 =  stack[stack_teller]

    elif stack[stack_teller][0:9] == "1-0:32.36":
        spannings_piek_l1 =  stack[stack_teller][12:17]

    elif stack[stack_teller][0:9] == "1-0:52.36":
        spannings_piek_l2 =  stack[stack_teller][12:17]

    elif stack[stack_teller][0:9] == "1-0:72.36":
        spannings_piek_l3 =  stack[stack_teller][12:17]

    elif stack[stack_teller][0:8] == "1-0:41.7":
        vermogen_verbruik_l2 = stack[stack_teller][11:17] 

    elif stack[stack_teller][0:8] == "1-0:42.7":
        vermogen_terug_l2 =  stack[stack_teller]

    elif stack[stack_teller][0:8] == "1-0:61.7":
        vermogen_verbruik_l3 = stack[stack_teller][11:17]
    elif stack[stack_teller][0:8] == "1-0:62.7":
        vermogen_terug_l3 =  stack[stack_teller]

    elif stack[stack_teller][0:9] == "1-0:32.32":
        spannings_dip_l1 = stack[stack_teller][12:17]

    elif stack[stack_teller][0:9] == "1-0:52.32":
        spannings_dip_l2 = stack[stack_teller][12:17]

    elif stack[stack_teller][0:9] == "1-0:72.32":
        spannings_dip_l3 = stack[stack_teller][12:17]

    #elif stack[stack_teller][0:8] == "1-0:31.7":
    #    print ("Stroom fase 1", stack[stack_teller])

    #elif stack[stack_teller][0:8] == "1-0:51.7":
    #    print ("Stroom fase 2", stack[stack_teller])


    #elif stack[stack_teller][0:8] == "1-0:71.7":
    #    print ("Stroom fase 3", stack[stack_teller])

    stack_teller = stack_teller + 1




actueel_verbruik = int(str(actueel_verbruik).replace('.', ''))

geleverd_tarief_1 = int(str(geleverd_tarief_1).replace('.', ''))
geleverd_tarief_2 = int(str(geleverd_tarief_2).replace('.', ''))

geleverd_tarief_1 = geleverd_tarief_1 + 1

vermogen_verbruik_l1 = int(str(vermogen_verbruik_l1).replace('.', ''))
vermogen_verbruik_l2 = int(str(vermogen_verbruik_l2).replace('.', ''))
vermogen_verbruik_l3 = int(str(vermogen_verbruik_l3).replace('.', ''))

opgetelde_vermogen = (vermogen_verbruik_l1 + vermogen_verbruik_l2 + vermogen_verbruik_l3)
vl1 = float(vl1)
vl2 = float(vl2)
vl3 = float(vl3)


json_body = [
    {
        "measurement": "energie",
        "time": current_time,
        "fields": {
            "Spanning Fase 1": float(vl1),
            "Spanning Fase 2": float(vl2),
            "Spanning Fase 3": float(vl3),
            "Spannings piek Fase 1": int(spannings_piek_l1),
            "Spannings piek Fase 2": int(spannings_piek_l2),
            "Spannings piek Fase 3": int(spannings_piek_l3),
            "Spannings dip Fase 1": int(spannings_dip_l1),
            "Spannings dip Fase 2": int(spannings_dip_l2),
            "Spannings dip Fase 3": int(spannings_dip_l3),
            "Geleverd tarief 1": int(geleverd_tarief_1),
            "Geleverd tarief 2": int(geleverd_tarief_2),
            "verbruik totaal": int(actueel_verbruik),
            "fases opgeteld": int(opgetelde_vermogen),
            "Vermogen verbruikt Fase 1": int(vermogen_verbruik_l1),
            "Vermogen verbruikt Fase 2": int(vermogen_verbruik_l2),
            "Vermogen verbruikt Fase 3": int(vermogen_verbruik_l3)
        }
    }
]
#print (json_body)
client.write_points(json_body)



