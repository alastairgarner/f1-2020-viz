#! /usr/bin/env python3

################################################
# Load Dependencies

import os
import sqlite3
import pandas as pd

from .tables import PktType
from .utils import PacketParser

################################################
# Classes

class DBConnection(object):
    """A class to manage a connection to the current sqlite3 database"""
    
    _default_query = """
        SELECT *
        FROM packets
        WHERE packetId IN ({})
    """
    
    def __init__(self, database_path="./"):
        
        if not os.path.isfile(database_path):
            raise Exception(f"{database_path} does not exist")
        
        self.path = database_path
        self.conn = None
        self.connected_db = None
        
        self.connect()
    
    def connect(self):
        """Create connection to sqlite3 file"""
        
        if self.conn != None:
            self.disconnect()
        
        self.conn = sqlite3.connect(self.path)
        self.connected_db = self.path
        
        print(f"Connected to {self.connected_db}")
        
    def execute(self, *args, **kwargs):
        """Execute SQL query and return a cursor object"""
        
        return self.conn.execute(*args, **kwargs)
    
    def disconnect(self):
        """Close connection to sqlite3 file"""
        
        try:
            self.conn.close()
            self.conn = None
            
            print(f"Disconnected from {self.connected_db}")
            self.connected_db = None
        except:
            pass
        
    def get(self, fields=None, query=None, df=True):
        """Get specified packet fields from database"""
                
        types = ",".join([str(k.value) for k in fields.keys()])
        if query is None:
            query = self._default_query.format(types)
        
        cursor = self.execute(query)
        data = self._parse(cursor, fields)
        
        return data
    
    def _parse(self, cursor, fields=None):
        """Docstring"""
        
        if not isinstance(fields, dict):
            raise Exception("'fields' argument should be a dictionary")

        # Define parsers
        parsers = {pkt:PacketParser(pkt,flds) for pkt,flds in fields.items()}
        counter = {pkt:0 for pkt,_ in fields.items()}

        # Loop through rows and parse
        while True:
            # Pull next entry from the database
            row = cursor.fetchone()
            if row is None:
                break
            
            # Don't parse the packet if there isn't a parser defined for it
            pkt_type = PktType(row[6])
            if pkt_type not in parsers.keys():
                continue
            
            # Parse packet
            _ = parsers[pkt_type].parse(row)
            counter[pkt_type] += 1
        
        # Print how many packets were parsed
        for pkt,val in counter.items():
            print(f"Parsed {val} entries of the {pkt.name.capitalize()} packet")
        
        # Unpack data to dataframe
        data = {}
        for pkt,_ in parsers.items():
            rows,columns = parsers[pkt].queue.process()
            data[pkt] = pd.DataFrame(rows, columns=columns)

        return data
    
    # Destructor
    def __del__(self):  
        
        self.disconnect()
        print("Closed old connection") 