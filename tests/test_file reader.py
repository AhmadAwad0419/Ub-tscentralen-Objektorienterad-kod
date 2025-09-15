import sys
import os
import threading
import queue
from itertools import islice

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.file_reader import FileReader
from tests.test_path import get_random_drone_id

test_drone_id = get_random_drone_id()

def file_reader_thread(file_reader, drone_id, file_type, data_queue):
    """
    Funktion som körs i en egen tråd för att läsa en fil
    och placera varje rad i en kö.
    """
    print(f"Startar tråd för att läsa {file_type} för ubåt {drone_id}")

    # Ändra till None för att läsa alla rader i filerna
    lines_to_read = 10
    
    if file_type == 'movements':
        # Anropar generatorn för rörelser
        for command, value in islice(file_reader.load_movements(drone_id), lines_to_read):
            if command and value is not None:
                data_queue.put((file_type, command, value))
    
    elif file_type == 'sensors':
        # Anropar generatorn för sensordata
        for line in islice(file_reader.load_sensor_data(drone_id), lines_to_read):
            if line is not None:
                data_queue.put((file_type, line))
    
    # Signalerar att tråden är klar
    data_queue.put(None)
    print(f"Tråden för {file_type} är klar.")

if __name__ == "__main__":
    reader = FileReader()
    
    # Skapa en trådsäker kö för att dela data
    data_queue = queue.Queue()
    
    # Skapa trådarna för varje filinläsning
    movement_thread = threading.Thread(
        target=file_reader_thread,
        args=(reader, test_drone_id, 'movements', data_queue)
    )
    
    sensor_thread = threading.Thread(
        target=file_reader_thread,
        args=(reader, test_drone_id, 'sensors', data_queue)
    )
    
    # Starta trådarna
    movement_thread.start()
    sensor_thread.start()
    
    finished_threads = 0
    
    # Konsument-loop i huvudtråden
    while finished_threads < 2:
        # Hämta data från kön
        data = data_queue.get()
        
        if data is None:
            finished_threads += 1
            continue
        
        # Bearbeta datan beroende på typ
        file_type = data[0]
        if file_type == 'movements':
            command, value = data[1], data[2]
            print(f"Bearbetar rörelse: Command={command}, Value={value}")
        
        elif file_type == 'sensors':
            line = data[1]
            print(f"Bearbetar sensordata: Line={line}")
        
        # Säger till kön att vi är klara med en uppgift
        data_queue.task_done()
    
    print("\nAlla trådar är klara och all data har bearbetats.")


