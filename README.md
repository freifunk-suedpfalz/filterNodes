# filterNodes
Python3 script for deleting nodes from alfreds nodes.json based on site_code


## Prerequisites
-python3
-pip (pip install json)

## Arguments
--file  Alfreds nodes.json
--site  site_code of Nodes that should be deleted from --file

## Usage
./filterNodes.py --file nodes.json --site ffws > nodesnes.json
