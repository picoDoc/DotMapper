# Utility function to convert a json-loaded object from unicode to utf-8 strings
# Thanks to Mark Amery on Stackoverflow #6633651
def convert(input):
    if isinstance(input, dict):
        return { convert(key) : convert(value) for key, value in input.iteritems() }
    elif isinstance(input, list):
        return [ convert(element) for element in input ]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input