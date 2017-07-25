#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import lxml.etree as ET
import pprint as pp


osm_file = 'budapest_hungary_inner.osm'
expected_street_types = set()

tag_attributes = {}
street_names = {}
unexpected_street_names = set()
unexpected_postcodes = {}
unexpected_coordinates = []
invalid_emails = []


def is_proper_street_name(street_name):
    '''Check whether the type in the street name is included in the official list of types'''
    match  = re.match('.*\s(.*)$', street_name)
    if match:
        street_type = match.group(1)
        return street_type in expected_street_types
    else:
        return False


def is_valid_postcode(postcode):
    '''Check whether a postcode adheres to the standard four-digit postcode format'''
    expected_format = '1([0-2][0-9])[0-9]'
    match = re.match(expected_format, postcode)
    if match:
        inner_digits = int(match.group(1))
        if inner_digits <= 23:
            return True
    return False


def is_valid_email(email):
    '''Rudimentary check for obviously outlier email addresses'''
    email_format = '[0-9, a-z, ., -]+@[0-9, a-z, ., -]+\.[a-z]{2,5}'
    match = re.match(email_format, email.lower())
    return bool(match)


def valid_coordinates(coordinates):
    '''Check whether lat, lon coordinates are of the right magnitude'''
    return round(coordinates[0], 1) == 47.5 and round(coordinates[1], 0) == 19


def count_tags(tag, attributes):
    '''Count different types of tags in the file'''
    if tag not in tag_attributes:
        tag_attributes[tag] = {}
        tag_attributes[tag]['attributes'] = {}
        tag_attributes[tag]['count'] = 0

    tag_attributes[tag]['count'] += 1

    for attrib in attributes:
        if attrib not in tag_attributes[tag]['attributes']:
            tag_attributes[tag]['attributes'][attrib] = 0

        tag_attributes[tag]['attributes'][attrib] += 1


def audit():
    '''Check for <tag> elements in <way> and <node> elements and validate them based on course examples'''
    for event, elem in ET.iterparse(osm_file, events=('start',)):
        tag = elem.tag
        attributes = elem.attrib

        count_tags(tag, attributes)

        if tag == 'node':
            # Check for non-float or outlier coordinates
            try:
                coordinates = [float(attributes['lat']), float(attributes['lon'])]
            except ValueError:
                unexpected_coordinates.append(coordinates)
            else:
                if not valid_coordinates(coordinates):
                    unexpected_coordinates.append(coordinates)

        for tag in elem.iter('tag'):
            if tag.attrib['k'] == 'email':
                email = tag.attrib['v']

                if not is_valid_email(email):
                    invalid_emails.append(email)

            if tag.attrib['k'] == 'addr:street':
                street = tag.attrib['v']

                if not is_proper_street_name(street):
                    unexpected_street_names.add(street)

                if street not in street_names:
                    street_names[street] = 0
                street_names[street] += 1

            if tag.attrib['k'] == 'addr:postcode':
                postcode = tag.attrib['v']

                if not is_valid_postcode(postcode):
                    if postcode not in unexpected_postcodes:
                        unexpected_postcodes[postcode] = {'count': 0, 'streets': []}
                    unexpected_postcodes[postcode]['count'] += 1

                    # Get the parent element's child tag with k = addr:street attribute and extract the value
                    try:
                        street_address = [item.attrib['v'] for item in elem.getchildren() if item.tag == 'tag' and item.attrib['k'] == 'addr:street'][0]
                    except IndexError:
                        # No addr:street tags on parent, skip
                        pass
                    else:
                        unexpected_postcodes[postcode]['streets'].append(street_address)


    # Print out all the findings of the audit
    print('\nTAG AND ATTRIBUTE COUNTS:\n')
    pp.pprint(tag_attributes)

    print('\nSTREET NAME COUNTS:\n')
    pp.pprint(street_names)

    print('\nUNEXPECTED STREET NAMES:\n')
    pp.pprint(unexpected_street_names)

    print('\nUNEXPECTED POSTCODES:\n')
    pp.pprint(unexpected_postcodes)

    print('\nUNEXPECTED COORDINATES:\n')
    pp.pprint(unexpected_coordinates)

    print('\nINVALID EMAIL ADDRESSES:\n')
    print(invalid_emails)


if __name__ == '__main__':
    # street_types_wikipedia.txt contains the official list of Hungarian types 
    # of public places (street, square, etc.) with examples from Wikipedia
    # (source: https://hu.wikipedia.org/wiki/K%C3%B6zter%C3%BClet)
    with open('street_types_wikipedia.txt', 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match('(.*)\:.*', line)
            expected_street_types.add(match.group(1))

    audit()
