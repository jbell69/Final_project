#dependancies

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
import os
import urllib
import webcolors 

def get_image(image_path):

    resp = urllib.request.urlopen(image_path)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_modify = cv2.resize(image, (400,400), interpolation = cv2.INTER_AREA)
    image_final = image_modify.reshape(image_modify.shape[0]*image_modify.shape[1], 3)
    return image_final


def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(requested_color):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)
        actual_name = None
    return closest_name

def get_colors(image, number):
    clf = KMeans(n_clusters = number)
    labels = clf.fit_predict(image)
    counts = Counter(labels)
    
    center_colors = clf.cluster_centers_
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    rgb_colors = [webcolors.hex_to_rgb(hex_colors[i]) for i in counts.keys()]

    named_colors = [get_color_name(rgb_colors[i]) for i in counts.keys()]

    values = list(counts.values())
    percentages = []

    for i in values: 
        p = round((i/160000)*100, 0)
        percentages.append(p)

    package = list(zip(hex_colors, named_colors, percentages))
    
    return package

import pandas as pd

paintings = pd.read_csv('paintings_final.csv')
print(paintings.Object_id.count())

painting_colors = {}

#itterate through and get colors for each painting
for index, row in paintings.iterrows():
    #grab the image link and the id
    path = paintings.loc[index, "Met_link"]
    id = paintings.loc[index, "Object_id"]
    
    #get the colors. It returns a list of tuples, which we turn into a list of lists to easier processing later
    try:
        painting_stats = get_colors(get_image(path), 10)
        color_list = [list(elem) for elem in painting_stats]

        painting_colors[id] = color_list
    
        print("Processing painting: " + str(index))
    
    except:
        print("Error in processing painting")
        
#Create new table, then melt so that each color pair is a unique row with it's assigned (repeating) index
colors = pd.DataFrame.from_dict(painting_colors, orient='index')
colors = colors.reset_index()
colors = pd.melt(colors, id_vars = ["index"])

print(colors["index"].nunique())
print(colors["index"].count())

colors.to_csv('paintings_colors.csv', index = False)