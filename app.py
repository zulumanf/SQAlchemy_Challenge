# 1. import Flask
from flask import Flask
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite/")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/enter requested start date in yyyy-mm-dd<br/>"
        f"/api/v1.0/enter requested start date in yyyy-mm-dd/enter requested end date in yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to obtain Precipitation information
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Add data obtained into a list
    prcp_list = []
    for date, prcp in prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query all stations
    stations = session.query(Station.id, Station.name).all()
    session.close()
    # Create a dictionary from the row data and append to a list
    station_info = []
    for id, name in stations:
        station_dict = {}
        station_dict["Station ID"] = id
        station_dict["Station Name"] = name
        station_info.append(station_dict)
    return jsonify(station_info)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query to obtain Temperatures information and most recent date
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    tobs_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
    session.close()
    
    # Add data obtained into a list
    tobs_info = []
    for date, tobs in tobs_year:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_info.append(tobs_dict)
    return jsonify(tobs_info)


#     Query most recent and oldest date in dataset    #

# Create our session (link) from Python to the DB
session = Session(engine)
start_dt = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
start_dt = start_dt[0].replace("-", "")
end_dt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
end_dt = end_dt[0].replace("-", "")
session.close()

@app.route("/api/v1.0/<start_date>")
def solo_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query min/max/avg tobs from a start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()  
    session.close()
    # Create a dictionary for min/max/avg tobs
    date_list = []
    for min, avg, max in results:
        date_list_dict = {}
        date_list_dict["min_temp"] = min
        date_list_dict["avg_temp"] = avg
        date_list_dict["max_temp"] = max
        date_list.append(date_list_dict) 
    return jsonify(date_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def two_dates(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query min/max/avg tobs from a start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()  
    # Create a dictionary for min/max/avg tobs between the two dates
    two_date_list = []
    for min, avg, max in results:
        two_date_dict = {}
        two_date_dict["Min. Temp (F)"] = min
        two_date_dict["Avg. Temp (F)"] = avg
        two_date_dict["Max Temp (F)"] = max
        two_date_list.append(two_date_dict) 
    return jsonify(two_date_list)

if __name__ == '__main__':
    app.run(debug=True)


