# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 01:04:56 2015

@author: Marcus Therkildsen
"""
from __future__ import division
import numpy as np
from datetime import datetime
from pytz import timezone
import cookielib
import urllib2
import dateutil

'''
CALC
'''


def expected_solar():

    # New source
    # http://www.solartopo.com/solar-orbit.htm

    # Find your latitude and longitude with www.google.dk/maps/
    lat = 'your latitude'
    lon = 'your longitude'

    # Today
    which_date = datetime.now().strftime("%d-%m-%Y")
    # 0 for wintertime, 1 for summertime
    daylight_saving = [str(datetime.now(tz=timezone('CET')).timetuple()
                                                           .tm_isdst)]

    # url to get csv file from
    url_data = ['http://www.solartopo.com/services/solarOrbit.php?lat=' + lat +
                '&long=' + lon + '&date=' + which_date + '&dst=' +
                daylight_saving]

    # Download csv file, open and extract time and height
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url_data)
    response = opener.open(request)
    data = response.read()
    with open('sun_height.csv', 'wb') as code:
        code.write(data)

    sun_height_full = np.genfromtxt('sun_height.csv', delimiter=',',
                                    dtype='str', autostrip=True)[7:]
    sun_height_full = np.array([sun_height_full[i].split(';')
                                for i in xrange(len(sun_height_full))])[:, :2]

    time_data = [dateutil.parser.parse(sun_height_full[i, 0])
                 for i in xrange(len(sun_height_full[:, 0]))]

    sun_alti = sun_height_full[:, 1].astype(float)

    return time_data, sun_alti
