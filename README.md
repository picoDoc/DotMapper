DotMapper
=========

*__Warning: Here be dragons!__ I'm putting this code up now so people can play with it, but it's definitely not ready for primetime. In particular the database query in dotmap.py is very slow, and if you're working with anything more complex than I was, you'd want to swap it for something else. Also, the black tiles are not generated in any sensible way, although if you use a second settings.json file you can generate them fairly easily. I will hopefully make some of these changes in the next week.*

A complete system for producing Google maps-enabled pure client-side dot maps, based on any suitable shapefiles and group totals.

http://projects.andrewwhitby.com/uk-ethnicity-map

Based on code from Dustin A. Cooper, who adapted it from a similar project by Brandon Martin-Anderson from the MIT Media Lab.

Usage
-----

Make sure your current working directory is the main project folder.

1. Copy settings.example.json to settings.json and edit as appropriate. This is completely undocumented but hopefully mostly self-explanatory.
2. Copy your shapefiles to 'boundaries+attributes'.
3. (optional - only if your shapefiles do not already contain the relevant attributes) Copy your csv-format attribute files to 'attributes'. Run 'python code/shapifyattributes.py'.
4. Run 'python dotfile.py'.
5. Run 'python dotmap.py'.
6. Run 'python generatetileindex.py'
7. Run 'python makeclient.py'

To test, enter the 'out' directory and run 'python -mSimpleHTTPServer'. You should be able to connect to http://localhost:8000 and see your map.

This procedure works error-free on the England and Wales data sources described at http://andrewwhitby.com/2013/09/03/uk-ethnicity-map/ , if you need something to get started.