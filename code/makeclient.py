import sys
import os
import json
import convertjson
from string import Template

def main(template_path, out_path, tiles_path, zoom_levels, client_settings, groups):
    with open(template_path + "/index.html", "r") as f_in:
        template = Template(f_in.read())
    
    with open(tiles_path + "/defined_tiles.json", "r") as f_defined_tiles:
        client_settings['_defined_tiles'] = f_defined_tiles.read()

    client_settings['_zoom_min'] = min(zoom_levels)
    client_settings['_zoom_max'] = max(zoom_levels)

    if 'head_filename' in client_settings:
        with open(client_settings['head_filename'], 'r') as f_head:
            client_settings['_head'] = f_head.read()
    else:
        client_settings['_head'] = ''  

    if 'sharing_filename' in client_settings:
        with open(client_settings['sharing_filename'], 'r') as f_sharing:
            client_settings['_sharing'] = f_sharing.read()
    else:
        client_settings['_sharing'] = ''  

    if 'branding_filename' in client_settings:
        with open(client_settings['branding_filename'], 'r') as f_branding:
            client_settings['_branding'] = f_branding.read()
    else:
        client_settings['_branding'] = ''
    
    legend = [{'desc' : gv['desc'], 'color' : gv['color']} for gv in sorted(groups.values(), key = lambda x: x['order'])]
    client_settings['_legend'] = json.dumps(legend);

    out = template.substitute(client_settings)
    with open(out_path + "/index.html", "w") as f_out:
        f_out.write(out)

# Execution code...

if __name__=='__main__':
    settings_file = "settings.json"

    if (len(sys.argv) > 1):
        settings_file = sys.argv[1]

    with open(settings_file, "r") as f:
        settings = json.load(f)

    # convert from unicode to utf-8 to avoid upsetting ogr
    settings = convertjson.convert(settings)

    main(settings['template_path'], settings['out_path'], settings['tiles_path'], settings['zoom_levels'],settings['client'], settings['groups'])
