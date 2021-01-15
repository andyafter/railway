from app import db


class Line(db.Model):
    __tablename__ = 'railway_line'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column('code', db.String(32))


class Station(db.Model):
    __tablename__ = 'railway_station'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(255))


class StationBelong(db.Model):
    __tablename__ = 'railway_station_belong'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('railway_line.id'))
    station_id = db.Column(db.Integer, db.ForeignKey('railway_station.id'))
    station_code = db.Column('station_code', db.String(32))
    sequence = db.Column('sequence', db.Integer)
    opened_at = db.Column('opened_at', db.String(32))

    line = db.relationship('Line', backref=db.backref('station_belong_line'), lazy=True)
    station = db.relationship('Station', backref=db.backref('station_belong_station'), lazy=True)


class TimeType(db.Model):
    __tablename__ = 'railway_time_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(100))
    weekdays = db.Column(db.String(1000))
    time_intervals = db.Column(db.String(1000))
    change_cost = db.Column('change_cost', db.Integer)


class TimeCost(db.Model):
    __tablename__ = 'railway_time_cost'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('railway_line.id'))
    time_type_id = db.Column(db.Integer, db.ForeignKey('railway_time_type.id'))
    take_cost = db.Column('take_cost', db.Integer)
    is_open = db.Column(db.Integer)

    line = db.relationship('Line', backref=db.backref('time_cost_line_belong'), lazy=True)
    time_type = db.relationship('TimeType', backref=db.backref('time_cost_time_type'), lazy=True)
