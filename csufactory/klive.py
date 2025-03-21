import os
import socket
import json
import datetime

def show(gds_filename, keep_position=True):
    """ Show GDS in klayout """
    #时间戳：
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not os.path.isfile(gds_filename):
        raise ValueError("{} does not exist".format(gds_filename))
    data = {
        "gds": os.path.abspath(gds_filename),
        "keep_position": keep_position,
    }
    data = json.dumps(data)
    try:
        conn = socket.create_connection(("127.0.0.1", 8082), timeout=0.5)
        data = data + "\n"
        data = data.encode() if hasattr(data, "encode") else data
        conn.sendall(data)
        conn.close()
        print(f"{timestamp} |INFO|show:8814-klive v0.3.3: Reloaded file: {gds_filename}")
    except socket.error:
        print("warning, could not connect to the klive server")
        pass
