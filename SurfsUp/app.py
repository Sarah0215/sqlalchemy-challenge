# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
most_recent_date = '2017-08-23'
one_year_ago=datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=366)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-01<br/>"
        f"/api/v1.0/2015-08-01/2016-08-01"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
   
    """ retrieve only the last 12 months of data"""
    # Query for the last 12 months of data
    last_year_data = session.query(Measurement.date,Measurement.prcp).\
                        filter(Measurement.date >= one_year_ago).\
                        order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    last_year_list = list(np.ravel(last_year_data))

    return jsonify(last_year_list)


@app.route("/api/v1.0/stations")
def stations():
   
    """ retrieve the list of stations"""
    # Query for the list of station
    stations_data=session.query(Station.station,func.count(Measurement.station))\
                                .join(Measurement, Station.station == Measurement.station)\
                                .group_by(Station.station)\
                                .order_by(func.count(Station.station).desc()).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations_data))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
   
    """ retrieve the temperature of the most active station"""
    # Query for the temperature of most active station
    date_tobs_data=session.query(Measurement.date,Measurement.tobs)\
                                .filter(Measurement.date >= one_year_ago, Measurement.station=="USC00519281").all()

    # Convert list of tuples into normal list
    date_tobs_list = list(np.ravel(date_tobs_data))

    return jsonify(date_tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start,end=None):
    """Fetch the start date and end date"""

    if end:
        temp_data= session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
                .filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        temp_data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))\
                .filter(Measurement.date >= start).all()

    session.close()

    temp_stats = {
        "TMIN": temp_data[0][0],
        "TAVG": temp_data[0][1],
        "TMAX": temp_data[0][2] 
    }
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)


