import numpy as np

import sqlalchemy
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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
               
   )


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/percipitation")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    
    """Return a list of date and percipitation"""
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()
    measurement_dict = {}

    def change(tup, di):
        for a, b in tup: 
            di.setdefault(a, []).append(b) 
        return di
   
    change(results, dictionary)
    #all_measurements = []
    
    return jsonify(measurement_dict)

@app.route("/api/v1.0/tobs")
def tobs_lastyr():
    session = Session(engine)
    """Return a the latest date"""
    tobs_last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close() 
    last_date = list(np.ravel(tobs_last_date))
    
    import datetime as dt
    for date in last_date:
        Dyear, Dmon, Ddate = date.split('-')
        latest_date = dt.date(int(Dyear),int(Dmon),int(Ddate))

    year_ago = latest_date - dt.timedelta(days=365)
    
    session = Session(engine)
    temperature = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
    temperature_list = list(np.ravel(temperature))
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def temp_stat_start(start):
    def temp_cal(start, end_date):
            vac_start_date = datetime.strptime(start, "%Y-%m-%d")
            vac_end_date = session.query(func.max(Measurement.date)).all()[0][0]
            return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= vac_start_date).filter(Measurement.date <= vac_end_date).all()
    enddate = session.query(func.max(Measurement.date)).all()[0][0]
    temps = temp_cal(start, enddate)
    temp_list = list(np.ravel(temps))
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stat_vacydays(start, end):
    def temp_calc_vacy(start, end):
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_vacy = temp_calc_vacy(start, end)
    temp_vacy_list = list(np.ravel(temps_vacy))
    return jsonify(temp_vacy_list)


if __name__ == '__main__':
    app.run(debug=True)
