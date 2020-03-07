import serial
import csv
import time
import os
import json
import datetime

SERIAL_PORT = "COM7"
BAUD_RATE = 9600


write_dump = False;


# keeps track of receiving data
received = 0
total_data = 0
average_data = 0

# ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
date = datetime.date.today()

# paths
path = "./Data/"
dump_path_temp = "{0}dump-({1}).csv"
dump_path_finial = ""
temp_path = "{}Current.json".format(path)
start_dump = path + str(date) + "-"

# initialize the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

ser.write(str.encode("-"))  # "-" skips the fix for the GPS
time.sleep(1)
ser.write(str.encode("+"))  # telemetry module will not transmit data until "+" is sent

data_raw_dict = {"!!": "", "@@": "", "##": "", "%%": "", "$$": ""}

data_clean_dict = {"bme": {"temperature": "", "humidity": ""},

                   "ccs": {"co2": "", "tvoc": ""},

                   "baro": {"pressure": "", "altitude": ""},

                   "bno": {"quaternion": {"quat_w": "", "quat_x": "", "quat_y": "", "quat_z": ""},
                           "mag": {"mag_x": "", "mag_y": "", "mag_z": ""},
                           "gyroscope": {"gyro_x": "", "gyro_y": "", "gyro_z": ""},
                           "accelerometer": {"accel_x": "", "accel_y": "", "accel_z": ""}
                           },

                   "gps": {"time": {"hour": "", "min": "", "sec": "", "milli": "", "day": "", "month": "", "year": ""},
                           "connection": {"fix": "", "fix_quality": ""},
                           "positon": {"latitude": "", "lat": "", "longitude": "", "long": ""},
                           "info": {"speed": "", "angle": "", "altitude": "", "satellites": ""}
                           },
                   "data" : {"current": 0, "average": 0}
                   }


def calc_average():
    global total_data, average_data
    total_data += data_clean_dict["data"]["current"]
    average_data = total_data // received
    data_clean_dict["data"]["average"] = average_data
    print("average" + average_data + " current " + data_clean_dict["data"]["current"])


def apply_to_dict(key, data, offset):
    i = 0 + offset
    for sub_key in data_clean_dict[key].items():
        for sub_sub_key in data_clean_dict[key][sub_key[0]]:
            data_clean_dict[key][sub_key[0]][sub_sub_key] = data[i]
            i += 1


def proper_format(tag, incoming):
    data = incoming.replace(tag + ',', "").split(',')
    offset = 1

    if (tag == "!!"):
        data_clean_dict["bme"]["temperature"] = data[offset + 1];
        data_clean_dict["bme"]["humidity"] = data[offset + 2];
    elif (tag == "@@"):
        data_clean_dict["ccs"]["co2"] = data[offset + 1];
        data_clean_dict["ccs"]["tvoc"] = data[offset + 2];
    elif (tag == "##"):
        data_clean_dict["baro"]["pressure"] = data[offset + 1];
        data_clean_dict["baro"]["altitude"] = data[offset + 2];
    elif (tag == "%%"):
        apply_to_dict("bno", data, offset+1)
    elif (tag == "$$"):
        apply_to_dict("gps", data, offset+1)

    return data_clean_dict


if write_dump:
    current = 0
    while True:
        testName = dump_path_temp.format(start_dump, current)
        if os.path.exists(testName):
            current += 1
        else:
            dump_path_finial = testName
            break;

while True:
    incoming = ser.readline()
    incoming_raw = incoming.strip().decode("utf-8")
    incoming_split = incoming_raw.split(",")

    tag = incoming_split[0]

    received += 1
    data_clean_dict["data"]["current"] = len(incoming)
    #calc_average()
    
    print(incoming_split)

    if write_dump:
        with open(dump_path_finial, 'a') as dataDump:
            writer = csv.writer(dataDump)
            writer.writerow(incoming_split)
            dataDump.close()

    with open(temp_path, 'w') as dataTemp:
        if tag in data_raw_dict:
            json.dump(proper_format(tag, incoming_raw), dataTemp, default=json)
        dataTemp.close()

ser.close()