#!/usr/bin/env python3
import argparse

import json

def main(file,site):
    jsondata = {}
    jsondata=read_jsonfile(file)

    for node in list(jsondata['nodes']):
        try:
            if jsondata['nodes'][node]['nodeinfo']['system']['site_code'] == site:
                del jsondata['nodes'][node]
        except:
            pass
    print (json.dumps(jsondata))

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:
            jsondata = json.load(data_file)
    except:
        print("Couldn't read json file: ")
    return jsondata

def parse_args():
    parser = argparse.ArgumentParser(
        description='export alfred data to influxdb')

    parser.add_argument('--file', type=str, required=True, default='',
                        help='file to pars (nodes.json)')
    parser.add_argument('--site', type=str, required=True, default='',
                        help='site of node to delete')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main( file=args.file, site=args.site)
