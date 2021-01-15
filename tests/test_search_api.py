import json
import unittest
from datetime import datetime

from app import create_app, db


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.success_string = 'success'
        self.failed_string = 'failed'

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    @staticmethod
    def get_api_headers():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _get_response(self, from_station, to_station, order_by='distance', time=None):
        if not time:
            time = datetime.now().strftime('%Y-%m-%d %H:%M')
        url = '/api/search?from={}&to={}&time={}&order_by={}'.format(from_station, to_station, time, order_by)
        return self.client.get(url, headers=self.get_api_headers())

    def test_from_station_not_found(self):
        from_station = 'Yish'
        to_station = 'Cashew'
        response = self._get_response(from_station, to_station)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.failed_string)
        self.assertEqual(json_response['description'], 'Yish  is not contain')

    def test_to_station_not_found(self):
        from_station = 'Dhoby Ghaut'
        to_station = 'Cash'
        response = self._get_response(from_station, to_station)

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.failed_string)
        self.assertEqual(json_response['description'], 'Cash  is not contain')

    def test_shortest_route_without_time_consideration(self):
        from_station = 'Holland Village'
        to_station = 'Bugis'
        response = self._get_response(from_station, to_station)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.success_string)
        self.assertEqual(json_response['description'], '1 route(s) found')
        result_summary = 'Travel from Holland Village to Bugis Stations travelled: 9 Route: (CC21,CC20,CC19,DT9,DT10,DT11,DT12,DT13,DT14)'
        suggest_routes = json_response['suggest_routes']
        self.assertEqual(suggest_routes[0]['summary'], result_summary)

    def test_shortest_route_with_time_cost_in_non_peak_time(self):
        from_station = 'Holland Village'
        to_station = 'Bugis'
        time = datetime.strptime('2021-01-15 13:00', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.success_string)
        self.assertEqual(json_response['description'], '1 route(s) found')
        result_summary = 'Travel from Holland Village to Bugis during non-peak Time: 70 minutes Route: (CC21,CC20,CC19,DT9,DT10,DT11,DT12,DT13,DT14)'
        summary = suggest_routes = json_response['suggest_routes'][0]['summary']
        self.assertEqual(summary, result_summary)

    def test_shortest_route_with_time_cost_in_night_time(self):
        from_station = 'Holland Village'
        to_station = 'Bugis'
        time = datetime.strptime('2021-01-15 22:00', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.success_string)
        self.assertEqual(json_response['description'], '1 route(s) found')
        result_summary = 'Travel from Holland Village to Bugis during night Time: 110 minutes Route: (CC21,CC22,EW21,EW20,EW19,EW18,EW17,EW16,EW15,EW14,EW13,EW12)'
        summary = json_response['suggest_routes'][0]['summary']
        self.assertEqual(summary, result_summary)

    def test_shortest_route_with_time_cost_in_peak_time(self):
        from_station = 'Boon Lay'
        to_station = 'Little India'
        time = datetime.strptime('2021-01-15 06:00', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        result_summary = 'Travel from Boon Lay to Little India during peak Time: 150 minutes Route: (EW27,EW26,EW25,EW24,EW23,EW22,EW21,CC22,CC21,CC20,CC19,DT9,DT10,DT11,DT12)'
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.success_string)
        self.assertEqual(json_response['description'], '1 route(s) found')
        summary = suggest_routes = json_response['suggest_routes'][0]['summary']
        self.assertEqual(summary, result_summary)

    def test_shortest_route_with_time_cost_from_peak_time_to_non_peak_time_then_to_night_time(self):
        from_station = 'Boon Lay'
        to_station = 'Little India'
        time = datetime.strptime('2021-01-15 20:40', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        result_summary = 'Travel from Boon Lay to Little India during peak Time: 160 minutes Route: (EW27,EW26,EW25,EW24,EW23,EW22,EW21,EW20,EW19,EW18,EW17,EW16,NE3,NE4,NE5,NE6,NE7)'
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.success_string)
        self.assertEqual(json_response['description'], '1 route(s) found')
        summary = json_response['suggest_routes'][0]['summary']
        self.assertEqual(summary, result_summary)

    def test_shortest_route_with_time_cost_when_station_not_opened(self):
        from_station = 'Shenton Way'
        to_station = 'Little India'
        time = datetime.strptime('2021-01-15 20:40', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.failed_string)
        self.assertEqual(json_response['description'], 'Shenton Way is not in operation or opened')

    def test_shortest_route_with_time_cost_when_station_not_in_operation(self):
        from_station = 'Changi Airport'
        to_station = 'Little India'
        time = datetime.strptime('2021-01-15 23:40', '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        response = self._get_response(from_station, to_station, order_by='time', time=time)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['result'], self.failed_string)
        self.assertEqual(json_response['description'], 'Changi Airport is not in operation or opened')
