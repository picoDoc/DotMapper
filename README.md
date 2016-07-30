DotMapper (adapted for N.I. grid square census data)
=========

*__Warning: Here be dragons!__ I'm putting this code up now so people can play with it, but it's definitely not ready for primetime. In particular the database query in dotmap.py is very slow, and if you're working with anything more complex than I was, you'd want to swap it for something else. Also, the black tiles are not generated in any sensible way, although if you use a second settings.json file you can generate them fairly easily. I will hopefully make some of these changes in the next week.*

A complete system for producing Google maps-enabled pure client-side dot maps, based on any suitable shapefiles and group totals.

http://projects.andrewwhitby.com/uk-ethnicity-map

Based on code from Dustin A. Cable, who adapted it from a similar project by Brandon Martin-Anderson from the MIT Media Lab.

Usage
-----

Make sure your current working directory is the main project folder.

Run *generate_dotmap.sh settings.json*, replacing settings.json with your own settings file.  This will run all the python scripts in the *code* directory in the correct order and output a final webpage to the 'out' directory.

To test, enter the 'out' directory and run 'python -mSimpleHTTPServer'. You should be able to connect to http://localhost:8000 and see your map.

