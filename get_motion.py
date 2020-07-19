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
    global data
    global data_lock
    global command
    global command_lock
    global motion_data
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
            for index in feature_indices:
                feature = features[index]
                feature_listener = MyFeatureListener()
                feature.add_listener(feature_listener)
                device.enable_notifications(feature)

            # Getting notification
            notifications = 0
            while notifications < notifications:
                if device.wait_for_notifications(0.05):
                notifications += 1

            # Disabling notifications.
            device.disable_notifications(feature)
            feature.remove_listener(feature_listener)

            ####################################################################
            ################PARSE DATA AND UPDATE TABLE#########################
            ####################################################################
        else:
            time.sleep(0.1)

