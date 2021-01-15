import csv
import logging
import os
from datetime import datetime

from flask import jsonify, request

from app import db
from config import basedir
from controllers import api
from models.models import Line, Station, StationBelong
from services.bfs import MetroLineSearch


@api.route("/search")
def search():
    """
    from: from station name, case-insensitive
    to: to station name, case-insensitive
    time: the time start to take rail way
    order_by: distance or time, distance is shortest distance route without time consideration
    time is shortest distance route with time cost, case-insensitive
    :return: json format route information
    """
    from_station = request.args.get('from', '').title()
    to_station = request.args.get('to', '').title()
    time = request.args.get('time', datetime.now().strftime('%Y-%m-%d %H:%M'))
    order_by = request.args.get('order_by', 'distance').lower()

    search_func = MetroLineSearch(from_station, to_station, time, order_by)

    result = search_func.generate_railway_routes()
    logging.info(result)

    return jsonify(result)


# @api.route("/data")
def gen_data():
    """
    load csv file's data to database
    :return:
    """
    data_file_path = os.path.join(basedir, 'StationMap.csv')
    with open(data_file_path) as file:
        csv_data = csv.reader(file)
        cnt = 0
        lines = {}
        stations = {}
        for row in csv_data:
            if not cnt:
                cnt += 1
                continue

            station_code = row[0].strip()

            line_code = station_code[:2]
            line = lines.get(line_code, '')
            if not line:
                line = Line(code=line_code)
                db.session.add_all([line])
                db.session.commit()
                lines[line_code] = line

            station_name = row[1].strip()
            station = stations.get(station_name, '')
            if not station:
                station = Station(name=station_name)
                db.session.add_all([station])
                db.session.commit()
                stations[station_name] = station

            station_seq = int(str(station_code[2:]))
            opened_at = row[2].strip()

            station_belong = StationBelong(station_id=station.id, line_id=line.id, seq=station_seq, opened_at=opened_at)

            db.session.add_all([station_belong])
            db.session.commit()

    return jsonify({
        'status': 200,
        'data': {
            'info': 'successful'
        }
    })
