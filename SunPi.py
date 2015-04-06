from __future__ import division 
from Subfact_ina219 import INA219
import time
from datetime import datetime, timedelta
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure, YAxis
import numpy as np
import os
from matplotlib.dates import date2num#,num2date
### SunPi script

def connect2plotly():
    # Logging in to plotly 
    username = 'your username'
    api_key = 'your-api_key'
    stream_token = 'stream_token1'
    stream_token2 = 'stream_token2'
    
    py.sign_in(username, api_key)
    
    # Initializing scatterplot
    trace1 = Scatter(
        x=[],
        y=[],
        name = 'Battery',
        stream=dict(
            token=stream_token,
            maxpoints=200
        )
    )
    
    
    trace2 = Scatter(
        x=[],
        y=[],
        name = 'Solar panel',
        stream=dict(
            token=stream_token2,
            maxpoints=200
        )
    )
    
    
    
    layout = Layout(
        title='SunPi',
        yaxis=YAxis(
            title='Power [W]'      # y-axis title
    )
    )
    
    
    
    fig = Figure(data=[trace1,trace2], layout=layout)
    
    # Comment out this line (put # in front) to keep old data in plot when restarting
    #print py.plot(fig, filename='SunPi')
    
    # Open streams
    stream = py.Stream(stream_token)
    stream.open()
    
    stream2 = py.Stream(stream_token2)
    stream2.open()
    
    return stream, stream2
    
# Opening connection to plotly

[stream, stream2] = connect2plotly()


# Adding hours
add_hour = 2


# Values
sec_between_real_measurements = 1
num_loop_over_time = 216-16 #org 216-16 Number of measurements needed before taking avg for points (-16 since they are reserved for sending the mean to plotly)
num_of_points_12_hours = 200 #org 200 Number of these avg points I want in 12 hours plot
how_long_time_getting_data_for_one_point_should_have_taken = num_loop_over_time + 16

# Initializing arrays
loop_over_time = xrange(num_loop_over_time)
ran_numba = np.zeros(num_loop_over_time)
solar = np.zeros(num_loop_over_time)
full_day_data = np.empty([2*num_of_points_12_hours,2*num_of_points_12_hours])#np.empty([num_loop_over_time,2*num_of_points_12_hours]) # 400 points when having 216 sec in between
full_day_for_loop = xrange(2*num_of_points_12_hours)
data_to_send_to_plotly = np.zeros(2*num_of_points_12_hours)
solar_avg = np.zeros(2*num_of_points_12_hours)
time_for_saving = np.zeros(2*num_of_points_12_hours)
# Getting start time
starttime=time.time()

g = -1

while True:
    g += 1
    # Collecting data over max 1 whole day
    # 400 points for a whole day 
    
    day_data_collected_from = (datetime.now() + timedelta(hours=add_hour)).date()
        
    # Collecting data for a single point
    for k in loop_over_time:

	# Battery sensor
        try:
            ina = INA219(address = int('0x44',16)) # Change this to reflect your address
            ran_numba[k] = (ina.getBusVoltage_V()+(ina.getShuntVoltage_mV()/1000)) * ina.getCurrent_mA()/1000 ## i.e. grab data from ina
        except Exception: 
            # If not able to read from device, simply pass. Oterwise the script will stop executing.
            pass

	time.sleep(0.15)

    # Solar panel sensor
        try:
            ina = INA219(address = int('0x40',16))
            solar[k] = -(ina.getBusVoltage_V()+(ina.getShuntVoltage_mV()/1000)) * ina.getCurrent_mA()/1000 ## i.e. grab data from ina
        except Exception:
            # If not able to read from device, simply pass. Oterwise the script will stop executing.
            pass

# The following lines are for testing
	
#        print 'Solar right now is ' + str(solar[k])   
#        print 'Battery i/o right now is ' + str(ran_numba[k])
#        print 'time to wait '+str(sec_between_real_measurements - ((time.time() - starttime) % sec_between_real_measurements))
#        print

        # Waiting a certain time such that the stuff inside this loop + time.sleep equals the sec_between_real_measurements
        time.sleep(sec_between_real_measurements - ((time.time() - starttime) % sec_between_real_measurements))
	
    # Adding hours to fit timezone and/or summertime. Change this to your needs.
    added_hours = datetime.now() + timedelta(hours=add_hour)
    
    time_for_plotly = format(added_hours,'%Y-%m-%d %H:%M:%S.%f')
    data_to_send_to_plotly[g] = np.mean(ran_numba)     
    solar_avg[g] = np.mean(solar)   
    # Since the time is a datetime object, translate this into numbers. 
    # When you want to go from these numbers to the original dates then use num2date
    time_for_saving[g] = date2num(added_hours)
	

    # Give loop some time to send the data to plotly in a consistent way
    # If exception: restart wifi connection
    try:    
        print 'stream1'
        stream.write({'x': time_for_plotly, 'y': data_to_send_to_plotly[g]})    
    except Exception:
	#print 'Running sudo ifdown wlan0'
        os.system("sudo ifdown wlan0")

        #print
        #print 'Now waiting 5 sec'
        time.sleep(2)
        #print

        #print 'Running sudo ifup --force wlan0'
        os.system("sudo ifup --force wlan0")
        time.sleep(2)
        
        # Opening connection to plotly
        [stream, stream2] = connect2plotly()

        pass

    try:
        print 'stream2'
        stream2.write({'x': time_for_plotly, 'y': solar_avg[g]})
    except Exception:
        #print 'Running sudo ifdown wlan0'
        os.system("sudo ifdown wlan0")

        #print
        #print 'Now waiting 5 sec'
        time.sleep(2)
        #print

        #print 'Running sudo ifup --force wlan0'
        os.system("sudo ifup --force wlan0")
        
        time.sleep(2)
        
        # Opening connection to plotly
        [stream, stream2] = connect2plotly()

        pass

        # So the "Collecting data" loop should have taken sec_between_real_measurements * num_loop_over_time seconds
        # Let's just collect data (for a single point) for 200 seconds, then spend 16 seconds on sending the mean of the data to plotly.
        # This means, change num_loop_over_time from 216 -> 200        
#       print 'Sending data to plotly and then waiting ' + str(how_long_time_getting_data_for_one_point_should_have_taken - ((time.time() - starttime) % how_long_time_getting_data_for_one_point_should_have_taken))
        
        
    # Check if we passed midnight and if: yes; then save data to txt      
        
    if day_data_collected_from < (datetime.now() + timedelta(hours=add_hour)).date():
        full_day_data = [np.copy(time_for_saving),np.copy(data_to_send_to_plotly),np.copy(solar_avg)]    
#        print 'data from '+str(day_data_collected_from) + ' now saving file'
        np.savetxt('/home/pi/SunPi/Data/SunPi_mismatch_'+day_data_collected_from.strftime("%Y_%m_%d")+'.txt',full_day_data)#test)	        
        # Make sure the loop starts from g = 0 after saving files
        g = -1
	
        # Reset the data arrays
        time_for_saving = np.zeros(2*num_of_points_12_hours)
        data_to_send_to_plotly = np.zeros(2*num_of_points_12_hours)
        solar_avg = np.zeros(2*num_of_points_12_hours)
        full_day_data = np.empty([2*num_of_points_12_hours,2*num_of_points_12_hours])
    #    print 'file saved, now waiting ' + str(how_long_time_getting_data_for_one_point_should_have_taken - ((time.time() - starttime) % how_long_time_getting_data_for_one_point_should_have_taken))	
    
    # Again we wait such that the stuff inside loop + time.sleep equals how_long_time_getting_data_for_one_point_should_have_taken    
    time.sleep(how_long_time_getting_data_for_one_point_should_have_taken - ((time.time() - starttime) % how_long_time_getting_data_for_one_point_should_have_taken))    
        
        
