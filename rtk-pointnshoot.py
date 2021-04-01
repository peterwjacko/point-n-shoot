# %% codecell
import sys, os, math
#from pyproj import CRS, Transformer, transform
import tkinter as tk
from tkinter.filedialog import askopenfilename
from pathlib import Path
import numpy as np
import pandas as pd
# %% codecell
# define functions
root = tk.Tk()

def openRTK():
    pathPointsRTK = askopenfilename(mode ='r', initialdir = "/", title = "Select RTK points file", filetypes = (("comma delimited","*.csv"),("all files","*.*")))
    return pathPointsRTK

def openTrees():
    pathPointsTree = askopenfilename(mode ='r', initialdir = "/", title = "Select tree points file", filetypes = (("comma delimited","*.csv"),("all files","*.*")))
    return pathPointsTree

# csv of rtk reference points and their grid coordinates (this case is GDA94MGA56)
#pathPointsRTK = "C:\\Users\\Study\\OneDrive - University of the Sunshine Coast\\Documents\\FieldData\\pointRTK.csv"
# csv of tree records with rtk reference point, compass heading (magnetic), distance from rtk ref point
#pathPointsTree = "C:\\Users\\Study\\OneDrive - University of the Sunshine Coast\\Documents\\FieldData\\Transect_References.csv"

pointsRTK = pd.read_csv(openRTK()) #(pathPointsRTK)
pointsTree = pd.read_csv(openTrees()) #pd.read_csv(pathPointsTree)

# don't need this right now
#targetCRS = CRS.from_epsg(28356) # target CRS for output points
#dataCRS = CRS.from_epsg(4326)# input coordinates of reference points
#crsTransformer = Transformer.from_crs(targetCRS, dataCRS)

# %% codecell
# create coordinate columns
pointsTree.loc[:, 'treeY'] = np.nan
pointsTree.loc[:, 'treeX'] = np.nan
pointsTree.loc[:, 'azimuthTrue'] = np.nan
pointsTree.loc[:, 'azimuthGrid'] = np.nan
pointsTree.loc[:, 'convergenceGrid'] = np.nan

# rename columns
pointsTree.rename(columns = {
                            'RTK Point': 'refRTK',
                            'StartPointHeading': 'treeHeading',
                            'Distance': 'treeDistance'
                            },
                            inplace = True)
pointsRTK.rename(columns = {
                            'Name': 'refRTK',
                            'Northing': 'northingRTK',
                            'Easting': 'eastingRTK'
                            },
                            inplace = True)

# %% codecell
# match tree points with corresponding rtk ref point
pointsTree = pd.merge(pointsTree, pointsRTK, on = 'refRTK', how = 'left')

# %% codecell
pointsTree.replace(np.nan, -999) # fill nan with -999 to enable dtype conversion
pointsTree.replace("None", -999) # some columns had the string "None" which was confusing things

# set data types
pointsTree = pointsTree.astype({
                                "treeHeading": float,
                                "treeDistance": float,
                                "northingRTK": float,
                                "eastingRTK": float,
                                "treeY": float,
                                "treeX": float,
                                "azimuthTrue": float,
                                "azimuthGrid": float,
                                "convergenceGrid": float
                                })

# %% codecell
# calculate new x and y
D = 10.77 # magnetic delcination in WGS84 (from Geoscience Australia, link in README)
centralMeridian = 153 # central meridian for GDA94MGA56

for i in range(len(pointsTree)):
    try:
        if pd.notna(pointsTree.loc[i, 'refRTK']):
            # calculate location if trees are based off a reference point
            xPoint = pointsTree.loc[i, 'eastingRTK']
            yPoint = pointsTree.loc[i, 'northingRTK']
            gridConvergence = math.atan(math.tan(xPoint - centralMeridian) * math.sin(yPoint))
            azimuthTrue = pointsTree.loc[i, 'treeHeading'] + D
            azimuthGrid = azimuthTrue + gridConvergence
            northingAdjusted = math.cos(math.radians(azimuthGrid)) * pointsTree.loc[i, 'treeDistance'] + pointsTree.loc[i, 'northingRTK']
            eastingAdjusted = math.sin(math.radians(azimuthGrid)) * pointsTree.loc[i, 'treeDistance'] + pointsTree.loc[i, 'eastingRTK']

            pointsTree.loc[i, 'treeNorthing'] = northingAdjusted
            pointsTree.loc[i, 'treeEasting'] = eastingAdjusted
            pointsTree.loc[i, 'azimuthTrue'] = azimuthTrue
            pointsTree.loc[i, 'azimuthGrid'] = azimuthGrid
            pointsTree.loc[i, 'convergenceGrid'] = gridConvergence

        elif pd.isna(pointsTree.loc[i, 'refRTK']):
            # some trees had handheld gps waypoints taken at the base of the tree and are true
            # probably don't need this but I'll put in new columns for clarity
            pointsTree.loc[i, 'treeNorthing'] = pointsTree.loc[i, 'Northing']
            pointsTree.loc[i, 'treeEasting'] = pointsTree.loc[i, 'Easting']

    except:
        continue

# %% codecell
# drop columns merged from RTK point dataframe
for col in list(pointsRTK.columns):
    try:
        if col not in ["refRTK", "northingRTK", "eastingRTK"]:
            pointsTree = pointsTree.drop([col], axis = 1)
    except KeyError:
        print(col, " column does not exist")
        continue

# %% codecell
# output dataframe to csv
outputPath = str(Path(pathPointsTree).parent) + "\\transectPoints_Adjusted.csv"
pointsTree.to_csv(outputPath, header = True)
