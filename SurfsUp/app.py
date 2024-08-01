# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine,reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return( 
        f"Welcome to the 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    session = Session(engine)
    prcp_result = session.query(Measurement.date,Measurement.prcp).all()
    session.close()
    prcp_dic = {date : prcp
               for date, prcp in prcp_result}
    return jsonify(prcp_dic)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")
    session = Session(engine)
    stations_result = session.query(Measurement.station).distinct().all()
    session.close()
    station_ls = [station[0] for station in stations_result]
    return jsonify(station_ls)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")
    session = Session(engine)
    Recent_date = datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d').date()
    Start_date = Recent_date - timedelta(days=365)
    most_active = session.query(Measurement.station)\
                              .group_by(Measurement.station)\
                              .order_by(func.count(Measurement.station).desc()).first()
    last_one_year = session.query(Measurement.tobs)\
                            .filter(Measurement.station == most_active[0])\
                            .filter(Measurement.date >= Start_date).all()
    session.close()
    last_active_tobs = [tob[0] for tob in last_one_year]
    return jsonify(last_active_tobs)


@app.route("/api/v1.0/<start>")
def start_date(start):
    print(f"Server received request for start date: {start}...")
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                   .filter(Measurement.date >= start_date).all()
    session.close()
    temp_dict = {'TMIN': temps[0][0], 'TAVG': temps[0][1], 'TMAX': temps[0][2]}
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    print(f"Server received request for start date: {start},end date: {end}...")
    session = Session(engine)
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                   .filter(Measurement.date >= start_date)\
                   .filter(Measurement.date <= end_date).all()
    session.close()
    temp_dict = {'TMIN': temps[0][0], 'TAVG': temps[0][1], 'TMAX': temps[0][2]}
    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)

