from __future__ import division
from Subfact_ina219 import INA219
import time
from datetime import datetime, timedelta
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure, YAxis, Font, Marker
import numpy as np
from matplotlib.dates import date2num  # ,num2date
from expected_solar import expected_solar

'''
SunPi script
'''


def connect2plotly():

    # Logging in to plotly
    username = 'your username'
    api_key = 'your api key'
    stream_token = 'stream_token1'
    stream_token2 = 'stream_token2'
    stream_token3 = 'stream_token3'

    py.sign_in(username, api_key)

    # Initializing scatterplot
    trace1 = Scatter(
        x=[],
        y=[],
        name='Wattage',
        stream=dict(
            token=stream_token,
            maxpoints=400
        ),
        marker=Marker(
            color='#1f77b4'
            ),
        yaxis='y'
        )

    trace2 = Scatter(
        x=[],
        y=[],
        name='Voltage',
        stream=dict(
            token=stream_token2,
            maxpoints=400
        ),
        marker=Marker(
            color='#d62728'
            ),
        yaxis='y2'
        )

    trace3 = Scatter(
        x=[],
        y=[],
        name='Sun altitude',
        stream=dict(
            token=stream_token3,
            maxpoints=100
        ),
        marker=Marker(
            color='#E79726'
            ),
        yaxis='y3'
        )

    layout = Layout(
        title='SunPi battery',
        yaxis=YAxis(
            title='Power [W]',      # y-axis title
            titlefont=Font(
                color='#1f77b4'
                ),
            tickfont=Font(
                color='#1f77b4'
                )
            ),
        yaxis2=YAxis(
            title='Voltage [V]',
            anchor='x',
            overlaying='y',
            side='right',
            titlefont=Font(
                color='#d62728'
                ),
            tickfont=Font(
                color='#d62728'
            )),
        yaxis3=YAxis(
            title='Sun altitude [deg.]',
            anchor='free',
            overlaying='y',
            side='right',
            position=0.95,
            titlefont=Font(
                color='#E79726'
                ),
            tickfont=Font(
                color='#E79726'
            ),
        )
    )

    fig = Figure(data=[trace1, trace2, trace3], layout=layout)

    # Comment this line (put # in front)
    # to keep old data in plot when restarting
    print py.plot(fig, filename='SunPi')

    # Open streams
    stream = py.Stream(stream_token)
    stream.open()

    stream2 = py.Stream(stream_token2)
    stream2.open()

    stream3 = py.Stream(stream_token3)
    stream3.open()

    return stream, stream2, stream3

# Opening connection to plotly
[stream, stream2, stream3] = connect2plotly()

# Adding hours
add_hour = 0

# Values
sec_between_real_measurements = 1

# Org 216-16 Number of measurements needed before taking avg for points
# (-16 since they are reserved for sending the mean to plotly)
num_loop_over_time = 216-16

# Org 200 Number of these avg points I want in 12 hours plot
num_of_points_12_hours = 200

expected_time = num_loop_over_time + 16

# Initializing arrays
loop_over_time = xrange(num_loop_over_time)
bat_vol = np.zeros(num_loop_over_time)
bat_wat = np.zeros(num_loop_over_time)
# 400 points when having 216 sec in between
full_day_data = np.empty([2*num_of_points_12_hours,
                          2*num_of_points_12_hours])
full_day_for_loop = xrange(2*num_of_points_12_hours)
bat_vol_plotly = np.zeros(2*num_of_points_12_hours)
bat_wat_plotly = np.zeros(2*num_of_points_12_hours)
time_for_saving = np.zeros(2*num_of_points_12_hours)

# Initializing sensor (assuming single sensor connected)
ina = INA219()
# Change this to reflect your address

# Plotting what we expect
try:
    # print 'stream3'
    time_expect, sun_expect = expected_solar()
    stream3.write({'x': time_expect, 'y': sun_expect})
except Exception:
    pass
    # could not get sun curve for today. oh, well. We will try again tomorrow


# Getting start time
starttime = time.time()

g = -1

while True:
    g += 1
    # Collecting data over max 1 whole day
    # 400 points for a whole day

    day_data_collected_from = (datetime.now() +
                               timedelta(hours=add_hour)).date()

    # Collecting data for a single point
    for k in loop_over_time:

        # Battery sensor
        try:
            # Voltage
            bat_vol[k] = (ina.getBusVoltage_V() +
                          (ina.getShuntVoltage_mV()/1000))

            # Wattage, bat_vol[k]*amp_temp
            bat_wat[k] = -bat_vol[k]*ina.getCurrent_mA()/1000
        except Exception:
            # If not able to read from device, simply pass.
            # Oterwise the script will stop executing.
            pass

        # Waiting a certain time such that the stuff inside this loop +
        # time.sleep equals the sec_between_real_measurements
        time.sleep(sec_between_real_measurements -
                   ((time.time() - starttime) % sec_between_real_measurements))

    # Adding hours to fit timezone and/or summertime. Change this to your needs
    added_hours = datetime.now() + timedelta(hours=add_hour)
    time_for_plotly = format(added_hours, '%Y-%m-%d %H:%M:%S.%f')
    bat_wat_plotly[g] = np.mean(bat_wat)
    bat_vol_plotly[g] = np.mean(bat_vol)

    # Since the time is a datetime object, translate this into numbers.
    # When you want to go from these numbers to the original dates
    # then use num2date
    time_for_saving[g] = date2num(added_hours)

    # Give loop some time to send the data to plotly in a consistent way
    # If exception: wait, reconnect
    try:
        # print 'stream1'
        stream.write({'x': time_for_plotly, 'y': bat_wat_plotly[g]})
    except Exception:

        time.sleep(2)

        # Opening connection to plotly
        [stream, stream2, stream3] = connect2plotly()

        pass

    try:
        # print 'stream2'
        stream2.write({'x': time_for_plotly, 'y': bat_vol_plotly[g]})
    except Exception:

        time.sleep(2)

        # Opening connection to plotly
        [stream, stream2, stream3] = connect2plotly()

        pass

    '''
     So the "Collecting data" loop should have taken
     sec_between_real_measurements * num_loop_over_time seconds
     Let's just collect data (for a single point) for 200 seconds,
     then spend 16 seconds on sending the mean of the data to plotly.
     This means, change num_loop_over_time from 216 -> 200
     '''

    # Check if we passed midnight and if: yes; then save data to txt

    if day_data_collected_from < (datetime.now() +
                                  timedelta(hours=add_hour)).date():

        full_day_data = [np.copy(time_for_saving),
                         np.copy(bat_wat_plotly),
                         np.copy(bat_vol_plotly)]

        # Got data, now saving data
        np.savetxt('/home/pi/SunPi/Data/SunPi_mismatch_' +
                   day_data_collected_from.strftime("%Y_%m_%d") +
                   '.txt', full_day_data)

        # Make sure the loop starts from g = 0 after saving files
        g = -1

        # Reset the data arrays
        time_for_saving = np.zeros(2*num_of_points_12_hours)
        bat_vol_plotly = np.zeros(2*num_of_points_12_hours)
        bat_wat_plotly = np.zeros(2*num_of_points_12_hours)
        full_day_data = np.empty([2*num_of_points_12_hours,
                                  2*num_of_points_12_hours])

        # Plotting what we expect
        try:
            # print 'stream3'
            time_expect, sun_expect = expected_solar()
            stream3.write({'x': time_expect, 'y': sun_expect})
        except Exception:
            pass
            # Unable to get sun curve for today.
            # Oh, well. we will try again tomorrow !

    # Again we wait such that the stuff inside loop+time.sleep=expected_time
    [time.sleep(expected_time - ((time.time() - starttime) % expected_time))]
