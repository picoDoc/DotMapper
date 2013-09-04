import sys
import os
import json
import convertjson
import glob

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

def main(tiles_path):
    tiles = glob.glob(tiles_path+'/*/*/*.png')
    for t in tiles:
        parts = t.split('/')
        zoom = int(parts[-3])
        x = int(parts[-2])
        y = int(parts[-1].split('.')[0])
        define_tile(zoom, x, y)

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

    main(settings['tiles_path'])