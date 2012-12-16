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
import sys
import urllib2
import gzip
import re
import argparse
import sqlite3


# Program information
my_url = 'http://www.salixos.org/wiki/index.php/Pkgtxt2db'
my_name = 'pkgtxt2db'
my_version = '0.2.0'


# Parse the CLI options
parser = argparse.ArgumentParser(
        prog='pkgtxt2db',
        description='Convert PACKAGES.TXT to DB',
        epilog=
        "i.e. pkgtxt2db -u -t salix --repo \
            x86_64 -r 14.0 -c json -o salix64.json")

parser.add_argument('-u', '--update', action="store_true",
        default=False,
        help='Download/update the PACKAGES.TXT file')

parser.add_argument('-t', '--target', action="store",
        dest='target',
        help='Choose the O.S.: slackware or salix (default) ')

parser.add_argument('--repo', action="store",
        dest='repo',
        help='Choose the arch repo: x86_64 or i486 (default)')

parser.add_argument('-e', '--expa', action="store",
        dest='expa', default='/',
        help='Choose the slackware extra/patches')

parser.add_argument('-r', '--release', action="store",
        dest='release',
        help='Choose the release: 13.0 to 14.0 (default)')

parser.add_argument('-c', '--convert', action="store",
        dest='convert', default='csv',
        help='Choose the DB format: xml, json, csv, sqlite')

parser.add_argument('-o', '--output', action="store",
        dest='output', default='packages',
        help='Choose the name of your DB file')

parser.add_argument('--version', action='version',
        version='%(prog)s ' + my_version)

if len(sys.argv) == 1:
    sys.exit('Wrong usage, see pkgtxt2db --help')

args = parser.parse_args()

# vars
mirror = 'http://salix.enialis.net/'
pkgtxtz = 'PACKAGES.TXT.gz'
pkgtxt = 'PACKAGES.TXT'
update = args.update
target = args.target
repo = args.repo
release = args.release
expa = args.expa
convert = args.convert
output = args.output
outputfile = '.'.join([output, convert])


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
def pkgtxturl(repo='i486', target='salix', release='14.0', expa='/'):
    """
    Download the slackware/salix PACKAGES.TXT.gz from a built URL and unzip it.
    pkgtxturl(repo, target, release, |extra|patches)
    """

    # Check the repo
    Rep = {'i486', 'x86_64'}
    if repo not in Rep:
        sys.exit('Choose a valid arch please, aborting.')

    # Check if the choosen release is a valid one.
    R = {'13.0', '13.1', '13.37', '14.0', 'current'}
    if release not in R:
        sys.exit('Choose a valid release please, aborting.')

    # Check the target
    if target == 'slackware':
        target = 'slackware-'
    elif target == 'salix':
        target = ''
    else:
        sys.exit('Choose a valid target, aborting.')

    #
    if expa == 'extra':
        expa = '/extra/'
    elif expa == 'patches':
        expa = '/patches/'

    slash = '/'

    # Build the URL to fetch PACKAGES.TXT
    url = mirror + repo + slash + target + release + expa + pkgtxtz

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
    with open(outputfile, 'a') as csvf:
        csvf.write(
            sep.join(map(lambda field: pkgDct.get(field, ''), fields)) + '\n')


# to JSON DB
def tojson(pkgDct):
    """
    Export PACKAGES.TXT to a JSON database format
    """
    with open("pre.json", 'a') as j:
        j.write('  {\n')
        j.write('    \"name\": \"' + pkgDct.get("name") + '\",\n')
        j.write('    \"version\": \"' + pkgDct.get("version") + '\",\n')
        j.write('    \"arch\": \"' + pkgDct.get("arch") + '\",\n')
        j.write('    \"release\": \"' + pkgDct.get("release") + '\",\n')
        j.write('    \"location\": \"' + pkgDct.get("location") + '\",\n')
        j.write('    \"deps\": \"' + pkgDct.get("deps") + '\",\n')
        j.write('    \"sizec\": \"' + pkgDct.get("sizec") + '\",\n')
        j.write('    \"sizeu\": \"' + pkgDct.get("sizeu") + '\",\n')
        j.write('    \"slackdesc\": \"' + pkgDct.get("slackdesc") + '\"\n')
        j.write('  },\n')


# to XML DB
def toxml(pkgDct):
    """
    Export PACKAGES.TXT to a XML database format.
    """
    with open(outputfile, 'a') as xmlf:
        xmlf.write('\t<package>\n')
        xmlf.write('\t\t<name>'
            + pkgDct.get("name") + '</name>\n')
        xmlf.write('\t\t<version>'
            + pkgDct.get("version") + '</version>\n')
        xmlf.write('\t\t<arch>'
            + pkgDct.get("arch") + '</arch>\n')
        xmlf.write('\t\t<release>'
            + pkgDct.get("release") + '</release>\n')
        xmlf.write('\t\t<location>'
            + pkgDct.get("location") + '</location>\n')
        xmlf.write('\t\t<deps>'
            + pkgDct.get("deps") + '</deps>\n')
        xmlf.write('\t\t<sizec>'
            + pkgDct.get("sizec") + '</sizec>\n')
        xmlf.write('\t\t<sizeu>'
            + pkgDct.get("sizeu") + '</sizeu>\n')
        xmlf.write('\t\t<slackdesc>'
            + pkgDct.get("slackdesc") + '</slackdesc>\n')
        xmlf.write('\t</package>\n')


# to SQLite DB
def tosqlite(pkgDct):
    """
    Export PACKAGES.TXT to a SQLite database.
    """
    conn = sqlite3.connect(outputfile)
    # fix sqlite3.ProgrammingError You must not use 8-bit bytestrings unless
    # you use a text_factory that can interpret 8-bit bytestrings
    # (like text_factory = str).
    conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    cursor = conn.cursor()
    # insert data
    cursor.execute("""INSERT INTO pkgtable (name , version , arch, release,
       location, deps, sizec, sizeu, slackdesc) VALUES (?, ?,
       ?, ?, ?, ?, ?, ?, ?)""", (pkgDct.get("name"),
       pkgDct.get("version"), pkgDct.get("arch"),
       pkgDct.get("release"), pkgDct.get("location"),
       pkgDct.get("deps"), pkgDct.get("sizec"),
       pkgDct.get("sizeu"), pkgDct.get("slackdesc")))
    # save data to database
    conn.commit()


# parser
def mkdadb(towhat):
    """
    Parse PACKAGES.TXT to get the values we need.
    Choose the export format:
        - CSV  : tocsv
        - JSON : tojson
        - XML  : toxml
    """
    # delete old file DB
    if os.path.isfile(outputfile):
        os.remove(outputfile)
        print outputfile, 'has been updated.'
    else:
        print outputfile, 'has been built.'
    if towhat == tojson:
        with open("pre.json", 'w') as j:
                j.write('{\n')
                j.write('"packages": [\n')
    if towhat == toxml:
        with open(outputfile, 'w') as xmlf:
                xmlf.write('<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n')
                xmlf.write('<packages>\n')
    if towhat == tosqlite:
        # create the DB
        conn = sqlite3.connect(outputfile)
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE pkgtable
            (name TEXT, version TEXT, arch TEXT, release TEXT,
            location TEXT, deps TEXT, sizec TEXT, sizeu TEXT,
            slackdesc TEXT)""")
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
        with open("pre.json", 'r') as j, open(outputfile, "w") as jsonf:
            alllines = j.readlines()
            alllines[-1] = alllines[-1].replace('},', '}')
            jsonf.writelines(alllines)
            jsonf.write(']\n')
            jsonf.write('}\n')
            os.remove("pre.json")
    if towhat == toxml:
        with open(outputfile, 'a') as xmlf:
            xmlf.write('</packages>\n')
    if towhat == tosqlite:
        conn.close()


def main():
    if not update and not os.path.isfile(pkgtxt):
        sys.exit('No PACKAGES.TXT found, you should fetch one, aborting.')
    elif not update and os.path.isfile(pkgtxt):
        if repo:
            sys.exit(
            "The repo variable can't be setup without --update, aborting.")
        if target:
            sys.exit(
            "The target variable can't be setup without --update, aborting.")
        if release:
            sys.exit(
            "The release variable can't be setup without --update, aborting.")
    else:
        pkgtxturl(repo, target, release, expa)

    if convert == 'csv':
        mkdadb(tocsv)
    elif convert == 'json':
        mkdadb(tojson)
    elif convert == 'xml':
        mkdadb(toxml)
    elif convert == 'sqlite':
        mkdadb(tosqlite)
    else:
        sys.exit('You have to choose a valid database format, aborting.')


if __name__ == '__main__':
    main()
