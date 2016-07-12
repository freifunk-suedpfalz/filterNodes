#!/usr/bin/env python2

import argparse
import json
import urllib
import socket
import sys
import datetime

rightnow = datetime.datetime.now()

def filter(nodes,site):
    jsondata = {}
    jsondata=read_jsonfile(nodes)
    print ('Backup file to {}.bak'.format(nodes))
    with open(nodes + '.bak','w') as outfile:
        json.dump(jsondata, outfile)
    for node in list(jsondata['nodes']):
        try:
            if jsondata['nodes'][node]['nodeinfo']['system']['site_code'] == site:
                del jsondata['nodes'][node]
        except:
            pass
    print ('Write new file to {}'.format(nodes))
    with open(nodes,'w') as outfile:
        json.dump(jsondata, outfile)

def shifting(url,statusSocket,blacklist):
    #get data
    response= urllib.urlopen(url + '/nodes.json')
    nodesjson=json.loads(response.read())

    response= urllib.urlopen(url + '/nodelist.json')
    nodelistjson=json.loads(response.read())

    response= urllib.urlopen(url + '/graph.json')
    graphjson=json.loads(response.read())

    #find supernodes in data
    supernodes = get_supernodes(nodesjson)
    print ('####check supernodes####')
    print ('####found supernodes:####')
    for supernode in supernodes:
        print supernode

    #find Nodes with fastd's status socket
    print ('####check nodes####')
    nodes = get_nodes(statusSocket)
    print ('####found nodes:####')
    for node in nodes:
        print node
    
    # Summary
    print ('####Summary:####')
    if len(supernodes)>0:
    	print ("Found {} Supernodes".format(len(supernodes)))
    else:
        print ("No Supernodes Found")
    if len(nodes)>0:
    	print ("Found {} Nodes".format(len(nodes)))
    else:
        print ("No Nodes Found")

    # Shifting
    print ('####Shifting:####')    
    amount = 0
    while amount <= 0:
        amount = int(input("How many nodes to shift/block? "))
        if amount <= 0:
            print ("Nothing to shift/block. Please correct or abort (ctrl+c).")
        if amount > len(nodes):
            amount = 0
            print ("Cannot switch/block more nodes than found. Please correct.")
    
    create_blacklist(nodes,amount,blacklist)

def read_jsonfile(file):
    jsondata = {}
    try:
        with open(file) as data_file:
            jsondata = json.load(data_file)
    except:
        print("Couldn't read json file: ")
    return jsondata

def get_supernodes(nodesjson):
    supernodes = []
    #loop over every node and check if node is gateway
    for node in list(nodesjson['nodes']):
        try:
            if nodesjson['nodes'][node]['flags']['gateway'] == True:
                if not nodesjson['nodes'][node]['nodeinfo']['hostname'] in supernodes:
                    supernodes.append(nodesjson['nodes'][node]['nodeinfo']['hostname'])
        except:
            pass
    return supernodes

def get_nodes(statusSocket):
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = statusSocket
    print >>sys.stderr, 'connecting to %s' % server_address
    try:
        sock.connect(server_address)
        data = ""
        part = None
        while part != "":
            part = sock.recv(4096)
            data += part
        if not data :
            print '\nDisconnected from server'
            sys.exit()
        else :
            #filter for pubkeys only
            data = json.loads(data)
            result = list(data['peers'])
            return result
        sock.close()
    except socket.error, msg:
        print >>sys.stderr, msg
        sys.exit(1)

def create_blacklist(nodes,amount,blacklist):
    data = {}
    data['peers'] = []
    i = 0
    while i < amount:
        data['peers'].append({'pubkey':nodes[i],'comment':'shift to other server','added':str(rightnow)})
        i = i + 1
    with open(blacklist,'w') as outfile:
        json.dump(data, outfile)
    sys.exit(0)

def clear_blacklist(blacklist):
    data = {}
    data['peers'] = []
    with open(blacklist,'w') as outfile:
        json.dump(data, outfile)
    sys.exit(0)

def parse_args_shift():
    parser = argparse.ArgumentParser(description='shift nodes')
    parser.add_argument('-u','--url',type=str,required=True,default='', help='Url to data "http://www.freifunk-suedpfalz.de/karte"')
    parser.add_argument('-s','--socket',type=str,required=True,default='', help='/var/tmp/fastd.ffld.sock')
    parser.add_argument('-b','--blacklist',type=str,required=True,default='', help='/etc/fastd/fastd-shifter.json')
    return parser.parse_args()

def parse_args_clear():
    parser = argparse.ArgumentParser(description='clear blacklist')
    parser.add_argument('-b','--blacklist',type=str,required=True,default='', help='/etc/fastd/fastd-shifter.json')
    return parser.parse_args()

def parse_args_filter():
    parser = argparse.ArgumentParser(description='filter by site code')
    parser.add_argument('-n','--nodes',type=str,required=True,default='', help='path to nodes.json')
    parser.add_argument('-c','--code',type=str,required=True,default='', help='sitecode to be deleted')

    return parser.parse_args()

if __name__ == '__main__':
    print ('Managing Node Shifting/Blacklisting')
    print ('[0] Clear Blacklisting') 
    print ('[1] Shift Nodes')
    print ('[2] Filter Sitecode')
    option = -1
    while option < 0 or option > 2: 
        option = input('Choose a Number between 0-2: ')
    if option == 0:
        args = parse_args_clear()
        clear_blacklist(blacklist=args.blacklist)
    elif option == 1:
        args = parse_args_shift()
        shifting( url=args.url,statusSocket=args.socket,blacklist=args.blacklist)
    elif option == 2:
        args = parse_args_filter()
        filter( nodes=args.nodes,site=args.code)
