DotMapper (adapted for N.I. grid square census data)
=========

A complete system for producing Google maps-enabled pure client-side dot maps, based on shapefiles and N.I. grid square [census data](http://www.nisra.gov.uk/census/2011/results/grid-square.html).  This code can probably be adapted for use with similar data, but no guarantees provided!

Based on code from Andrew Whitby, who adapted it from Dustin A. Cable, who adapted it from a similar project by Brandon Martin-Anderson from the MIT Media Lab.

Usage
-----

Make sure your current working directory is the main project folder.  Run 

```
generate_dotmap.sh settings.json
```

replacing __settings.json__ with your own settings file.  This will run all the python scripts in the *code* directory in the correct order and output a final webpage to the *out* directory.

To test, enter the 'out' directory and run 'python -mSimpleHTTPServer' (or your prefered server application). You should be able to connect to *http://localhost:8000* and see your map.

