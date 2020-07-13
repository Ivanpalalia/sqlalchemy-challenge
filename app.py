import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
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
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Welcome():
    """List all available api routes."""
    return (
        f"*List of Available Routes:<br/><br/>"


        f"*Date and Precipitation.<br/>"
        f"  /api/v1.0/precipitation<br/><br/>"

        f"*stations.<br/>"
        f"  /api/v1.0/stations<br/><br/>"
       
        f"*temperature observations (TOBS) for the previous year.<br/>"
        f"  /api/v1.0/tobs<br/><br/>"

        f"*the minimum temperature, the average temperature, and the max temperature for a given start range.<br/>"
        f"  /api/v1.0/&ltstart_date&gt<br/><br/>"
        f"example: /api/v1.0/2016-06-06<br/><br/>"

        f"*the minimum temperature, the average temperature, and the max temperature for a given start-end range.<br/>"
        f"  /api/v1.0/&ltstart_date&gt/&ltend_date&gt<br/><br/>"
        f"example: /api/v1.0/2016-06-06/2016-07-07<br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #query for first_date
    first_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # perform calculation for the date 1 year ago from the last data point in the database
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    data_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()
    session.close()
    
    prcp_data = []
    for date, prcp in data_scores:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)
    
    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations"""
    # Query for all stations
    stations = session.query(Station.station, Station.name).all()

    session.close()

    # Create a station dictionary
    all_station = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_station.append(station_dict)

    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # query for active stations
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    """Return list of temperature for previous year (2016)"""
    # Query active station for temp data
    temp_data = session.query(Station.name, Measurement.tobs, Measurement.date).\
                filter(Measurement.date >= '2016-01-01').filter(Measurement.date <= '2016-12-31').\
                filter(Measurement.station == active_station[0][0]).all()

    session.close()

    # Create a station dictionary
    all_temperature = []
    for name, tobs, date in temp_data:
        temp_dict = {}
        temp_dict["Station Name"] = name
        temp_dict["Temp observation"] = tobs
        temp_dict["Date"] = date
        all_temperature.append(temp_dict)

    return jsonify(all_temperature)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    
    session = Session(engine)
       

    """Return tmin, tavg, tmax for starting date"""
    # Query for active station for temp data
    start_date_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()
        
    return jsonify(list(start_date_data))
        
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    """Return tmin, tavg, tmax for a date range"""
    # Query active station for temp data
    date_range_data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                       filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()
    
    return jsonify(list(date_range_data))


if __name__ == '__main__':
    app.run(debug=True)


    