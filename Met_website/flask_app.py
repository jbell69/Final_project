import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, json, request, render_template, jsonify
import sys
from sqlalchemy import inspect

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Met_test_db.db")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Paintings = Base.classes.Paintings
Artists = Base.classes.Artists
#Painting_colors = Base.classes.Paintings_colors
#Departments = Base.classes.Departments
#Colors = Base.classes.Colors 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes - Main Pages
#################################################
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/search")
def searchpage():
    return render_template("search.html")

@app.route("/aboutPaintings")
def aboutpaintingpage():
    return render_template("aboutPainting.html")

#################################################
# Flask Routes - Queries 
#################################################
@app.route("/results", methods=["GET"])
def search():
    
    #get the user color arguement
    selected_color = request.args.get('color')
    #print(selected_color, file=sys.stderr)
    
    #inspector = inspect(engine)
    #print(inspector.get_table_names(),file=sys.stderr)
    
    #start session and query
    session = Session(engine)
    results = session.query(Paintings.Object_id, Paintings.Title, Paintings.Date_finish, Paintings.Met_link).all()
    session.close()

    painting_results = []
    for Object_id, Title, Date_finish, Met_link in results:
        result_dict = {}
        result_dict["Object_id"] = Object_id
        result_dict["Title"] = Title
        result_dict["Date_finish"] = Date_finish
        result_dict["Image"] = Met_link
        #result_dict["Artist_Name"] = Full_name
        painting_results.append(result_dict)

    #data = jsonify(painting_results[0])
    #print(json.dumps(painting_results))
    data = json.dumps(painting_results)
    #print(data,file=sys.stderr)

    return render_template('results.html', results = data)

if __name__ == "__main__":
    app.run(debug=True)

