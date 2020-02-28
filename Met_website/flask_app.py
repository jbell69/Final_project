import numpy as np

import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, create_engine, func, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select 
from sqlalchemy import func

from flask import Flask, json, request, render_template
import sys

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Met_final_db.db")

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
    Dept_id = Column(Integer, ForeignKey('Departments.Dept_id'))
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
    Biography = Column(String)
    Image_link = Column(String)
    paintings = relationship("Paintings", backref="Artists")

class Departments(Base):
    __tablename__ = 'Departments'
    Dept_name = Column(String)
    Dept_id = Column (Integer, primary_key = True)
    paintings = relationship("Paintings", backref="Departments")

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

@app.route("/about")
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
    results_q = session.query(Paintings.Object_id, Paintings.Title, Paintings.Date_finish, Paintings.Met_link, Artists.Full_name, func.sum(Paintings_colors.Size)).\
        join(Artists, Paintings.Artist_id == Artists.Artist_id).join(Paintings_colors, Paintings_colors.Object_id == Paintings.Object_id).\
            join(Colors, Paintings_colors.Color_name == Colors.Color_name).filter(Colors.Group == selected_color).group_by(Paintings.Object_id).having(func.sum(Paintings_colors.Size) > 20)
    
    results = results_q.order_by(func.sum(Paintings_colors.Size).desc()).all()
    
    
    session.close()

    painting_results = []
    for Object_id, Title, Date_finish, Met_link, Full_name, Size in results:
        result_dict = {}
        result_dict["Object_id"] = Object_id
        result_dict["Title"] = Title
        result_dict["Date_finish"] = Date_finish
        result_dict["Image"] = Met_link
        result_dict["Artist_Name"] = Full_name
        result_dict["Size"] = Size
        painting_results.append(result_dict)

    data = json.dumps(painting_results)
    #print(data,file=sys.stderr)

    return render_template('results.html', results = data, selected_color = selected_color)

@app.route("/aboutPainting", methods=["GET"])
def painting():

    #get the selected painting ID
    Selected_painting = request.args.get('id')

    if Selected_painting == "None":
        return render_template("404.html", error = "You want to see a painting, but haven't told us which one you want to see yet! Try searching the collection or selecting a painting in the artist's section.")
    


    else: 
        #start session and query
        session = Session(engine)

        #return the painting information
        results = session.query(Paintings.Object_id, Paintings.Met_link, Paintings.Title, Paintings.Medium, Paintings.Date_finish, Paintings.Dept_id, Artists.Artist_id, Artists.Full_name, Artists.Birth_date, Artists.Death_date).\
            join(Artists, Paintings.Artist_id == Artists.Artist_id).filter(Paintings.Object_id == Selected_painting).all()
            
        color_results = session.query(Paintings_colors.Hex).filter(Paintings_colors.Object_id == Selected_painting).all()

        session.close()

        painting_info = []
        for Object_id, Met_link, Title, Medium, Date_finish, Dept_id, Artist_id, Full_name, Birth_date, Death_date in results:
            result_dict = {}
            result_dict["Object_id"] = Object_id
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

@app.route("/aboutArtist", methods=["GET", "POST"])
def artist():

    #get the selected painting ID
    Artist_id = request.args.get('id')
    #Artist_name = request.form['artist']

    print(Artist_id, file=sys.stderr)
    #print(Artist_name, file=sys.stderr)

    # if Artist_name != "None":
    #     session = Session(engine)
    #     id_Lookup = session.query(Artists.Artist_id).filter(Artists.Full_name.like('%'+Artist_name+'%')).one()
    #     Artist_id = id_Lookup[0]
    #     print(Artist_id, file=sys.stderr)
    #     session.close()

    #if we have an id arguement and it's not assocaited with an "unknown author"
    if Artist_id == 2 or Artist_id == 320 or Artist_id == 684:
        return render_template ("404.html", error = "We couldn't seem to find the artist. Either they're unknown or don't exist in the Met's collection. Try again by visiting the homepage or selecting a new painting via search.")

    else:
        #if we have an id, that means we've been referred by a painting result. Grab the refering painting id to enable the toggler. 
        Painting_referral = request.args.get('referral')
        #start session and query
        session = Session(engine)

        #return the artist's information 
        results = session.query(Artists.Full_name, Artists.Birth_date, Artists.Death_date, Artists.Biography, Artists.Image_link).\
            filter(Artists.Artist_id == Artist_id).all()
   
        paintings = session.query(Paintings.Object_id, Paintings.Met_link, Paintings.Title).\
            join(Artists, Paintings.Artist_id == Artists.Artist_id ).filter(Artists.Artist_id == Artist_id).all()
        
        artist_collection = []
        for Object_id, Met_link, Title in paintings:
            painting_dict = {}
            painting_dict["Object_id"] = Object_id
            painting_dict["Image"] = Met_link
            painting_dict["Title"] = Title

            color_results = session.query(Paintings_colors.Hex).filter(Paintings_colors.Object_id == Object_id).all()
            all_colors = list(np.ravel(color_results))

            painting_dict["Colors"] = all_colors

            artist_collection.append(painting_dict)
        
        session.close()

        artist_info = []
        for Full_name, Birth_date, Death_date, Biography, Image_link in results:
            result_dict = {}
            result_dict["Artist_Name"] = Full_name
            result_dict["Birth_date"] = Birth_date
            result_dict["Death_date"] = Death_date
            result_dict["Biography"] = Biography
            result_dict["Image"] = Image_link
            artist_info.append(result_dict)
        
        artist_data = json.dumps(artist_info)
        print(artist_data,file=sys.stderr)

        painting_data = json.dumps(artist_collection)
        #print(painting_data,file=sys.stderr)

        return render_template('aboutArtist.html', artist_results = artist_data, painting_results = painting_data, painting_refer = Painting_referral)

@app.route("/SearchArtist", methods=["GET", "POST"])
def SearchArtist():

    #get the selected painting ID
    Artist_id = request.args.get('id')
    Artist_name = request.form['artist']

    print(Artist_id, file=sys.stderr)
    print(Artist_name, file=sys.stderr)

    if Artist_name != "None":
        session = Session(engine)
        try: 
            id_Lookup = session.query(Artists.Artist_id).filter(Artists.Full_name.like('%'+Artist_name+'%')).one()
            Artist_id = id_Lookup[0]
            print(Artist_id, file=sys.stderr)
        except:
            Artist_id = 2
        session.close()

    #if we have an id arguement and it's not assocaited with an "unknown author"
    if Artist_id == 2 or Artist_id == 320 or Artist_id == 684:
        return render_template ("404.html", error = "We couldn't seem to find the artist. They might be unknown or don't exist in the Met's collection. Try again by refining your search on the homepage or by selecting a painting via search.")

    else:
        #if we have an id, that means we've been referred by a painting result. Grab the refering painting id to enable the toggler. 
        Painting_referral = request.args.get('referral')
        #start session and query
        session = Session(engine)

        #return the artist's information 
        results = session.query(Artists.Full_name, Artists.Birth_date, Artists.Death_date, Artists.Biography, Artists.Image_link).\
            filter(Artists.Artist_id == Artist_id).all()
   
        paintings = session.query(Paintings.Object_id, Paintings.Met_link, Paintings.Title).\
            join(Artists, Paintings.Artist_id == Artists.Artist_id ).filter(Artists.Artist_id == Artist_id).all()
        
        artist_collection = []
        for Object_id, Met_link, Title in paintings:
            painting_dict = {}
            painting_dict["Object_id"] = Object_id
            painting_dict["Image"] = Met_link
            painting_dict["Title"] = Title

            color_results = session.query(Paintings_colors.Hex).filter(Paintings_colors.Object_id == Object_id).all()
            all_colors = list(np.ravel(color_results))

            painting_dict["Colors"] = all_colors

            artist_collection.append(painting_dict)
        
        session.close()

        artist_info = []
        for Full_name, Birth_date, Death_date, Biography, Image_link in results:
            result_dict = {}
            result_dict["Artist_Name"] = Full_name
            result_dict["Birth_date"] = Birth_date
            result_dict["Death_date"] = Death_date
            result_dict["Biography"] = Biography
            result_dict["Image"] = Image_link
            artist_info.append(result_dict)
        
        artist_data = json.dumps(artist_info)
        print(artist_data,file=sys.stderr)

        painting_data = json.dumps(artist_collection)
        #print(painting_data,file=sys.stderr)

        return render_template('aboutArtist.html', artist_results = artist_data, painting_results = painting_data, painting_refer = Painting_referral)


@app.route("/overview")
def overview():

    session = Session(engine)

    all_hex = session.query(Paintings_colors.Hex.distinct()).group_by(Paintings_colors.Hex).join(Colors, Paintings_colors.Color_name == Colors.Color_name).\
        filter(Colors.Group != "Black").having(func.sum(Paintings_colors.Size) > 20).order_by(Colors.Group).all()

    colors_summary = session.query(Paintings_colors.Color_name, func.sum(Paintings_colors.Size)).group_by(Paintings_colors.Color_name).all()

    mediums = session.query(Paintings.Medium, func.count(Paintings.Medium)).group_by(Paintings.Medium).\
        having(func.count(Paintings.Medium) > 10).all()

    dept_q = session.query(Departments.Dept_name, func.count(Paintings.Dept_id)).join(Paintings, Departments.Dept_id == Paintings.Dept_id).\
        group_by(Paintings.Dept_id).all()

    artist_results = session.query (Artists.Full_name, func.count(Paintings.Artist_id)).join(Paintings, Artists.Artist_id == Paintings.Artist_id).\
        group_by(Artists.Full_name).order_by(func.count(Paintings.Artist_id).desc()).limit(6).all()

    # color_groups = session.query(Colors.Group, func.sum(Paintings_colors.Size)).join(Paintings_colors, Colors.Color_name == Paintings_colors.Color_name).\
    #     group_by(Colors.Group).all()

    session.close()
    
    hex_list = [{"Hex": list(np.ravel(all_hex))}]
    hex_colors = json.dumps(hex_list)

    colors_sub = []
    for Color_name, Size in colors_summary:
        sub_dict = {}
        sub_dict["Color_name"] = Color_name
        sub_dict["Size"] = Size
        colors_sub.append(sub_dict)

    sub_color_data = json.dumps(colors_sub)
    #print(sub_color_data,file=sys.stderr)

    painting_mediums = []
    for Medium, Count in mediums:
        med_dict = {}
        med_dict["Medium"] = Medium
        med_dict["Count"] = Count
        painting_mediums.append(med_dict)
    
    top_mediums = json.dumps(painting_mediums)
    #print(painting_mediums, file=sys.stderr)

    painting_departments = []
    for Department, Count in dept_q:
        dept_dict = {}
        dept_dict["Department"] = Department
        dept_dict["Count"] = Count
        painting_departments.append(dept_dict)
    
    department_summary = json.dumps(painting_departments)

    artist_summary = []
    for Full_name, Count in artist_results:
        artist_dict = {}
        artist_dict["Full_name"] = Full_name
        artist_dict["Count"] = Count
        artist_summary.append(artist_dict)
    
    top_artists = json.dumps(artist_summary)

    return render_template('overview.html', hex_colors = hex_colors, group_colors = sub_color_data, top_mediums = top_mediums, department_summary = department_summary, top_artists = top_artists)
        
if __name__ == "__main__":
    app.run(debug=True)
