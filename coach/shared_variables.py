import threading
import time
import pandas as pd

connection_state = 3 #0 connecting, 1 connected, 2 disconnecting, 3 disconnected
connection_lock = threading.RLock()
command = 0#0 do nothing, 1 get shot data, 2 get suggestion
command_lock = threading.RLock()
data_columns = ['int_ax', 'ax_min', 'ax_max', 'int_ay', 'ay_min', \
                'ay_max', 'int_az', 'az_min', 'az_max', 'gyr_x_final', \
                'gyr_x_min', 'gyr_x_max', 'gyr_y_min', 'gyr_y_max', \
                'gyr_y_final', 'gyr_z_min', 'gyr_z_max', 'gyr_z_final', \
                'made','suggestion'] 
motion_data = pd.DataFrame([], columns = data_columns)
motion_data_lock = threading.RLock()
speaker = 0
speaker_lock = threading.RLock()
continue_variable = True
connection_tries = 10
shots = 0
makes = 0