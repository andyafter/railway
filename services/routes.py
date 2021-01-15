from datetime import datetime

from domains.domains import Line, Station, LineTimeCost
from models.models import Line as ModelLine, Station as ModelStation, StationBelong, TimeType, TimeCost


class RailwayData(object):
    """
    This class just cook data for BFS algorithm from sqlite database
    """

    def __init__(self, start_date):
        self.station_name_dict = {}
        self.lines = []
        self.station_code_dict = {}
        self.station_id_dict = {}
        self.line_id_dict = {}
        self.line_name_dict = {}
        self.time_type_dict = {}
        self.time_type_name_dict = {}
        self.start_date = start_date
        self.load()

    def load(self):
        lines = ModelLine.query.all()
        for item in lines:
            line_name = item.code
            line_id = item.id
            line = Line(line_name, line_id)
            self.line_name_dict[line_name] = line
            self.line_id_dict[line_id] = line
            self.lines.append(line)

        self._load_stations()

        stations_in_line = self._load_station_belong()

        for line in self.lines:
            line_id = line.line_id
            stations = stations_in_line[line_id]
            line.stations = stations

        self._refill_line_in_station()
        self._load_line_cost()

    def _load_stations(self):
        stations = ModelStation.query.all()

        for item in stations:
            station_id = item.id
            station = Station(name=item.name)

            self.station_id_dict[station_id] = station
            self.station_name_dict[item.name] = station

    def _load_station_belong(self):
        station_belongs = StationBelong.query.order_by(StationBelong.line_id, StationBelong.sequence).all()
        stations_in_line = {}
        for belong in station_belongs:
            line_id = belong.line_id
            station_id = belong.station_id

            line_stations = stations_in_line.get(line_id, [])

            station = self.station_id_dict[station_id]
            opened_at = datetime.strptime(belong.opened_at, '%Y-%m-%d').strftime('%Y-%m-%d')
            station_code = belong.station_code
            station_sequence = belong.sequence

            station.codes[line_id] = {
                'line_id': line_id,
                'opened_at': opened_at,
                'station_code': station_code,
                'station_sequence': station_sequence
            }

            line_stations.append(station)

            self.station_code_dict[station_code] = station
            stations_in_line[line_id] = line_stations

        return stations_in_line

    def _refill_line_in_station(self):

        for line in self.lines:
            interchangeable_stations = []
            stations = line.stations
            for idx, station in enumerate(stations):
                # station_name = station.name
                station.lines.append(line)
                # self.station_name_dict[station_name].lines[line.name] = (line, idx + 1)

                codes = station.codes
                if len(codes) <= 1:
                    continue

                for code in codes.values():
                    line_id = code['line_id']
                    station_code = code['station_code']
                    interchange_line = self.line_id_dict[line_id]
                    interchange_station = self.station_code_dict[station_code]
                    interchangeable_stations.append((interchange_line, interchange_station))

            line.transform_stations = interchangeable_stations

    def _load_line_cost(self):
        time_types = TimeType.query.all()
        time_type_dict = {}
        for time_type in time_types:

            if time_type.weekdays:
                weekdays = time_type.weekdays.split(',')
            else:
                weekdays = []
            time_intervals = []
            if time_type.time_intervals:
                intervals = time_type.time_intervals.split(',')
                for interval in intervals:
                    time_intervals.append(tuple(interval.split('-')))
            time_cost = LineTimeCost(time_type.name, time_type.id)
            time_cost.time_intervals = time_intervals
            time_cost.weekdays = weekdays
            time_cost.change_cost = time_type.change_cost
            time_type_dict[time_type.id] = time_cost
            self.time_type_name_dict[time_type.name] = time_cost

        time_cost = TimeCost.query.all()
        time_cost_dict = {}
        for cost in time_cost:
            line_id = cost.line_id
            line_cost = time_cost_dict.get(line_id, [])
            line_cost.append(cost)
            time_cost_dict[line_id] = line_cost

        for line in self.lines:
            line_id = line.line_id
            line_costs = time_cost_dict[line_id]
            for cost in line_costs:
                time_type_id = cost.time_type_id
                time_type = time_type_dict[time_type_id]

                line_cost = LineTimeCost(time_type.time_type, time_type.type_id)
                line_cost.is_open = cost.is_open
                line_cost.take_cost = cost.take_cost
                line_cost.change_cost = time_type.change_cost
                line_cost.weekdays = time_type.weekdays
                line_cost.time_intervals = time_type.time_intervals

                line.cost_info[time_type.time_type] = line_cost
