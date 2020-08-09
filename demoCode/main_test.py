
#from __future__ import print_function
import sys
import os
import subprocess
import time
import numpy as np
import pandas as pd
from abc import abstractmethod

from blue_st_sdk.manager import Manager
from blue_st_sdk.manager import ManagerListener
from blue_st_sdk.node import NodeListener
from blue_st_sdk.feature import FeatureListener
from blue_st_sdk.features.audio.adpcm.feature_audio_adpcm import FeatureAudioADPCM
from blue_st_sdk.features.audio.adpcm.feature_audio_adpcm_sync import FeatureAudioADPCMSync

from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

from scipy.integrate import simps
from scipy.fftpack import fft
from scipy.signal import resample

data = ''
suggestions = ['ns', 'ft', 'cw', 'bl', 'ei', 'ss', 'sf', 'sm']
#ns no suggestion, ft follow through, cw cock wrist, bl bend legs, ei elbow in,
#ss square sholder, sf shoot faster, so shoot in one continuous motion
NOTIFICATIONS = 600
SCANNING_TIME_s = 5
shots = 0 
makes = 0
taking_data = True

def print(output='', to_screen=False):
    global data
    output = str(output)+'\n'
    data += output
    if to_screen:
        sys.stdout.write(output+'\n')

# INTERFACES

#
# Implementation of the interface used by the Manager class to notify that a new
# node has been discovered or that the scanning starts/stops.
#
class MyManagerListener(ManagerListener):

    #
    # This method is called whenever a discovery process starts or stops.
    #
    # @param manager Manager instance that starts/stops the process.
    # @param enabled True if a new discovery starts, False otherwise.
    #
    def on_discovery_change(self, manager, enabled):
        print('Discovery %s.' % ('started' if enabled else 'stopped'), True)
        if not enabled:
            print()

    #
    # This method is called whenever a new node is discovered.
    #
    # @param manager Manager instance that discovers the node.
    # @param node    New node discovered.
    #
    def on_node_discovered(self, manager, node):
        print('New device discovered: %s.' % (node.get_name()),True)


#
# Implementation of the interface used by the Node class to notify that a node
# has updated its status.
#
class MyNodeListener(NodeListener):

    #
    # To be called whenever a node connects to a host.
    #
    # @param node Node that has connected to a host.
    #
    def on_connect(self, node):
        print('Device %s connected.' % (node.get_name()), True)

    #
    # To be called whenever a node disconnects from a host.
    #
    # @param node       Node that has disconnected from a host.
    # @param unexpected True if the disconnection is unexpected, False otherwise
    #                   (called by the user).
    #
    def on_disconnect(self, node, unexpected=False):
        print('Device %s disconnected%s.' % \
            (node.get_name(), ' unexpectedly' if unexpected else ''), True)
        if unexpected:
            print('Trying to reconnect.\n', True)
            if node.connect():
                print('Node connected', True)
            else:
                # Exiting.
                print('\nExiting...\n', True)
                sys.exit(0)


#
# Implementation of the interface used by the Feature class to notify that a
# feature has updated its data.
#
class MyFeatureListener(FeatureListener):

    _notifications = 0
    """Counting notifications to print only the desired ones."""

    #
    # To be called whenever the feature updates its data.
    #
    # @param feature Feature that has updated.
    # @param sample  Data extracted from the feature.
    #
    def on_update(self, feature, sample):
        if self._notifications < NOTIFICATIONS:
            self._notifications += 1
            print(feature, True)

def get_feedback(speaker):
    if speaker == 'cg':
        subprocess.check_output('omxplayer sounds/connecting.mp3', shell='True')
    elif  speaker == 'cd':
        subprocess.check_output('omxplayer sounds/connected.mp3', shell='True')
    elif  speaker == 'ud':
        subprocess.check_output('omxplayer sounds/unconnected.mp3',\
        shell='True')
    elif  speaker == 'rd':
        subprocess.check_output('omxplayer sounds/ready.mp3', shell='True')
    elif  speaker == 'nd':
        subprocess.check_output('omxplayer sounds/noDeviceFound.mp3',\
        shell='True')
    elif  speaker == 'ce':
        subprocess.check_output('omxplayer sounds/cantConnectGoodbye.mp3',\
        shell='True')
    elif  speaker == 'st':
        subprocess.check_output('omxplayer sounds/shoot.mp3', shell='True')
    elif  speaker == 'sr':
        subprocess.check_output('omxplayer sounds/shotRecorded.mp3',\
        shell='True')
    elif  speaker == 'bl':
        osubprocess.check_output('omxplayer sounds/bendYourLegs.mp3',\
        shell='True')
    elif  speaker == 'ft':
        subprocess.check_output('omxplayer sounds/followThrough.mp3',\
        shell='True')
    elif  speaker == 'cw':
        subprocess.check_output('omxplayer sounds/cockYourWrist.mp3',\
        shell='True')
    elif  speaker == 'ei':
        subprocess.check_output('omxplayer sounds/elbowIn.mp3', shell='True')
    elif  speaker == 'ss':
        subprocess.check_output('omxplayer sounds/squareShoulders.mp3',\
        shell='True')
    elif  speaker == 'sf':
        subprocess.check_output('omxplayer sounds/shootFaster.mp3',\
        shell='True')
    elif  speaker == 'sm':
        subprocess.check_output('omxplayer sounds/shootInOneMotion.mp3',\
        shell='True')
    elif  speaker == 'ns':
        subprocess.check_output('omxplayer sounds/niceShot.mp3', shell='True')

def trim_data(w,a):
    w2 = w['wx']**2 + w['wy']**2 + w['wz']**2
    a2 = a['ax']**2 + a['ay']**2 + a['az']**2
    center_index = w2.idxmax()
    empty_frame = (pd.DataFrame([],columns=w.columns),pd.DataFrame([],columns=a.columns))
    if w2.max()>2250000 and center_index-5>=0 and center_index+5<len(w2):
        start_index = center_index
        stop_index = center_index
        while (sum(list(w2[start_index:start_index+5]))/5 >50 or (w['time'][center_index]-w['time'][start_index])<200)\
        and start_index>1:
            start_index -= 1
        while sum(list(w2[stop_index-5:stop_index]))/5 >50 and stop_index<len(w2)-1:
            stop_index += 1
        start_time = w['time'][start_index]
        stop_time = w['time'][stop_index]
        w = w[w['time']>=start_time]
        w = w[w['time']<=stop_time]
        a = a[a['time']>=start_time]
        a = a[a['time']<=stop_time]
        w = w.reset_index()
        a = a.reset_index()
        return (w,a)
    else:
        return empty_frame

def get_v(w, a):
    g = np.sqrt(a['ax'][0]**2+a['ay'][0]**2+a['az'][0]**2)
    v = np.array([0, 0, 0])
    phi = np.arctan(a['ay'][0]/a['ax'][0])
    theta = np.arctan(np.sqrt(a['ax'][0]**2+a['ay'][0]**2)/a['az'][0])
    x = [1, 0, 0]
    y = [0, 1, 0]
    z = [0, 0, 1]
    Ry = [[np.cos(theta),0,-np.sin(theta)], [0,1,0], [np.sin(theta),1,np.cos(theta)]]
    Rz = [[np.cos(phi),-np.sin(phi),0], [np.sin(phi),np.cos(phi),0], [0,0,1]]
    xp = np.matmul(Rz,np.matmul(Ry,x))
    yp = np.matmul(Rz,np.matmul(Ry,y))
    zp = np.matmul(Rz,np.matmul(Ry,z))
    
    for n in range(len(w)-1):
        dt = (w['time'][n+1]-w['time'][n])/1000
        phi = np.arctan(a['ay'][0]/a['ax'][0])
        theta = np.arctan(np.sqrt(a['ax'][0]**2+a['ay'][0]**2)/a['az'][0])
        G = np.matmul(Rz,np.matmul(Ry,z))*g/1000*9.8
        v = v + (a['ax'][n]*xp+a['ay'][n]*yp+a['az'][n]*zp+G)*9.8/1000*dt
        wv = np.array([w['wx'][n], w['wy'][n], w['wz'][n]])*np.pi/180
        xn = xp + dt*np.cross(wv,xp)
        yn = yp + dt*np.cross(wv,yp)
        zn = zp + dt*np.cross(wv,zp)
        xp = xn/np.sqrt(np.dot(xn,xn))
        yp = yn/np.sqrt(np.dot(yn,yn))
        zp = zn/np.sqrt(np.dot(zn,zn))
    return v

def main(argv):
    global data
    global shots
    global makes

    try:

        motion_data = pd.read_csv('motion_data.csv')
        suggestion_data = pd.read_csv('suggestion_data.csv')

        # Creating Bluetooth Manager.
        manager = Manager.instance()
        manager_listener = MyManagerListener()
        manager.add_listener(manager_listener)
        feature_indices = []

        while True:
            # Synchronous discovery of Bluetooth devices.
            print('Scanning Bluetooth devices...\n', True)
            manager.discover(SCANNING_TIME_s)

            # Alternative 1: Asynchronous discovery of Bluetooth devices.
            #manager.discover(SCANNING_TIME_s, True)

            # Alternative 2: Asynchronous discovery of Bluetooth devices.
            #manager.start_discovery()
            #time.sleep(SCANNING_TIME_s)
            #manager.stop_discovery()

            # Getting discovered devices.
            discovered_devices = manager.get_nodes()

            # Listing discovered devices.
            if not discovered_devices:
                print('No Bluetooth devices found. Exiting...\n', True)
                sys.exit(0)
            print('Available Bluetooth devices:', True)
            i = 1
            for device in discovered_devices:
                print('%d) %s: [%s]' % (i, device.get_name(),\
                device.get_tag()), True)
                i += 1

            # Selecting a device.
            while True:
                choice = int(
                    input("\nSelect a device to connect to (\'0\' to quit): "))
                if choice >= 0 and choice <= len(discovered_devices):
                    break
            if choice == 0:
                # Exiting.
                manager.remove_listener(manager_listener)
                print('Exiting...\n', True)
                sys.exit(0)
            device = discovered_devices[choice - 1]
            node_listener = MyNodeListener()
            device.add_listener(node_listener)

            # Connecting to the device.
            print('Connecting to %s...' % (device.get_name()), True)
            if not device.connect():
                print('Connection failed.\n', True)
                continue

            while True:

                # Getting features.
                features = device.get_features()

                #get feature indicies
                for feature in features:
                    if feature.get_name() == 'Accelerometer':
                        acceleration_index = features.index(feature)
                        feature_indices.append(acceleration_index)
                    elif feature.get_name() == 'Gyroscope':
                        gyro_index = features.index(feature)
                        feature_indices.append(gyro_index)

                # Enabling notifications.
                feature_listener = MyFeatureListener()
                for index in feature_indices:
                    feature = features[index]
                    feature.add_listener(feature_listener)
                    device.enable_notifications(feature)
                # Selecting a feature.

                while True:
                    choice = int(input('\nShots: ' + str(shots) + ' Makes: '\
                    + str(makes)+'\nWould you like to shoot at this '\
                    + 'spot?\n1) Yes\n2) Change spots\n\nSelect a choice to '\
                    + 'connect to (\'0\' to disconnect): '))
                    if choice >= 0 and choice <= 2:
                        break
                if choice == 0:
                    # Disconnecting from the device.
                    print('\nDisconnecting from %s...' % (device.get_name()),\
                    True)
                    if not device.disconnect():
                        print('Disconnection failed.\n', True)
                        continue
                    device.remove_listener(node_listener)
                    # Resetting discovery.
                    manager.reset_discovery()
                    # Going back to the list of devices.
                    break

                # Handling audio case (both audio features have to be enabled).
                #if isinstance(feature, FeatureAudioADPCM):
                #    audio_sync_feature_listener = MyFeatureListener()
                #    audio_sync_feature.add_listener(audio_sync_feature_listener)
                #    device.enable_notifications(audio_sync_feature)
                #elif isinstance(feature, FeatureAudioADPCMSync):
                #    audio_feature_listener = MyFeatureListener()
                #    audio_feature.add_listener(audio_feature_listener)
                #    device.enable_notifications(audio_feature)
                #    device.enable_notifications(audio_feature)

                # Getting notifications.
                get_feedback('rd')
                time.sleep(1)
                get_feedback('st')
                notification = 0
                start_time = time.time()
                while time.time() - start_time < 3:
                    trial_time = time.time()
                    if device.wait_for_notifications(0.05):
                        notification += 1
                print(str(notification) + ' data points recorded', True)
                get_feedback('sr')

                #get result
                result = 6
                while not result in [0,1,2,3,4,5]:
                    result = int(input('\nPlease record the result.\n1) Make'\
                    + '\n2) Left\n3) Right\n4) Short\n5) Long\n6) Bad miss (do'\
                    + ' not record)\n(\'0\' to disconnect)'))-1
                if result == -1:
                    # Disconnecting from the device.
                    print('\nDisconnecting from %s...' % (device.get_name()),\
                    True)
                    if not device.disconnect():
                        print('Disconnection failed.\n', True)
                        continue
                    device.remove_listener(node_listener)
                    # Resetting discovery.
                    manager.reset_discovery()
                    # Going back to the list of devices.
                    break
                elif result == 0:
                    results = [1, 0, 0, 0, 0]
                    makes += 1
                    shots += 1
                elif result == 1:
                    results = [0, 1, 0, 0, 0]
                    shots += 1
                elif result == 2:
                    results = [0, 0, 1, 0, 0]
                    shots += 1
                elif result == 3:
                    results = [0, 0, 0, 1, 0]
                    shots += 1
                elif result == 4:
                    results = [0, 0, 0, 0, 1]
                    shots += 1
                else:
                    results = []

                if len(results):
                    #recording data
                    acceleration_df = pd.DataFrame([],columns=['time', 'ax', \
                    'ay', 'az'])
                    angular_speed_df = pd.DataFrame([],columns=['time', 'wx', \
                   'wy', 'wz'])
                    data_lines = data.split('\n')
                    for line in data_lines:
                    #Accelerometer(51692): ( X: 25 mg    Y: -45 mg    Z: 1010 mg )
                        if 'Accelerometer' in line:
                            t = line.split(')')[0].split('(')[1]
                            values = line.split(' ')
                            acceleration_df.loc[len(acceleration_df)] = [ \
                            float(t), float(values[3]), float(values[9]), \
                            float(values[15])]
                        elif 'Gyroscope' in line:
                            t = line.split(')')[0].split('(')[1]
                            values = line.split(' ')
                            angular_speed_df.loc[len(angular_speed_df)] = [ \
                            float(t), float(values[3]), float(values[9]), \
                            float(values[15])]

                    tas = acceleration_df['time'].to_numpy()
                    axs = acceleration_df['ax'].to_numpy()
                    ays = acceleration_df['ay'].to_numpy()
                    azs = acceleration_df['az'].to_numpy()
                    ax_int = simps(axs,tas)
                    ay_int = simps(ays, tas)
                    az_int = simps(azs, tas)
                    ax_max = axs.max()
                    ax_min = axs.min()
                    ax_mean = axs.mean()
                    ay_max = ays.max()
                    ay_min = ays.min()
                    ay_mean = ays.mean()
                    az_max = azs.max()
                    az_min = azs.min()
                    az_mean = azs.mean()
                    tws = angular_speed_df['time'].to_numpy()
                    wxs = angular_speed_df['wx'].to_numpy()
                    wys = angular_speed_df['wy'].to_numpy()
                    wzs = angular_speed_df['wz'].to_numpy()
                    wx_int = simps(wxs, tws)
                    wy_int = simps(wys, tws)
                    wz_int = simps(wzs, tws)
                    wx_max = wxs.max()
                    wx_min = wxs.min()
                    wx_mean = wxs.mean()
                    wy_max = wys.max()
                    wy_min = wys.min()
                    wy_mean = wys.mean()
                    wz_max = wzs.max()
                    wz_min = wzs.min()
                    wz_mean = wzs.mean()
                    a_int = simps(np.sqrt(axs**2+ays**2+azs**2), tas)
                    w_int = simps(np.sqrt(wxs**2+wys**2+wzs**2), tws)
                    v = get_v(angular_speed_df, acceleration_df)
                    vx = v[0]
                    vy = v[1]
                    vz = v[2]
                    N = len(angular_speed_df['time'])
                    if N > 10:
                        T = (angular_speed_df['time'][N-1]-\
                        angular_speed_df['time'][0])/N/1000
                        t = np.linspace(0.0, N*T, N)
                        f = np.linspace(0.0, 1.0/2/T, N//2)
                        uniform_wx= resample(angular_speed_df['wx'], N, \
                        angular_speed_df['time'])
                        fft_wx = fft(uniform_wx[0])
                        uniform_wy = resample(angular_speed_df['wy'], N, \
                        angular_speed_df['time'])
                        fft_wy = fft(uniform_wy[0])
                        uniform_wz = resample(angular_speed_df['wz'], N, \
                        angular_speed_df['time'])
                        fft_wz = fft(uniform_wz[0])
                        wxfs = 2/N*np.abs(fft_wx[0:N//2])
                        wxf = f[np.where(wxfs==wxfs.max())[0][0]]
                        wyfs = 2/N*np.abs(fft_wy[0:N//2])
                        wyf = f[np.where(wyfs==wyfs.max())[0][0]]
                        wzfs = 2/N*np.abs(fft_wz[0:N//2])
                        wzf = f[np.where(wzfs==wzfs.max())[0][0]]
                    else:
                        wxf = 1
                        wyf = 1
                        wzf = 1
                    if taking_data:
                        file_prefix = str(time.time()).split('.')[0]
                        acceleration_df.to_csv('data/'+file_prefix+'a.csv', \
                        index=False)
                        angular_speed_df.to_csv('data/'+file_prefix+'w.csv', \
                        index = False)
                    #update suggestion data
                    if choice == 1 and len(motion_data)>1:
                        numerical_data = motion_data.drop(['make', 'left', \
                        'right', 'short', 'long', 'file_name', 'suggestion'], \
                        axis=1)
                        old_values = \
                        numerical_data.loc[len(numerical_data)-2].to_numpy()
                        old_values = np.where(old_values==0,0.1,old_values)
                        new_values = \
                        numerical_data.loc[len(numerical_data)-1].to_numpy()
                        if N > 10:
                            new_data = (new_values-old_values)/old_values
                            suggestion_data.loc[len(suggestion_data)] = \
                            list(new_data)+[motion_data['suggestion']\
                            [len(motion_data)-1]]
                    #get klusters
                    kluster_data = pd.DataFrame([])
                    if len(motion_data)>30:
                        kluster_data = motion_data.drop(columns=['suggestion',\
                        'file_name'], axis=1)
                        kluster_data.loc[len(kluster_data)] = [ax_min, ax_max, \
                        ax_int, ax_mean, vx, ay_min, ay_max, ay_int, ay_mean, \
                        vy, az_min, az_max, az_int, az_mean, vz, wx_min, \
                        wx_max, wx_int, wx_mean, wxf, wy_min, wy_max, wy_int, \
                        wy_mean, wyf, wz_min, wz_max, wz_int, wz_mean, wzf,\
                        a_int, w_int] + results
                        kluster_data['speed'] = np.sqrt(kluster_data['vx']**2+\
                        kluster_data['vy']**2+kluster_data['vz']**2)
                        prediction_data = kluster_data.drop(['ax_min', 'ax_max', \
                        'ax_int', 'ax_mean', 'vx', 'ay_min', 'ay_max', \
                        'ay_int', 'ay_mean', 'vy', 'az_min', 'az_max', \
                        'az_int', 'az_mean', 'wx_min', 'wx_max', 'wx_int', \
                        'wx_mean', 'wxf', 'wy_min', 'wy_max', 'wy_int', \
                        'wy_mean', 'wyf', 'wz_min', 'wz_max', 'wz_int', \
                        'wz_mean', 'wzf', 'a_int', 'w_int', 'short', 'long',\
                        'left', 'right'], axis=1)
                        kmeans = KMeans(n_clusters=20)
                        kmeans.fit(prediction_data)
                        y_kmeans = kmeans.predict(prediction_data)
                        kluster_data['y_kmeans'] = y_kmeans
                        kluster_data = kluster_data[kluster_data['y_kmeans']==\
                        kluster_data['y_kmeans'][len(kluster_data)-1]]
                        kluster_data = kluster_data.drop(['speed', 'y_kmeans'],\
                        axis = 1)
                    #get suggestion
                    suggestion = 'ns'
                    if len(kluster_data) >= 2:
                        std = kluster_data.std()
                        mean = kluster_data.mean()
                        if len(kluster_data)<30:
                            while len(kluster_data)<30 or \
                                kluster_data['make'].sum() == len(kluster_data)\
                                or kluster_data['make'].sum() == 0:
                                new = list(np.random.normal(mean,std))[:-5]\
                                + [0,0,0,0,0]
                                if new[9] > (mean+std)[9]:
                                    new[-1] = 1
                                elif new[9] < (mean-std)[9]:
                                    new[-2] = 1
                                elif  new[4] > (mean+std)[4]:
                                    new[-3] = 1
                                elif new[4] < (mean-std)[4]:
                                    new[-4] = 1
                                else:
                                    new[-5] = 1
                                kluster_data.loc[len(kluster_data)] = new
                        X = kluster_data.drop(['ax_min', 'ax_max', 'ax_int', \
                        'ax_mean', 'ay_min', 'ay_max', 'az_min', 'az_max', \
                        'az_int', 'az_mean', 'vz', 'wx_min', 'wx_max', \
                        'wx_int', 'wx_mean', 'wy_min', 'wy_max', 'wy_int', \
                        'wy_mean', 'wyf', 'wz_min', 'wz_max', 'wz_int', \
                        'wz_mean', 'wzf', 'a_int', 'make', 'left', 'right',\
                        'short', 'long'], axis=1)
                        y = kluster_data['make']
                        clf = LogisticRegression().fit(X, y)
                        best_prob = 0
                        for temp_suggestion in suggestions:
                            one_suggestion = suggestion_data[\
                            suggestion_data['suggestion']==temp_suggestion]
                            one_suggestion = one_suggestion.drop(['ax_min', \
                            'ax_max', 'ax_int', 'ax_mean', 'ay_min', 'ay_max', \
                            'az_min', 'az_max', 'az_int', 'az_mean', 'vz', \
                            'wx_min', 'wx_max', 'wx_int', 'wx_mean', 'wy_min', \
                            'wy_max', 'wy_int', 'wy_mean', 'wyf', 'wz_min', \
                            'wz_max', 'wz_int', 'wz_mean', 'wzf', 'a_int', ], \
                            axis=1)
                            coefficients = one_suggestion.mean().to_numpy()
                            x = coefficients*X.loc[len(X)-1].to_numpy()
                            temp_prob = clf.predict_proba(x.reshape(1,-1))[0][1]
                            if temp_prob > best_prob:
                                suggestion = temp_suggestion
                                best_prob = temp_prob
                    if N > 10:
                        motion_data.loc[len(motion_data)] = [ax_min, ax_max, \
                        ax_int, ax_mean, vx, ay_min, ay_max, ay_int, ay_mean, \
                        vy, az_min, az_max, az_int, az_mean, vz, wx_min, \
                        wx_max, wx_int, wx_mean, wxf, wy_min, wy_max, wy_int, \
                        wy_mean, wyf, wz_min, wz_max, wz_int, wz_mean, wzf, \
                        a_int, w_int] + results + [file_prefix, suggestion]
                    if suggestion != 'ns':
                        get_feedback(suggestion)
                    motion_data.to_csv('motion_data.csv', index=False)
                    suggestion_data.to_csv('suggestion_data.csv', index=False)
                data = ''


                # Disabling notifications.
                for index in feature_indices:
                    feature = features[index]
                    device.disable_notifications(feature)
                    feature.remove_listener(feature_listener)

                # Handling audio case (both audio features have to be disabled).
                if isinstance(feature, FeatureAudioADPCM):
                    device.disable_notifications(audio_sync_feature)
                    audio_sync_feature.remove_listener(audio_sync_feature_listener)
                elif isinstance(feature, FeatureAudioADPCMSync):
                    device.disable_notifications(audio_feature)
                    audio_feature.remove_listener(audio_feature_listener)

    except KeyboardInterrupt:
        try:
            # Exiting.
            print('\nExiting...\n', True)
            sys.exit(0)
        except SystemExit:
            sys.exit(0)


if __name__ == "__main__":

    main(sys.argv[1:])