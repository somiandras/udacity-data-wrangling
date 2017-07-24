#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import lxml.etree as ET
import json


osm_file = 'budapest_hungary_inner.osm'
TAGS_TO_PROCESS = ['node', 'way', 'relation']
CREATED = ['user', 'uid', 'timestamp', 'version', 'changeset']
POS = ['lat', 'lon']


def shape_element(element):
    '''Create dict from XML element based on course examples'''
    if element.tag in TAGS_TO_PROCESS:
        elem_data = {}
        elem_data['type'] = element.tag

        for attr in element.attrib:
            if attr in CREATED:
                if 'created' not in elem_data:
                    elem_data['created'] = {}
                elem_data['created'][attr] = element.attrib[attr]
            elif attr == 'lat':
                if 'pos' not in elem_data:
                    elem_data['pos'] = [None, None]
                elem_data['pos'][0] = float(element.attrib[attr])
            elif attr == 'lon':
                if 'pos' not in elem_data:
                    elem_data['pos'] = [None, None]
                elem_data['pos'][1] = float(element.attrib[attr])
            else:
                elem_data[attr] = element.attrib[attr]

        for tag in element.iter():
            if tag.tag == 'tag':
                # Check for tags containing 'addr:...' but avoid 'addr:...:...' format tags
                match = re.match('^addr:([^:]*)$', tag.attrib['k'])
                if match:
                    if 'address' not in elem_data:
                        elem_data['address'] = {}
                    elem_data['address'][match.group(1)] = tag.attrib['v']
                else:
                    # Non-address tags are simple properties on the element
                    elem_data[tag.attrib['k']] = tag.attrib['v']
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


def clean_streetname(streetname):
    '''Programatically fix issues of street names'''
    if streetname == 'Kucsma':
        new_streetname = 'Kucsma utca'
    elif streetname.lower() == streetname:
        new_streetname = streetname[0].upper() + streetname[1:]
    else:
        new_streetname = streetname
    return new_streetname


def clean_postcode(postcode):
    '''Programatically fix issues with postcodes'''
    postcode_string = str(postcode)
    if postcode_string[:2] == 'H-':
        return int(postcode_string[2:])
    elif postcode_string == '1503':
        return 1053
    elif postcode_string == '1507':
        return 1057
    else:
        return int(postcode)


def correct_data_entry(elem_data):
    '''Fix known issues in data before adding to the database'''
    if 'address' in elem_data:
        if 'street' in elem_data['address']:
            elem_data['address']['street'] = clean_streetname(elem_data['address']['street'])
        if 'postcode' in elem_data['address']:
            elem_data['address']['postcode'] = clean_postcode(elem_data['address']['postcode'])
    return elem_data


def process_file():
    '''Transform the contents of the OSM XML file to a JSON file, based on the course examples'''
    data = []
    with open('dump.json', 'w') as file_out:
        for event, elem in ET.iterparse(osm_file, events=('start',)):
            elem_data = shape_element(elem)
            if elem_data:
                final_element = correct_data_entry(elem_data)
                data.append(final_element)
                file_out.write(json.dumps(final_element) + '\n')
    return data


if __name__ == '__main__':
    data = process_file()
