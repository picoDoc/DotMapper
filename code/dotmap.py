import sys
import os
from osgeo import ogr
from osgeo import osr
from shapely.wkb import loads
from shapely.geometry import *
from random import uniform
import sqlite3
import json
import convertjson
import glob
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
from globalmaptiles import GlobalMercator

TILE_X = 256
TILE_Y = 256

A = 1000.0

# use_ellipse, size, gamma, oversample
STYLE = {
4 : (False, 1, 153, 8),
5 : (False, 1, 153, 8),
6 : (False, 1, 179, 8),
7 : (False, 1, 179, 8),
8 : (False, 1, 204, 8),
9 : (False, 2, 204, 8),
10 : (False, 2, 230, 8),
11 : (False, 2, 230, 4),
12 : (False, 2, 255, 2),
13 : (False, 1, 255, 1)
}

defined_tiles = {}

def define_tile(zoom, x, y):
    if zoom not in defined_tiles:
        defined_tiles[zoom] = {}
    if x not in defined_tiles[zoom]:
        defined_tiles[zoom][x] = []
    if y not in defined_tiles[zoom][x]:
        defined_tiles[zoom][x].append(y)

def save_defined_tiles(tiles_path):
    with open(tiles_path + "/defined_tiles.json", "w") as f:    
        json.dump(defined_tiles, f)

def save_tile(img, tiles_path, zoom, x,y):
    fn = (tiles_path + '/{0}/{1}/{2}.png').format(zoom, x, y)
    img = img.resize((TILE_X, TILE_Y), Image.ANTIALIAS)
    if not os.path.exists(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))
    img.save(fn, "PNG")
    define_tile(zoom, x, y)
    print 'Saved {0}'.format(fn)

def main(tiles_path, db_file, groups):
    merc = GlobalMercator()

    # Set-up the output db
    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    for zoom in [5,6,7,8,9,10,11,12,13]: #TODO zoom levels
        results_set = c.execute("select x, y, quadkey, group_type from people_by_group order by quadkey asc, rand asc" )
        use_ellipse, radius_rel, gamma, os_scale = STYLE[zoom]
        radius = os_scale*radius_rel/4/2
        quadkey = None
        img = None

        for i,r in enumerate(results_set):
            if (i % 1000 == 0):
                print i
    
            x = float(r[0])
            y = float(r[1])
            next_quadkey = r[2][:zoom]
            group = r[3]
    
            if next_quadkey != quadkey:
                #finish last tile
                if img:
                    save_tile(img, tiles_path, zoom, gtx, gty)
                
                quadkey = next_quadkey
                tx, ty = merc.MetersToTile(x, y, zoom)
                gtx, gty = merc.GoogleTile(tx,ty,zoom)
        
                img = Image.new("RGB", (TILE_X*os_scale, TILE_Y*os_scale), "white")
                draw = ImageDraw.Draw(img)
                
            minx, miny, maxx, maxy = (c/A for c in merc.TileBounds(tx, ty, zoom))
            xscale = (TILE_X*os_scale)/(maxx - minx)
            yscale = (TILE_Y*os_scale)/(maxy - miny)


            #print 'minx', minx, 'miny', miny, 'maxx', maxx, 'maxy', maxy
            #print 'xscale',xscale,'yscale',yscale
            #print 'x',x,'y',y,'tx',tx,'ty',ty
        
            # Translate coordinates to tile-relative, google ready coordinates
            rx = (x/A - minx)*xscale
            ry = (maxy - y/A)*yscale
    
            fill=ImageColor.getrgb(groups[group]['color'])
            if use_ellipse:
                draw.ellipse((rx-radius,ry-radius,rx+radius,ry+radius), fill=fill)
            else:
                draw.point((rx, ry), fill=fill)
            #print "Draw at ", (rx-radius,ry-radius,rx+radius,ry+radius), ImageColor.getrgb(groups[group]['color'])

        save_tile(img, tiles_path, zoom, gtx, gty)
    
    save_defined_tiles(tiles_path)

# Execution code...

if __name__=='__main__':
    settings_file = "settings.json"

    if (len(sys.argv) > 1):
        settings_file = sys.argv[1]

    with open(settings_file, "r") as f:
        settings = json.load(f)

    # convert from unicode to utf-8 to avoid upsetting ogr
    settings = convertjson.convert(settings)

    main(settings['tiles_path'],
         settings['db_filename'],
         settings['groups'])
