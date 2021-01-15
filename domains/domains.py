from common.serializable import Serializable


class Station(Serializable):
    def __init__(self, name='', line=None):
        self.name = name
        self.codes = {}
        self.opened_at = ''
        self.sequence = 0
        self.lines = []


class Line(Serializable):
    def __init__(self, name, line_id):
        self.line_id = line_id
        self.name = name
        self.stations = []
        self.transform_stations = []
        self.cost_info = {}
        self.is_round_line = False


class LineTimeCost(Serializable):
    def __init__(self, time_type, type_id):
        self.type_id = type_id
        self.time_type = time_type
        self.weekdays = []
        self.time_intervals = []
        self.take_cost = 0
        self.change_cost = 0
        self.is_open = True


class Station2Station(Serializable):
    def __init__(self, from_station, line, to_station):
        self.from_station = from_station
        self.to_station = to_station
        self.line = line
        self.time_cost = 0
        self.start_time = ''
        self.end_time = ''


class Route(Serializable):
    def __init__(self):
        self.line = ''

        # From Holland Village to Bugis Stations
        self.direction = ''
        self.from_station = None
        self.to_station = None

        # ['CC21', 'CC20', 'CC19']
        self.take_stations = []

        # Unit is minute
        self.time_cost = 0


class SuggestRoute(Serializable):
    def __init__(self):
        # eg. CC->DT->NS
        self.summary = ''

        # ['CC21', 'CC20', 'CC19', 'DT9', 'DT10', 'DT11', 'DT12', 'DT13', 'DT14']
        self.take_stations = []

        self.total_station = 0
        self.total_cost = 0
        self.total_interchange = 0

        # list of Route
        self.routes = []


"""
Take EW line from Boon Lay to Lakeside 
Take EW line from Lakeside to Chinese Garden
Take EW line from Chinese Garden to Jurong East 
Take EW line from Jurong East to Clementi 
Take EW line from Clementi to Dover 
Take EW line from Dover to Buona Vista 

Change from EW line to CC line 

Take CC line from Buona Vista to Holland Village 
Take CC line from Holland Village to Farrer Road 
Take CC line from Farrer Road to Botanic Gardens 

Change from CC line to DT line 

Take DT line from Botanic Gardens to Stevens 
Take DT line from Stevens to Newton 
Take DT line from Newton to Little India
"""

"""
Travel from Holland Village to Bugis Stations travelled: 8 Route: ('CC21', 'CC20', 'CC19', 'DT9', 'DT10', 'DT11', 'DT12', 'DT13', 'DT14')

Take CC line from Holland Village to Farrer Road
Take CC line from Farrer Road to Botanic Gardens

Change from CC line to DT line

Take DT line from Botanic Gardens to Stevens
Take DT line from Stevens to Newton
Take DT line from Newton to Little India
Take DT line from Little India to Rochor
Take DT line from Rochor to Bugis
"""
