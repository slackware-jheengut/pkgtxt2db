#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pkgtxt2db.py
#
#       Copyright 2012 Frédéric Galusik <fredg~at~salixos~dot~org>
#
#
# License: BSD Revised
#
# Convert the Slackware/Salix PACKAGES.TXT file to some various database
# formats : CSV, json, xml
#


import os
import urllib2
import gzip
import re

# Program information
my_url = 'http://www.salixos.org/wiki/index.php/Pkgtxt2db'
my_name = 'pkgtxt2db'
my_version = '0.0'

# vars
mirror = 'http://salix.enialis.net/'
arch = ['i486/', 'x86_64/']
rep = ['', 'slackware-']
release = ['current', '14.0', '13.37', '13.1', '13.0']
expa = ['/', '/extra/', '/patches/']
pkgtxtz = 'PACKAGES.TXT.gz'
pkgtxt = 'PACKAGES.TXT'

# initialise the pkg dictionnary with empty values
fields = ['name',
             'version',
             'arch',
             'release'
             'location',
             'deps',
             'sizec',
             'sizeu',
             'slackdesc']


def new_pkgdct():
    return dict(zip(fields, ['', ] * len(fields)))


# Fetch PACKAGES.TXT
def pkgtxturl(a=0, re=0, rl=1, ep=0):
    """
    Download the slackware/salix PACKAGES.TXT.gz from a built URL and unzip it

    pkgtxturl(a, re, rl, ep))
    pkgtxturl(arch, os, release, extra|patches)
    -arch i486               : a=0
    -arch x86_64             : a=1
    -repository salix        : re=0
    -repository slackware    : re=1
    -release current         : rl=0
    -release 14.0            : rl=1
    -release 13.37           : rl=2
    -release 13.1            : rl=3
    -release 13.0            : rl=4
    -standard repo           : ep=0
    -extra slackware repo    : ep=1
    -patches slackware repo  : ep=2

    examples:
     -salix i486 14.0        : url(0, 0, 1, 0) (default)
     -     x86_64            : url(1, 0, 1, 0)
     -slackware i486 14.0    : url(0, 1, 1, 0)
     -                extra  : url(0, 1, 1, 1)
     -                patches: url(0, 1, 1, 2)
    """
    url = mirror + arch[a] + rep[re] + release[rl] + expa[ep] + pkgtxtz
    # remove old files
    if os.path.isfile(pkgtxtz):
        os.remove(pkgtxtz)
        print "Remove old ", pkgtxtz
    if os.path.isfile(pkgtxt):
        os.remove(pkgtxt)
        print "Remove old ", pkgtxt
    try:
        f = urllib2.urlopen(url)
        print "Fetching ", url
        print ""
        # Open local_file for writing
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
        return False
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url
        return False
    # unzip it
    fout = open(pkgtxt, 'w')
    with gzip.open(pkgtxtz, 'rb') as f:
        for line in f:
            fout.write(line)
    fout.close()


# to CSV DB
def tocsv(pkgDct, sep=";"):
    """
    Export PACKAGES.TXT to a CSV database format.
    The separated string can be choosen with the sep var, default is ;
    """
    with open("packages.csv", 'a') as csvf:
        csvf.write(
            sep.join(map(lambda field: pkgDct.get(field, ''), fields)) + '\n')


# to JSON DB
def tojson(pkgDct):
    """
    Export PACKAGES.TXT to a JSON database format
    """
    with open("packages.json", 'a') as jsonf:
        jsonf.write('  {\n')
        jsonf.write('    \"name\": \"' + pkgDct.get("name") + '\",\n')
        jsonf.write('    \"version\": \"' + pkgDct.get("version") + '\",\n')
        jsonf.write('    \"arch\": \"' + pkgDct.get("arch") + '\",\n')
        jsonf.write('    \"release\": \"' + pkgDct.get("release") + '\",\n')
        jsonf.write('    \"location\": \"' + pkgDct.get("location") + '\",\n')
        jsonf.write('    \"deps\": \"' + pkgDct.get("deps") + '\",\n')
        jsonf.write('    \"sizec\": \"' + pkgDct.get("sizec") + '\",\n')
        jsonf.write('    \"sizeu\": \"' + pkgDct.get("sizeu") + '\",\n')
        jsonf.write('    \"slackdesc\": \"' + pkgDct.get("slackdesc") + '\",\n')


# to XML DB
def toxml(pkgDct):
    """
    Export PACKAGES.TXT to a XML database format.
    """
    with open("packages.xml", 'a') as xmlf:
        xmlf.write('\t<package>\n')
        xmlf.write('\t\t<name>' + pkgDct.get("name") + '</name>\n')
        xmlf.write('\t\t<version>' + pkgDct.get("version") + '</version>\n')
        xmlf.write('\t\t<arch>' + pkgDct.get("arch") + '</arch>\n')
        xmlf.write('\t\t<release>' + pkgDct.get("release") + '</release>\n')
        xmlf.write('\t\t<location>' + pkgDct.get("location") + '</location>\n')
        xmlf.write('\t\t<deps>' + pkgDct.get("deps") + '</deps>\n')
        xmlf.write('\t\t<sizec>' + pkgDct.get("sizec") + '</sizec>\n')
        xmlf.write('\t\t<sizeu>' + pkgDct.get("sizeu") + '</sizeu>\n')
        xmlf.write('\t\t<slackdesc>' + pkgDct.get("slackdesc") + '</slackdesc>\n')
        xmlf.write('\t</package>\n')


# parser
def mkdadb(towhat):
    """
    Parse PACKAGES.TXT to get the values we need.
    Choose the export format:
        - CSV  : tocsv
        - JSON : tojson
        - XML  : toxml
    """
    if towhat == tocsv:
        if os.path.isfile("packages.csv"):
            os.remove("packages.csv")
            print "Updating packages.csv"
    if towhat == tojson:
        if os.path.isfile("packages.json"):
            os.remove("packages.json")
            print "Updating packages.json"
        with open("packages.json", 'w') as jsonf:
                jsonf.write('[\n')
    if towhat == toxml:
        if os.path.isfile("packages.xml"):
            os.remove("packages.xml")
            print "Updating packages.xml"
        with open("packages.xml", 'w') as xmlf:
                xmlf.write('<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n')
                xmlf.write('<packages>\n')
    pkg = new_pkgdct()
    with open('PACKAGES.TXT') as f:
        for line in f:
            pkgline = re.match(
                r'(PACKAGE NAME:\s\s)(.*)', line)
            locationline = re.match(
                r'(PACKAGE LOCATION:\s\s\.)(.*)', line)
            depline = re.match(
                r'(PACKAGE REQUIRED:\s\s)(.*)', line)
            sizecline = re.match(
                r'(PACKAGE\sSIZE\s\(compressed\):\s\s)(.*)', line)
            sizeuline = re.match(
                r'(PACKAGE\sSIZE\s\(uncompressed\):\s\s)(.*)', line)
            slackdescline = re.match(
                r'(%s:\s)(.*)' % pkg["name"].replace('+', '\+'), line)
            emptyline = re.match(
                r'^$', line)
            if pkgline:
                pname = pkgline.group(2)
                pname = re.match(
                    r'(.*)-([^-]*)-([^-]*)-([^-]*).t[glx]z$', pname)
                pkg["name"] = pname.group(1)
                pkg["version"] = pname.group(2)
                pkg["arch"] = pname.group(3)
                pkg["release"] = pname.group(4)
            if depline:
                pkg["deps"] = depline.group(2)
            if locationline:
                pkg["location"] = locationline.group(2)
            if sizecline:
                pkg["sizec"] = sizecline.group(2)
            if sizeuline:
                pkg["sizeu"] = sizeuline.group(2)
            if slackdescline:
                pkg["slackdesc"] += " " + slackdescline.group(2).\
                    replace('"', '\'').\
                    replace('&', 'and').\
                    replace('>', '').\
                    replace('<', '')
            if emptyline and pkg.get("name"):
                pkg["slackdesc"] = pkg["slackdesc"].strip()
                towhat(pkg)
                pkg = new_pkgdct()
    if towhat == tojson:
            with open("packages.json", 'a') as jsonf:
                jsonf.write(']\n')
    if towhat == toxml:
            with open("packages.xml", 'a') as xmlf:
                xmlf.write('</packages>\n')


def main():
    pkgtxturl()
    mkdadb(toxml)

if __name__ == '__main__':
    main()
