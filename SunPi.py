from __future__ import division
from Subfact_ina219 import INA219
import time
from datetime import datetime, timedelta
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure, YAxis
import numpy as np

### SunPi script

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

print py.plot(fig, filename='SunPi wattage')

# Open stream
#sensor_pin = 0
stream = py.Stream(stream_token)
stream.open()


# Initializing current sensor
ina = INA219()

add_hour = 1

# Want 12 hours in plot. 200 points split over 12 hours (43200 sec) -> 43200/200 = 216 sec per point 
avg_time_window = 216
power_avg = np.empty(avg_time_window)
for_avg_loop = xrange(avg_time_window)
# Main sensor reading loop
while True:
        #print
        #print "Shunt   : %.3f mV" % ina.getShuntVoltage_mV()
        #print "Bus     : %.3f V" % ina.getBusVoltage_V()
        #print "Current : %.3f mA" % ina.getCurrent_mA()
        #print "Power   : %.3f mW" % ina.getPower_mW()


        # delay between stream posts
        for k in for_avg_loop:
                power_avg[k] = -12*ina.getCurrent_mA()/1000#ina.getPower_mW()
                print power_avg[k]
                time.sleep(1)

        sensor_data = np.mean(power_avg)
        print
        print 'sensor data ' + str(sensor_data)
        added_hours = datetime.now() + timedelta(hours=add_hour)
        #stream.write({'x': datetime.datetime.now().strftime(add_hour,'%Y-%m-%d %H:%M:%S.%f'), 'y': sensor_data})
        stream.write({'x': format(added_hours,'%Y-%m-%d %H:%M:%S.%f'), 'y': sensor_data})

