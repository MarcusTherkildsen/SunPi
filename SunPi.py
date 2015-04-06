from __future__ import division
from Subfact_ina219 import INA219
import time
from datetime import datetime, timedelta
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure, YAxis
import numpy as np

### SunPi script ###

# Logging in to plotly
username = 'your plotly username'
api_key = 'plotly api key'
stream_token = 'plotly stream token'

py.sign_in(username, api_key)

# Initializing scatterplot
trace1 = Scatter(
    x=[],
    y=[],
    stream=dict(
        token=stream_token,
        maxpoints=200
    )
)

layout = Layout(
    title='SunPi wattage',
    yaxis=YAxis(
        title='Power [W]'      # y-axis title
)
)

fig = Figure(data=[trace1], layout=layout)

# Comment out this line to keep old data in plot.ly plot (e.g. if yiu have to restart you raspberry pi and you want the data collection to continue from where it left of)
print py.plot(fig, filename='SunPi wattage')

# Open stream

stream = py.Stream(stream_token)
stream.open()


# Initializing current sensor
ina = INA219()

# Adding 1 hour to datetime such that the time corresponds to local time here in Denmark
add_hour = 1

# Want 12 hours in plot. 200 points split over 12 hours (43200 sec) -> 43200/200 = 216 sec per point 
avg_time_window = 216

# Initializing arrays
power_avg = np.empty(avg_time_window)
for_avg_loop = xrange(avg_time_window)

# Main sensor reading loop
while True:
        #print
        #print "Shunt   : %.3f mV" % ina.getShuntVoltage_mV()
        #print "Bus     : %.3f V" % ina.getBusVoltage_V()
        #print "Current : %.3f mA" % ina.getCurrent_mA()
        #print "Power   : %.3f mW" % ina.getPower_mW()


        # Collecting avg_time_window - number of measurements seperated by approx. 1 sec
        for k in for_avg_loop:
                # Power in watt
                power_avg[k] = (ina.getBusVoltage_V()+(ina.getShuntVoltage_mV()/1000)) * ina.getCurrent_mA()/1000
                time.sleep(1)
        
        # Calculating mean value of the power
        sensor_data = np.mean(power_avg)
        
        # Getting date for the plot
        added_hours = datetime.now() + timedelta(hours=add_hour)
        
        # Sending data to plot.ly
        stream.write({'x': format(added_hours,'%Y-%m-%d %H:%M:%S.%f'), 'y': sensor_data})

