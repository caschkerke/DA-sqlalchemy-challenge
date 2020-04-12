import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# creating session(link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes (Dates formatted as %Y-%m-%d):<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""

    results = session.query(measurement.date, measurement.prcp)\
                        .order_by(measurement.date)\
                        .all()

    # precip = []
    # for r in results:
    #     precip_dict = {}
    #     precip_dict["Date"] = r.date
    #     precip_dict["Prcp"] = r.prcp
    #     precip.append(precip_dict)

    return jsonify(dict(results))

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset."""

    results = session.query(station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    """Return a JSON list of temperature observations (TOBS) for the previous year."""

    # most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365) 

    results = session.query(measurement.tobs, measurement.date)\
                        .filter(measurement.date >= year_ago, measurement.station == "USC00519281")\
                        .order_by(measurement.tobs)\
                        .all()

    return jsonify(results)

def calc_temps_start(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
       start_date (string): A date string in the format %Y-%m-%d
       end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(measurement.tobs),\
                        func.avg(measurement.tobs), \
                        func.max(measurement.tobs))\
                        .filter(measurement.date >= start_date)\
                        .all()

@app.route("/api/v1.0/<start>")
def start_date(start):

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range."""

    results = calc_temps_start(start)

    res_list = list(np.ravel(results))

    res_min = res_list[0]
    res_avg = res_list[1]
    res_max = res_list[2]

    res = {'Temp Min':res_min, 'Temp Avg':res_avg, 'Temp Max':res_max}

    return jsonify(res)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(measurement.tobs),\
                        func.avg(measurement.tobs),\
                        func.max(measurement.tobs))\
                        .filter(measurement.date >= start_date)\
                        .filter(measurement.date <= end_date)\
                        .all()


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""

    results = calc_temps(start, end)

    res_list = list(np.ravel(results))

    res_min = res_list[0]
    res_avg = res_list[1]
    res_max = res_list[2]

    res = {'Temp Min':res_min, 'Temp Avg':res_avg, 'Temp Max':res_max}

    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)
