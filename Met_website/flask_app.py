import numpy as np

import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, func, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select 

from flask import Flask, json, request, render_template
import sys

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Met_test_db.db")

# reflect an existing database into a new model
Base = declarative_base()

class Paintings(Base):
    __tablename__ = 'Paintings'
    Object_id = Column(Integer, primary_key=True)
    Object_type = Column(String)
    Title = Column(String)
    Date_start = Column(String)
    Date_finish = Column(String)
    Medium = Column(String)
    Met_link = Column(String)
    Artist_id = Column(Integer, ForeignKey('Artists.Artist_id'))
    Dept_id = Column(Integer)
    painting_colors = relationship("Paintings_colors", backref="Paintings")

class Paintings_colors(Base):
    __tablename__ = 'Paintings_colors'
    Object_id = Column(Integer, ForeignKey('Paintings.Object_id'))
    Hex = Column(String)
    Color_name = Column(String, ForeignKey('Colors.Color_name'))
    Size = Column(Float)
    Arb_key = Column(Integer, primary_key = True)

class Colors(Base):
    __tablename__ = 'Colors'
    Color_name = Column(String, primary_key = True)
    Group = Column(String)
    painting_colors = relationship("Paintings_colors", backref="Colors")

class Artists(Base):
    __tablename__ = 'Artists'
    Surname = Column(String)
    First_name =  Column(String)
    Full_name =  Column(String)
    Birth_date =  Column(String)
    Death_date =  Column(String)
    Artist_id = Column (Integer, primary_key = True)
    Image = Column(String)
    Biography = Column(String)
    paintings = relationship("Paintings", backref="Artists")


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

@app.route("/aboutUs")
def about():
    return render_template("aboutUs.html")


#################################################
# Flask Routes - Queries 
#################################################
@app.route("/results", methods=["GET"])
def search():
    
    #get the user color argument
    selected_color = request.args.get('color')
    #print(selected_color, file=sys.stderr)

    #Inspector for debugging - uncomment if needed
    #inspector = inspect(engine)
    #print(inspector.get_table_names(),file=sys.stderr)
    
    #start session and query
    session = Session(engine)

    #return the painting id, title, date, image link and artist name, filtered where color is >= 30 from Paintings_colors
    results = session.query(Paintings.Object_id, Paintings.Title, Paintings.Date_finish, Paintings.Met_link, Artists.Full_name).\
        join(Artists, Paintings.Artist_id == Artists.Artist_id).all()
        #.join(Paintings_colors, Paintings_colors.Object_id == Paintings.Object_id).filter(Paintings_color.Color_name == Colors.Color_name).filter(Colors.Group == selected_color).\filter(func.sum(Paintings_color.Size) > 30 ).all()

    session.close()

    painting_results = []
    for Object_id, Title, Date_finish, Met_link, Full_name in results:
        result_dict = {}
        result_dict["Object_id"] = Object_id
        result_dict["Title"] = Title
        result_dict["Date_finish"] = Date_finish
        result_dict["Image"] = Met_link
        result_dict["Artist_Name"] = Full_name
        painting_results.append(result_dict)

    data = json.dumps(painting_results)
    #print(data,file=sys.stderr)

    return render_template('results.html', results = data)

@app.route("/aboutPainting", methods=["GET"])
def painting():

    #get the selected painting ID
    Selected_painting = request.args.get('id')

    if Selected_painting == "":
        return render_template("404.html", error = "You want to see a painting, but haven't told us which one you want to see yet! Try searching the collection or selecting a painting in the artist's section.")
    
    else: 
        #start session and query
        session = Session(engine)

        #return the painting information
        results = session.query(Paintings.Met_link, Paintings.Title, Paintings.Medium, Paintings.Date_finish, Paintings.Dept_id, Artists.Artist_id, Artists.Full_name, Artists.Birth_date, Artists.Death_date).\
            join(Artists, Paintings.Artist_id == Artists.Artist_id).filter(Paintings.Object_id == Selected_painting).all()
            
        color_results = session.query(Paintings_colors.Hex).filter(Paintings_colors.Object_id == Selected_painting).all()

        session.close()

        painting_info = []
        for Met_link, Title, Medium, Date_finish, Dept_id, Artist_id, Full_name, Birth_date, Death_date in results:
            result_dict = {}
            result_dict["Image"] = Met_link
            result_dict["Title"] = Title
            result_dict["Medium"] = Medium
            result_dict["Date_finish"] = Date_finish
            result_dict["Dept_id"] = Dept_id
            result_dict["Artist_id"] = Artist_id
            result_dict["Artist_Name"] = Full_name
            result_dict["Birth_date"] = Birth_date
            result_dict["Death_date"] = Death_date

        all_colors = list(np.ravel(color_results)) 

        result_dict["Colors"] = all_colors 
        
        painting_info.append(result_dict)
        
        data = json.dumps(painting_info)
        #print(data,file=sys.stderr)
    
        return render_template('aboutPainting.html', results = data, artist_refer = result_dict['Artist_id'], painting_refer = Selected_painting)

@app.route("/aboutArtist", methods=["GET"])
def artist():

    #get the selected painting ID
    Artist_id = request.args.get('id')
    Artist_name = request.args.get('search')

    #if we have an id arguement and it's not assocaited with an "unknown author"
    if Artist_id != "" and Artist_id != 2 or Artist_id != 320 or Artist_id != 684:
        #if we have an id, that means we've been referred by a painting result. Grab the refering painting id to enable the toggler. 
        Painting_referral = request.args.get('referral')
        #start session and query
        session = Session(engine)

        #return the artist's information 
        results = session.query(Artists.Image, Artists.Full_name, Artists.Birth_date, Artists.Death_date, Artists.Biography).\
            filter(Artists.Artist_id == Artist_id).all()
            
        paintings = session.query(Paintings.Object_id, Paintings.Met_link, Paintings.Title).\
            join(Artists, Paintings.Artist_id == Artists.Artist_id ).filter(Artists.Artist_id == Artist_id).all()
        
        artist_collection = []
        for Object_id, Met_link, Title in paintings:
            painting_dict = {}
            painting_dict["Object_id"] = Object_id
            painting_dict["Image"] = Met_link
            painting_dict["Title"] = Title

            color_results = session.query(Paintings_colors.Hex).filter(Paintings_colors.Object_id == Selected_painting).all()
            all_colors = list(np.ravel(color_results))

            painting_dict["Colors"] = all_colors

            artist_collection.append(painting_dict)
        
        session.close()

        artist_info = []
        for Image, Full_name, Birth_date, Death_date, Biography in results:
            result_dict = {}
            result_dict["Image"] = Image
            result_dict["Artist_Name"] = Full_Name
            result_dict["Birth_date"] = Birth_date
            result_dict["Death_date"] = Death_date
            result_dict["Biography"] = Biography
            artist_info.append(result_dict)
        
        artist_data = json.dumps(artist_info)
        #print(artist_data,file=sys.stderr)

        painting_data = json.dumps(artist_collection)
        #print(painting_data,file=sys.stderr)

        return render_template('aboutArtist.html', artist_results = artist_data, painting_results = painting_data, painting_refer = Painting_referral)

    elif Artist_name != "":
        #Jason's stuff goes here? 

    else: 
        return render_template ("404.html", error = "We couldn't seem to find the artist. Either they're unknown or don't exist in the Met's collection. Try again by visiting the homepage or selecting a new painting via search.")

if __name__ == "__main__":
    app.run(debug=True)
