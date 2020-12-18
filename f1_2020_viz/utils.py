#! /usr/bin/env python3

################################################
# Load Dependencies

import ctypes

from collections import namedtuple
from queue import Queue
import pandas as pd

from f1_2020_telemetry.packets import unpack_udp_packet

from .tables import PktClasses

################################################
# Classes

class DataReceiver(Queue):
    
    def __init__(self, fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.columns = fields
        
    def process(self):
        "Unload the queue to a numpy array"
        
        data = []
        for i in range(self.qsize()):
            data.extend(self.get())
        
        # if df & (self.columns != None):
            # data = pd.DataFrame(data, columns=self.columns)
        
        return data, self.columns

    def clear(self):
        "Delete all pending items"
        
        for i in range(self.qsize()):
            _ = self.get()
        

class PacketParser(object):
    """
    F1-2020-telemetry packet parser
    """
    
    _packet_tuple = namedtuple('Packet',['pkt_id', 'timestamp', 'packetFormat', 'gameMajorVersion',
        'gameMinorVersion', 'packetVersion', 'packetId', 'sessionUID',
        'sessionTime', 'frameIdentifier', 'playerCarIndex', 'packet'])
    

    def __init__(self, packet_type, fields=None):
        
        self.type = packet_type
        struct,lengths = get_packet_structure(PktClasses[packet_type]) 
        
        if fields == None:
            fields = list(struct.keys())
        
        self.fields = fields
        paths,order = get_field_paths(fields, packet_type)
        
        self.field_lengths = lengths
        self.pkt_length = {key:lengths[key] for key,_ in paths.items()}
        self.field_paths = paths
        self.field_order = order
        
        max_len = max(self.pkt_length.values())
        if max_len > 1:
            self._template = [[i] for i in range(max_len)]
            self.field_order = ['vehicleId', *self.field_order]
            
        else:
            self._template = [[]]
        
        self.queue = DataReceiver(fields=self.field_order)
        
    def parse(self, row):
        """Parse the packet and return a list"""
        
        row = self._packet_tuple(*row)
        packet = unpack_udp_packet(row.packet)
        data = self.unpack_fields(packet)
        
        self.queue.put(data)
        
        return data
    
    def getattrs(self, obj, attrs):
        """Extension of 'getattr' for pulling fields from C-type structs"""
        
        return [getattr(obj,attr) if self.field_lengths[attr]==1 else [*getattr(obj,attr)] for attr in attrs]
        
    def unpack_fields(self, packet):
        """Get specified fields from a F1 packet"""
        
        data = [i[:] for i in self._template] # copy the template
        length = len(data)
        
        # Loop through keys in the dict of fields
        for key,attrs in self.field_paths.items():
            subpack = getattr(packet, key, packet)
            
            # If the subpacket is an array (has an entry for each vehicle)
            if self.pkt_length[key] > 1:
                vals = [self.getattrs(subrow, attrs) for subrow in subpack]
                _ = [data[i].extend(vals[i]) for i in range(length)]

            # Else, if the subpacket is a solitary object
            else:
                val = self.getattrs(subpack, attrs)
                _ = [data[i].extend(val) for i in range(length)]
                
        return data

def get_packet_structure(packet, prev_level=[]):
    "Docstring"
    
    values = {}; lengths ={}
    fields = None; length = None
    
    if hasattr(packet, '_fields_'):
        fields = packet._fields_
        
    elif hasattr(packet, '_type_'):
        if hasattr(packet._type_, '_fields_'):
            fields = packet._type_._fields_
        
    if fields != None:
        for name,cls in fields:
            layer = [name,*prev_level]
            
            if hasattr(cls,'_length_'):
                if cls._type_ != ctypes.c_char:
                    length = cls._length_
            else:
                length = 1
            
            vals,lens = get_packet_structure(cls, layer)
            
            lengths[name] = length
            if len(vals)==0:
                values[name] = [*prev_level,name]
        
            values.update(vals)
            lengths.update(lens)
            
            
    return values,lengths

def get_field_paths(fields, packet_type):
    """Find the location of fields (nested path) in a packet"""

    pkt_structure,_ = get_packet_structure(PktClasses[packet_type])

    paths = [pkt_structure[fld] for fld in fields]
    # nfields = [PktStructure[packet_type][fld] for fld in fields]
            
    tree = {}
    for p in paths:
        k,*v = p
        if k not in tree:
            tree[k] = []
        
        tree[k].extend(v)

    field_paths = tree
    field_order = [v for key,val in tree.items() for v in val]
    
    return field_paths,field_order