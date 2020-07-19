data = ''

#overload print
def print(message):
    global data
    data += message
    sys.stdout.write(message)

class MyManagerListener(ManagerListener):
    def on_discovery_change(self, manager, enabled):
        print('Discovery %s.' % ('started' if enabled else 'stopped'))
        if not enabled:
            print()
    def on_node_discovered(self, manager, node):
        print('New device discovered: %s.' % (node.get_name()))

class MyNodeListener(NodeListener):
    def on_connect(self, node):
        print('Device %s connected.' % (node.get_name()))
    def on_disconnect(self, node, unexpected=False):
        print('Device %s disconnected%s.' % \
            (node.get_name(), ' unexpectedly' if unexpected else ''))
        if unexpected:
            # Exiting.
            print('\nExiting...\n')
            sys.exit(0)

class MyFeatureListener(FeatureListener):
    notifications = 0
    def on_update(self, feature, sample):
        if self._notifications < notifications:
            self._notifications += 1
            print(feature)

def get_motion():

    #creating variables
    global continue_variable
    global speaker
    global speaker_lock
    global motion_data
    global data_lock
    global command
    global command_lock
    global data
    scaning_time_s = 3
    devices = []
    connection_tries = 0
    current_row = [0]*24
    started_taking_data = False

    #getting devices
    speaker_lock.acquire()
    speaker = 1
    manager = Manager.instance()
    manager.discover(scanning_time_s)
    print('Devices Connected')
    discovered_devices = manager.get_nodes()
    for device in discovered_devices:
        print('%s: [%s]' % (device.get_name(), device.get_tag()))
        devices.append(device)
        while not device.connect() or connection_tries > 10:
            connection_tries += 1

    #get feature indicies
    device = devices[0]
    feature_indices = []
    features = device.get_features()
    for feature in features:
        if feature.get_name() == 'Accelerometer':
            acceleration_index = features.index(feature)
            feature_indices.append(acceleration_index)
        elif feature.get_name() == 'Gyroscope':
            gyro_index = features.index(feature)
            feature_indices.append(gyro_index)

    #get measurements
    while continue_variable:
        if command == 1:
            data = 0
            acceleration_df = pd.DataFrame([],columns=['time','ax','ay','az'])
            angular_speed_df = pd.DataFrame([],columns=['time','wx','wy','wz'])
            for index in feature_indices:
                feature = features[index]
                feature_listener = MyFeatureListener()
                feature.add_listener(feature_listener)
                device.enable_notifications(feature)

            wait_for_speaker()
            speaker_lock.acquire()
            speaker = 5
            speaker_lock.release()
            wait_for_speaker()

            # Getting notification
            notifications = 0
            while notifications < 20:
                if device.wait_for_notifications(0.05):
                notifications += 1

            # Disabling notifications.
            device.disable_notifications(feature)
            feature.remove_listener(feature_listener)

            #adding to data table
            data_lines = data.split('\n')
            for line in data_lines:
                #Accelerometer(51692): ( X: 25 mg    Y: -45 mg    Z: 1010 mg )
                if 'Accelerometer' in line:
                    rows = acceleration_df.shape()[0]
                    time = line.split(')')[0].split('(')[1]
                    values = line.split(' ')
                    acceleration_df[rows] = [time, values[3], values[9],\
                                            values[15]
                elif 'Gyroscope' in line:
                    rows = angular_speed_df.shape()[0]
                    time = line.split(')')[0].split('(')[1]
                    values = line.split(' ')
                    angular_speed_df[rows] = [time, values[3], values[9],\
                                            values[15]]
                times = acceleration_df['time'].to_numpy()
                axs = acceleration_df['ax'].to_numpy()
                ays = acceleration_df['ay'].to_numpy()
                azs = acceleration_df['az'].to_numpy()
                int_ax = integrate.simps(axs, times)
                int_ay = integrate.simps(ays, times)
                int_az = integrate.simps(azs, times)
                ax_max = max(axs)
                ax_min = min(axs)
                ay_max = max(ays)
                ay_min = min(ays)
                az_max = max(azs)
                az_min = min(azs)
                wxs = angular_speed_df['wx'].to_numpy()
                wys = angular_speed_df['wy'].to_numpy()
                wzs = angular_speed_df['wz'].to_numpy()
                wx_max = max(wxs)
                wx_min = min(wxs)
                wy_max = max(wys)
                wy_min = min(wys)
                wz_max = max(wzs)
                wz_min = min(wzs)
                rows = motion_data.size()[0]
                motion_data_lock.acquire()
                made = 2
                while made not in [0,1]:
                    made = int(input('\n\nDid you make it?\n\t1) Miss\n\t'+\
                    '2)Make'))-1
                    if not made in [0,1]:
                        sys.stdout.write('\n\nPlease enter 1 or 2')
                motion_data[rows] = [int_ax, ax_min, ax_max, int_ay, ay_min, \
                ay_max, int_az, az_min, az_max, wx_min, wx_max, wy_min, \
                wy_max, wz_min, wz_max, made, '']
                command_lock.acquire()
                command = 2
                command_lock.release()
        else:
            time.sleep(0.1)

