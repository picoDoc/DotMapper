import sys
from osgeo import ogr
from osgeo import osr
from shapely.wkb import loads
from shapely.geometry import *
from random import uniform
import sqlite3
import json
import convertjson
import glob

# Import the module that converts spatial data between formats

sys.path.append("filepath")
from globalmaptiles import GlobalMercator

# Main function that reads the shapefile, obtains the population counts,
# creates a point object for each person by race, and exports to a SQL database.

def main(shapes_file_list, db_file, groups):
    field_ids = {}
    # Create a GlobalMercator object for later conversions
    
    merc = GlobalMercator()

    # Set-up the output db
    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    #c.execute("drop table if exists people_by_group")
    c.execute("create table if not exists people_by_group (x real, y real, quadkey text, rand real, group_type text)" )
    c.execute("drop index if exists i_quadkey")

    # Open the shapefiles

    for input_filename in shapes_file_list:
        print "Processing file {0}".format(input_filename)
        ds = ogr.Open(input_filename)
    
        if ds is None:
            print "Open failed.\n"
            sys.exit( 1 )

        # Obtain the first (and only) layer in the shapefile
    
        lyr = ds.GetLayerByIndex(0)

        lyr.ResetReading()

        # Obtain the field definitions in the shapefile layer

        feat_defn = lyr.GetLayerDefn()
        field_defns = [feat_defn.GetFieldDefn(i) for i in range(feat_defn.GetFieldCount())]

        # Set up a coordinate transformation to latlon
        wgs84 = osr.SpatialReference()
        wgs84.SetWellKnownGeogCS("WGS84")
        sr = lyr.GetSpatialRef()
        xformer = osr.CoordinateTransformation(sr,wgs84)

        # Obtain the index of the group fields
        for i, defn in enumerate(field_defns):
            if defn.GetName() in groups:
                field_ids[defn.GetName()] = i

        # Obtain the number of features (Census Blocks) in the layer
        n_features = len(lyr)

        # Iterate through every feature (Census Block Ploygon) in the layer,
        # obtain the population counts, and create a point for each person within
        # that feature.
        for j, feat in enumerate( lyr ):
        
            # Print a progress read-out for every 1000 features and export to hard disk
            if j % 1000 == 0:
                conn.commit()
                print "%s/%s (%0.2f%%)"%(j+1,n_features,100*((j+1)/float(n_features)))
            
            # Obtain total population, racial counts, and state fips code of the individual census block

            counts = {}
            for f in field_ids:
                val = feat.GetField(field_ids[f])
                if val:
                    counts[f] = int(val)
                else:
                    counts[f] = 0

            # Obtain the OGR polygon object from the feature
            geom = feat.GetGeometryRef()
            if geom is None:
                continue
        
            # Convert the OGR Polygon into a Shapely Polygon
            poly = loads(geom.ExportToWkb())
        
            if poly is None:
                continue        
            
            # Obtain the "boundary box" of extreme points of the polygon
            bbox = poly.bounds
        
            if not bbox:
                continue
     
            leftmost,bottommost,rightmost,topmost = bbox
    
            # Generate a point object within the census block for every person by race
       
            for f in field_ids:
                for i in range(counts[f]):
                    # Choose a random longitude and latitude within the boundary box
                    # and within the orginial ploygon of the census block
                    while True:
                        samplepoint = Point(uniform(leftmost, rightmost),uniform(bottommost, topmost))
                        if samplepoint is None:
                            break
                        if poly.contains(samplepoint):
                            break
    
                    # Convert the longitude and latitude coordinates to meters and
                    # a tile reference
    
                    try:
                        # In general we don't know the coordinate system of input data
                        # so transform it to latlon
                        lon, lat, z = xformer.TransformPoint(samplepoint.x, samplepoint.y)
                        x, y = merc.LatLonToMeters(lat,lon)
                    except:
                        print "Failed to convert ", lat, lon
                        sys.exit(-1)
                    tx,ty = merc.MetersToTile(x, y, 21)
                
                    # Create a unique quadkey for each point object        
                    quadkey = merc.QuadTree(tx, ty, 21)
                
                    # Create categorical variable for the race category           
                    group_type = f         
    
                # Export data to the database file    
                    try:
                        c.execute( "insert into people_by_group values (?,?,?,random(),?)", (x, y, quadkey,group_type) )
                    except:
                        print "Failed to insert ", x, y, tx, ty, group_type
                        sys.exit(-1)

	    c.execute("create index if not exists i_quadkey on people_by_group(x, y, quadkey, rand, group_type)")
        conn.commit()

# Execution code...

if __name__=='__main__':
    settings_file = "settings.json"

    if (len(sys.argv) > 1):
        settings_file = sys.argv[1]

    with open(settings_file, "r") as f:
        settings = json.load(f)

    # convert from unicode to utf-8 to avoid upsetting ogr
    settings = convertjson.convert(settings)

    shapes_file_list = glob.glob(settings['shapes_path']+'/*.shp')

    main(shapes_file_list,
         settings['db_filename'],
         settings['groups'])
