#! /usr/bin/env python3

################################################
# Load Dependencies

from enum import Enum, IntEnum, unique

from f1_2020_telemetry.packets import (
    unpack_udp_packet, 
    PacketLapData_V1, 
    PacketCarSetupData_V1,
    PacketCarStatusData_V1,
    PacketCarTelemetryData_V1,
    PacketEventData_V1,
    PacketLobbyInfoData_V1,
    PacketMotionData_V1,
    PacketParticipantsData_V1,
    PacketSessionData_V1,
    PacketFinalClassificationData_V1
)

################################################
### UDP Packet Spec Tables

# Set up main enum, for referencing basically everything
class PktType(Enum): 
    MOTION = 0
    SESSION = 1
    LAPDATA = 2
    EVENT = 3
    PARTICIPANTS = 4
    CARSETUPS = 5
    CARTELEMETRY = 6
    CARSTATUS = 7
    CLASSIFICATION = 8
    LOBBY = 9

# Session types
SessionType = {
    0: 'unknown',
    1: 'Practice 1',
    2: 'Practice 2',
    3: 'Practice 3',
    4: 'Short Practice',
    5: 'Quali 1',
    6: 'Quali 2',
    7: 'Quali 3',
    8: 'Short Quali',
    9: 'One Shot Quali',
    10: 'Race',
    11: 'Race 2',
    12: 'Time Trial'
}
    
# Drivers
DriverIDs = {
    0: ("Carlos Sainz", "SAI"),
    1: ("Daniil Kvyat", "KVY"),
    2: ("Daniel Ricciardo", "RIC"),
    6: ("Kimi Räikkönen", "RAI"),
    7: ("Lewis Hamilton", "HAM"),
    9: ("Max Verstappen", "VER"),
    10: ("Nico Hulkenberg", "HUL"),
    11: ("Kevin Magnussen", "MAG"),
    12: ("Romain Grosjean", "GRO"),
    13: ("Sebastian Vettel", "VET"),
    14: ("Sergio Perez", "PER"),
    15: ("Valtteri Bottas", "BOT"),
    17: ("Esteban Ocon", "OCO"),
    19: ("Lance Stroll", "STR"),
    20: ("Arron Barnes", "BAR"),
    21: ("Martin Giles", "GIL"),
    22: ("Alex Murray", "MUR"),
    23: ("Lucas Roth", "ROT"),
    24: ("Igor Correia", "COR"),
    25: ("Sophie Levasseur", "LEV"),
    26: ("Jonas Schiffer", "SCH"),
    27: ("Alain Forest", "FOR"),
    28: ("Jay Letourneau", "LET"),
    29: ("Esto Saari", "SAA"),
    30: ("Yasar Atiyeh", "ATI"),
    31: ("Callisto Calabresi", "CAL"),
    32: ("Naota Izum", "IZU"),
    33: ("Howard Clarke", "CLA"),
    34: ("Wilhelm Kaufmann", "KAU"),
    35: ("Marie Laursen", "LAU"),
    36: ("Flavio Nieves", "NIE"),
    37: ("Peter Belousov", "BEL"),
    38: ("Klimek Michalski", "MIC"),
    39: ("Santiago Moreno", "MOR"),
    40: ("Benjamin Coppens", "COP"),
    41: ("Noah Visser", "VIS"),
    42: ("Gert Waldmuller", "WAL"),
    43: ("Julian Quesada", "QUE"),
    44: ("Daniel Jones", "JON"),
    45: ("Artem Markelov", "MAR"),
    46: ("Tadasuke Makino", "MAK"),
    47: ("Sean Gelael", "GEL"),
    48: ("Nyck De Vries", "VRI"),
    49: ("Jack Aitken", "AIT"),
    50: ("George Russell", "RUS"),
    51: ("Maximilian Günther", "GUN"),
    52: ("Nirei Fukuzumi", "FUK"),
    53: ("Luca Ghiotto", "GHI"),
    54: ("Lando Norris", "NOR"),
    55: ("Sérgio Sette Câmara", "CAM"),
    56: ("Louis Delétraz", "DEL"),
    57: ("Antonio Fuoco", "FUO"),
    58: ("Charles Leclerc", "LEC"),
    59: ("Pierre Gasly", "GAS"),
    62: ("Alexander Albon", "ALB"),
    63: ("Nicholas Latifi", "LAT"),
    64: ("Dorian Boccolacci", "BOC"),
    65: ("Niko Kari", "KAR"),
    66: ("Roberto Merhi", "MER"),
    67: ("Arjun Maini", "MAI"),
    68: ("Alessio Lorandi", "LOR"),
    69: ("Ruben Meijer", "MEI"),
    70: ("Rashid Nair", "NAI"),
    71: ("Jack Tremblay", "TRE"),
    74: ("Antonio Giovinazzi", "GIO"),
    75: ("Robert Kubica", "KUB"),
    78: ("Nobuharu Matsushita", "MAT"),
    79: ("Nikita Mazepin", "MAZ"),
    80: ("Guanyu Zhou", "ZHO"),
    81: ("Mick Schumacher", "SCH"),
    82: ("Callum Ilott", "ILO"),
    83: ("Juan Manuel Correa", "COR"),
    84: ("Jordan King", "KIN"),
    85: ("Mahaveer Raghunathan", "RAG"),
    86: ("Tatiana Calderón", "CAL"),
    87: ("Anthoine Hubert", "HUB"),
    88: ("Giuliano Alesi", "ALE"),
    89: ("Ralph Boschung", "BOS"),
}

################################################
### Related to f1-2020-telemetry

# Link the packet types to the enum
PktClasses = {
    PktType.MOTION: PacketMotionData_V1,
    PktType.SESSION: PacketSessionData_V1,
    PktType.LAPDATA: PacketLapData_V1,
    PktType.EVENT: PacketEventData_V1,
    PktType.PARTICIPANTS: PacketParticipantsData_V1,
    PktType.CARSETUPS: PacketCarSetupData_V1,
    PktType.CARTELEMETRY: PacketCarTelemetryData_V1,
    PktType.CARSTATUS: PacketCarStatusData_V1,
    PktType.CLASSIFICATION: PacketFinalClassificationData_V1,
    PktType.LOBBY: PacketLobbyInfoData_V1
}

################################################
### Package specific

TeamColours = {
    0 : (0,210,190), # 'Mercedes',
    1 : (192,0,0), # 'Ferrari',
    2 : (6,0,239), # 'Red Bull Racing',
    3 : (0,130,250), # 'Williams',
    4 : (245,150,200), # 'Racing Point',
    5 : (255,245,0), # 'Renault',
    6 : (200,200,200), # 'Toro Rosso',
    7 : (120,120,120), # 'Haas',
    8 : (255,135,0), # 'McLaren',
    9 : (150,0,0), # 'Alfa Romeo',
    255 : (0, 255, 0) # 'MyTeam
}
for key, rgb in TeamColours.items():
    TeamColours[key] = tuple(c/255 for c in rgb)
    

Fields = {
    PktType.PARTICIPANTS: {
        'header': ['frameIdentifier'],
        'carStatusData': ['tyresWear', 'visualTyreCompound', 'tyresAgeLaps', 'fuelInTank', 'fuelRemainingLaps']
    },
    PktType.LAPDATA: {
        'header': ['frameIdentifier'],
        'lapData': ['lastLapTime', 'sector1TimeInMS', 'sector2TimeInMS', 'bestLapTime', 
                    'bestLapNum', 'currentLapNum', 'pitStatus', 'currentLapInvalid', 'resultStatus']
    },
    PktType.CARSTATUS: {
        'header': ['frameIdentifier'],
        'carStatusData': ['tyresWear', 'visualTyreCompound', 'tyresAgeLaps', 'fuelInTank', 'fuelRemainingLaps']
    }
}

