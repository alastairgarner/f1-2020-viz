#! /usr/bin/env python3

################################################
### Load Dependencies

import sqlite3
import os
from collections import namedtuple
from queue import Queue
import ctypes

import numpy as np
import pandas as pd

from f1_2020_telemetry.packets import unpack_udp_packet
from f1_2020_viz import DBConnection, PktType 

################################################
### Functions
    
class Query(object):
    """Docstring"""
    
    GET_PARTICIPANTS = f"""
        SELECT MAX(pkt_id),*
        FROM packets
        WHERE packetId == {PktType.PARTICIPANTS.value}
    """
    
################################################
### Scripting

filename = "./dbs/F1_2019_8fbc811b663fb2e4.sqlite3"

db = DBConnection(filename)

########

fields = {
    PktType.PARTICIPANTS: [
        'playerCarIndex', 'aiControlled', 'driverId', 'teamId', 'raceNumber', 'nationality', 'name',
    ],
    PktType.LAPDATA: [
        "frameIdentifier", "sessionTime", "currentLapNum", "lapDistance", "totalDistance", "carPosition", "resultStatus"
    ]
}

data = db.get(fields=fields)

data[PktType.PARTICIPANTS]
data[PktType.LAPDATA]

########

