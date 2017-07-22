#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import lxml.etree as ET
import pprint as pp
import json

# Issues to clean before upload:
# 1. Missing 'utca' from 'Kucsma' in one case
# 2. Lower-case street names
# 3. Remove 'H-' from postcodes
# 4. Change 1503 and 1507 postcodes to 1053 and 1057

filename = 'budapest_hungary_inner.osm'
TAGS_TO_PROCESS = ['node', 'way', 'relation']
CREATED = ['user', 'uid', 'timestamp', 'version', 'changeset']
POS = ['lon', 'lat']


def shape_element(element):
    if element.tag in TAGS_TO_PROCESS:
        elem_data = {}
        elem_data['type'] = element.tag

        for attr in element.attrib:
            if attr in CREATED:
                if 'created' not in elem_data:
                    elem_data['created'] = {}
                elem_data['created'][attr] = element.attrib[attr]
            elif attr in POS:
                if 'pos' not in elem_data:
                    elem_data['pos'] = {}
                elem_data['pos'][attr] = float(element.attrib[attr])
            else:
                elem_data[attr] = element.attrib[attr]

        for tag in element.iter():
            if tag.tag == 'tag':
                match = re.match('^addr:([^:]*)$', tag.attrib['k'])
                if match:
                    if 'address' not in elem_data:
                        elem_data['address'] = {}
                    elem_data['address'][match.group(1)] = tag.attrib['v']
            elif tag.tag == 'nd':
                if 'ref' in tag.attrib:
                    if 'node_refs' not in elem_data:
                        elem_data['node_refs'] = []
                    elem_data['node_refs'].append(tag.attrib['ref'])
            elif tag.tag == 'member':
                member_data = {}
                if 'members' not in elem_data:
                    elem_data['members'] = []
                for attr in tag.attrib:
                    member_data[attr] = tag.attrib[attr]
                elem_data['members'].append(member_data)
        return elem_data
    else:
        return None


def process_file():
    data = []
    counter = 0
    for event, elem in ET.iterparse(filename, events=('start',)):
        elem_data = shape_element(elem)
        if elem_data:
            data.append(elem_data)
        # counter += 1
        # if counter == 10000:
        #     break
    return data


def upload_to_database(data):
    with open('dump.json', 'w') as file_out:
        file_out.write(json.dumps(data, indent=2))


if __name__ == '__main__':
    data = process_file()
    upload_to_database(data)
