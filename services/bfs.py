from datetime import datetime, timedelta

from domains.domains import Station2Station, SuggestRoute, Route
from services.routes import RailwayData


class MetroLineSearch(object):
    """
    The core algorithm for route search is base on BFS
    key point is regard each line as a node,
    then use the BFS to calculate the route of e start station's line to end station's line
    find the shortest route

    distance is mean shortest distance without time consideration
    time is mean shortest distance with time cost

    shortest distance with time cost algorithm has filter the lines and stations which not operate in Night Hours
    when calculate route time cost also we considered the situation of crossing two hours manner
    such as from Peak Hours to Non-Peak Hours
    """

    def __init__(self, from_station, to_station, time, order_by):
        self.stations = {}
        self.lines = []
        self._min_distance = 0
        self._shortest_routes = []

        self.from_station = from_station
        self.to_station = to_station
        self.time = datetime.strptime(time, '%Y-%m-%d %H:%M')

        self.order_by = order_by if order_by else 'distance'
        self.result = {}

        self._init_data()

    def _init_data(self):
        railway_data = RailwayData(self.time.strftime('%Y-%m-%d'))
        self.stations = railway_data.station_name_dict
        self.lines = railway_data.lines
        self.time_types = railway_data.time_type_name_dict

    def generate_railway_routes(self):

        # confirm station is in station list
        if not self.stations.__contains__(self.from_station):
            return self._generate_failed_result(self.from_station + "  is not contain")
        if not self.stations.__contains__(self.to_station):
            return self._generate_failed_result(self.to_station + "  is not contain")

        if self.from_station == self.to_station:
            return self._generate_failed_result(self.from_station + " and " + self.to_station + ' is the same station')

        start = self.stations[self.from_station]
        end = self.stations[self.to_station]

        # confirm station is running and in operation
        if not self._is_opened_station(self.time, start):
            return self._generate_failed_result(self.from_station + " is not in operation or opened")

        if not self._is_opened_station(self.time, end):
            return self._generate_failed_result(self.to_station + " is not in operation or opened")

        # reset min cost
        self._min_distance = 1000

        # shortest route without time consideration
        line_his = []
        for line in start.lines:
            station_list = []
            line_his.append(line)
            self._search_routes(0, start, line, end, station_list, line_his, self.time)

        # generate route information
        result = self._render_route_info()

        # clear temp list data
        self._shortest_routes.clear()
        return result

    def _search_routes(self, distance, current_station, current_line, end_station, station_list, line_his,
                       current_time):
        # if current distance larger than min distance just return
        if distance > self._min_distance:
            return

        # if current line is not in operation just return
        if not self._is_operated_line(current_time, current_line):
            return

        # successful when current station and end station is belong to line
        if self._is_same_line(current_station, end_station, current_line):

            s2s = Station2Station(current_station, current_line, end_station)
            station_list.append(s2s)

            added_distance = self._calculate_distance(s2s)
            # clear shortest routes when min distance larger than current
            if self._min_distance > distance + added_distance:
                self._min_distance = distance + added_distance
                self._shortest_routes.clear()
                self._shortest_routes.append(station_list.copy())

            station_list.remove(s2s)
            return

        transform = current_line.transform_stations

        # traverse interchangeable station in current line,
        # recurse to find shortest route by BFS algorithm
        for item in transform:
            line = item[0]
            station = item[1]

            # skip those lines which taken
            if line_his.__contains__(line):
                continue

            # skip those lines which not running
            if not self._is_operated_line(current_time, line):
                continue

            line_his.append(line)
            s2s = Station2Station(current_station, current_line, station)
            station_list.append(s2s)
            added_distance = self._calculate_distance(s2s)
            self._calculate_take_cost(station_list)
            interchange_cost = self._get_interchange_cost(s2s.end_time)
            time_cost = s2s.time_cost + interchange_cost
            # reverse call
            current_time += timedelta(minutes=time_cost)
            self._search_routes(distance + added_distance, station, line, end_station, station_list, line_his,
                                current_time)
            current_time -= timedelta(minutes=time_cost)

            # clear the list for sufficient
            line_his.remove(line)
            station_list.remove(s2s)

    def _calculate_take_cost(self, station_list):
        current_time = self.time
        interchange_costs = []
        change_number = len(station_list) - 1
        for idx, item in enumerate(station_list):
            time_cost = 0
            line = item.line
            line_cost = line.cost_info
            item.start_time = current_time
            distance = self._calculate_distance(item)
            take_cost = 0
            for i in range(distance):
                time_type = self._get_time_type(current_time)
                cost_info = line_cost[time_type]
                take_cost = cost_info.take_cost
                time_cost += take_cost
                current_time += timedelta(minutes=take_cost)

            item.time_cost = time_cost
            item.end_time = current_time

            time_type = self._get_time_type(current_time)
            cost_info = line_cost[time_type]
            change_cost = cost_info.change_cost
            if idx < change_number:
                interchange_costs.append(change_cost)
                current_time += timedelta(minutes=change_cost)

        return interchange_costs

    def _get_interchange_cost(self, current_time):
        return self.time_types[self._get_time_type(current_time)].change_cost

    def _get_time_type(self, time: datetime):
        weekday = time.weekday()
        time_h_m = time.strftime('%H:%M')
        for cost in self.time_types.values():
            for interval in cost.time_intervals:
                if interval[0] <= time_h_m < interval[1] and self._is_in_weekday(weekday, cost.weekdays):
                    return cost.time_type

        return self.time_types['Non-Peak'].time_type

    @staticmethod
    def _is_in_weekday(w, weekdays):
        for idx, _ in enumerate(weekdays):
            if idx == w:
                return True
        return False

    def _is_operated_line(self, current_time, line):
        if self.order_by == 'distance':
            return True
        time_type = self._get_time_type(current_time)
        cost = line.cost_info[time_type]
        return True and cost.is_open

    def _is_operated_station(self, current_time, station):

        time_type = self._get_time_type(current_time)
        is_operated = False
        for line in station.lines:
            is_operated = is_operated or self._is_operated_line(current_time, line)
        return is_operated

    def _is_opened_station(self, current_time, station):
        current_date = datetime.strftime(current_time, '%Y-%m-%d')
        is_opened = False
        for code in station.codes.values():
            opened_at = code['opened_at']
            is_opened = is_opened or opened_at < current_date

        if not is_opened:
            return is_opened

        # consider time cost
        if self.order_by == 'time':
            is_opened = is_opened and self._is_operated_station(current_time, station)
        return is_opened

    @staticmethod
    def _calculate_distance(s2s: Station2Station):
        stations = s2s.line.stations
        from_index = stations.index(s2s.from_station)
        to_index = stations.index(s2s.to_station)
        return abs(from_index - to_index)

    def _render_route_info(self):

        route_number = len(self._shortest_routes)
        if not route_number:
            return self._generate_failed_result('Sorry, no route found !')

        self.result['result'] = 'success'
        self.result['description'] = '{} route(s) found'.format(route_number)
        self.result['suggest_routes'] = []

        for innerList in self._shortest_routes:
            interchange_costs = self._calculate_take_cost(innerList)
            suggest_route = SuggestRoute()
            total_interchange = len(interchange_costs)
            suggest_route.total_interchange += total_interchange
            for idx, sts in enumerate(innerList):
                route = Route()
                line = sts.line
                line_id = line.line_id
                route.line = line.name
                line_stations = line.stations

                from_seq = line_stations.index(sts.from_station)
                to_seq = line_stations.index(sts.to_station)

                if from_seq < to_seq:
                    direction = line_stations[0].name + '->' + line_stations[-1].name
                    step = 1
                else:
                    direction = line_stations[-1].name + '->' + line_stations[0].name
                    step = -1

                route.direction = direction
                route.from_station = sts.from_station.name
                route.to_station = sts.to_station.name
                route.time_cost = sts.time_cost

                for i in range(from_seq, to_seq + step, step):
                    station = line_stations[i]
                    code_info = station.codes[line_id]
                    route.take_stations.append({
                        'code': code_info['station_code'],
                        'name': station.name
                    })
                suggest_route.take_stations.extend(route.take_stations)
                suggest_route.total_station += abs(from_seq - to_seq)
                suggest_route.total_cost += sts.time_cost
                if idx < total_interchange:
                    suggest_route.total_cost += interchange_costs[idx]
                suggest_route.routes.append(route)
                suggest_route.summary = self._generate_route_summary(suggest_route)

            self.result['suggest_routes'].append(suggest_route.serialize())

        return self.result

    @staticmethod
    def _is_same_line(station1, station2, line):
        return line.stations.__contains__(station1) and line.stations.__contains__(station2)

    def _generate_route_summary(self, suggest_route):
        stations = suggest_route.take_stations

        from_station = stations[0]['name']
        end_station = stations[-1]['name']
        station_list = [s['code'] for s in stations]
        route = ','.join(station_list)

        if self.order_by == 'time':
            time_type = self._get_time_type(self.time).lower()
            summary = '''Travel from {} to {} during {} Time: {} minutes Route: ({})''' \
                .format(from_station, end_station, time_type, suggest_route.total_cost, route)
        else:
            summary = '''Travel from {} to {} Stations travelled: {} Route: ({})''' \
                .format(from_station, end_station, len(station_list), route)
        return summary

    def _generate_failed_result(self, error_info):
        self.result['result'] = 'failed'
        self.result['description'] = error_info
        self.result['suggest_routes'] = []
        return self.result
