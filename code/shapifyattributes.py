import sys
from osgeo import ogr
import csv
import json
import glob
import convertjson
import operator as op
import numpy as np
from copy import deepcopy

# Main function that reads the shapefile, and reads the attribute data,
# merges the data back in to the shapefile
# Note: changes the input shapefile, so copy first

def main(shapes_file_list, attr_file_list, attr_skip_lines,
         shape_id_field, attr_id_field, groups, attr_filters = {}):
    attr = {}

    # Read in all the attributes to memory, file by file

    for attr_filename in attr_file_list:
        with open(attr_filename, "rb") as attr_file:
            for i in range(0, attr_skip_lines):
                attr_file.next()
        
            attr_reader = csv.DictReader(attr_file)

            for row in attr_reader:
                # check if this row passes all the filters
                if all([getattr(op, val['op'])(type(val['val'])(row[flt]), val['val']) for flt, val in attr_filters.items()]):
                    a = {}
                    for f in groups:
                        if isinstance(groups[f]['field'], list):
                            a[f] = 0
                            for subfield in groups[f]['field']:
                                a[f] = a[f] + int(row[subfield].replace(',',''))
                        else:
                            a[f] = int(row[groups[f]['field']].replace(',',''))
                    attr[row[attr_id_field]] = a

        print "Processed {0} rows in {1}".format(len(attr), attr_filename)

    # in the census data only 100m boxes with over a certain population are listed, so we must infer the rest
    # here we calculate the infered average population values for unlisted 100m boxes from the listed 1km and 100m boxes

    # for each 1km area init a count of unlisted 100m areas it contains, and census totals
    unlisted_100m_count = {} # how many 100m boxes are unlisted?
    totals_1km = {} # people living in these unlisted boxes?
    for sid,v in attr.iteritems():
        if len(sid) == 7:
            unlisted_100m_count[sid] = 100
            totals_1km[sid] = deepcopy(v)

    # for each 1km area how many people live outside the listed 100m squares?
    for sid,groups in attr.iteritems():
        if len(sid) == 9:
            sid_1km = sid[0:4] + sid[5:8]
            unlisted_100m_count[sid_1km] -= 1
            for group in groups:
                totals_1km[sid_1km][group] -= groups[group]


    # what is the average population per unlisted 100m box inside a given 1km box
    # TODO values are rounded down to ints, so there is some inaccuracy.  Could be improved
    unlisted_100m_average = {}
    for sid,groups in totals_1km.iteritems():
        unlisted_100m_average[sid] = {}
        for group, v in groups.iteritems():
            unlisted_100m_average[sid][group] = float(v) / unlisted_100m_count[sid]

    # Open and process the shapefiles

    for shapes_filename in shapes_file_list:
        ds = ogr.Open(shapes_filename, True)

        if ds is None:
            print "Open failed.\n"
            sys.exit( 1 )

        # Obtain the first (and only) layer in the shapefile
        lyr = ds.GetLayerByIndex(0)

        lyr.ResetReading()

        # Obtain the field definitions in the shapefile layer
        for f in groups:
            print f
            field_defn = ogr.FieldDefn( f, ogr.OFTInteger )

            if lyr.CreateField ( field_defn ) != 0:
                print "Creating Name field failed.\n"
                sys.exit( 1 )


        for i,feat in enumerate(lyr):
            if i % 1000 == 0:
                print "Processed {0} features".format(i)
        
            sid = feat.GetField(shape_id_field)

            if sid in attr:
                for f in groups:
                    feat.SetField( f, attr[sid][f] )
                lyr.SetFeature(feat)
            # if the 100m box is not provided in census data, use infered data
            elif len(sid) == 9:
                sid_1km = sid[0:4] + sid[5:8]
                if sid_1km in unlisted_100m_average:
                    for f in groups:
                        # convert average to a discrete value based on poisson dist.
                        feat.SetField( f, np.random.poisson(unlisted_100m_average[sid_1km][f]) )
                    lyr.SetFeature(feat)
    ds = None


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
    attr_file_list = glob.glob(settings['attr_path']+'/*.csv')  

    main(shapes_file_list,
         attr_file_list,
         settings['attr_skip_lines'],
         settings['shape_id_field'],
         settings['attr_id_field'],
         settings['groups'],
         settings['attr_filters'] if 'attr_filters' in settings else {})
