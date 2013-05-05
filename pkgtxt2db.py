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
# formats : CSV, json, SQLite, xml
#

import os
import sys
import urllib2
import gzip
import re
import argparse
import sqlite3
from ParsePkgtxt import Package

# Program information
my_url = 'http://www.salixos.org/wiki/index.php/Pkgtxt2db'
my_name = 'pkgtxt2db'
my_version = '0.2.2.1'

# Parse the CLI options
parser = argparse.ArgumentParser(
        prog='pkgtxt2db',
        description='Convert PACKAGES.TXT to DB',
        epilog=
        "i.e. pkgtxt2db -u -t salix --repo \
            x86_64 -r 14.0 -c json -o salix64")

parser.add_argument('-u', '--update', action="store_true",
        default=False,
        help='Download/update the PACKAGES.TXT file')

parser.add_argument('-t', '--target', action="store",
        dest='target',
        help='Choose the O.S.: slackware or salix')

parser.add_argument('-a', '--allrepo', action="store_true",
        default=False,
        help='Choose the main slackware repo + extra + patches')

parser.add_argument('--repo', action="store",
        dest='repo',
        help='Choose the arch repo: x86_64 or i486')

parser.add_argument('-e', '--expa', action="store",
        dest='expa', default='/',
        help='Choose the slackware extra/patches repository')

parser.add_argument('-r', '--release', action="store",
        dest='release',
        help='Choose the release: 13.0 to 14.0')

parser.add_argument('-c', '--convert', action="store",
        dest='convert', default='csv',
        help='Choose the DB format: csv, json, sqlite, xml')

parser.add_argument('-o', '--output', action="store",
        dest='output', default='packages',
        help='Choose the name of your DB file')

parser.add_argument('--version', action='version',
        version='%(prog)s ' + my_version)

if len(sys.argv) == 1:
    sys.exit('Wrong usage, see pkgtxt2db --help')

args = parser.parse_args()

# vars
#mirror = 'http://salix.enialis.net/'
mirror = 'http://download.salixos.org/'
pkgtxtz = 'PACKAGES.TXT.gz'
pkgtxt = 'PACKAGES.TXT'
update = args.update
allrepo = args.allrepo
target = args.target
repo = args.repo
release = args.release
expa = args.expa
convert = args.convert
output = args.output
outputfile = '.'.join([output, convert])
tmpfile = '/tmp/' + outputfile

PACKAGETXT = 'PACKAGES.TXT'

def pkgdic():
    """
    Build the dictionnary from PACKAGES.TXT
    """
    return Package.parse(Package(), PACKAGETXT)


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
    # remove pkgtxtz
    if os.path.isfile(pkgtxtz):
        os.remove(pkgtxtz)
        print "Remove old ", pkgtxtz
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
    fout = open(pkgtxt, 'a')
    with gzip.open(pkgtxtz, 'rb') as f:
        for line in f:
            fout.write(line)
    fout.close()


# to CSV DB
def tocsv(sep=";"):
    """
    Export PACKAGES.TXT to a CSV database format.
    The separated string can be choosen with the sep var, default is ;
    """
    with open(outputfile, 'w') as csvf:
        for k, v in pkgdic().iteritems():
            csvf.write(sep.join([
                        k,v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8],v[9]
                        ]) + '\n')

# to JSON DB
def tojson():
    """
    Export PACKAGES.TXT to a JSON database format
    """
    with open(tmpfile, 'w') as j:
        j.write('{\n')
        j.write('"packages": [\n')
        for k, v in sorted(pkgdic().items()):                
            j.write('  {\n')
            j.write('    \"name\": \"' + k + '\",\n')
            j.write('    \"version\": \"' + v[0] + '\",\n')
            j.write('    \"arch\": \"' + v[1] + '\",\n')
            j.write('    \"release\": \"' + v[2] + '\",\n')
            j.write('    \"deps\": \"' + v[3] + '\",\n')
            j.write('    \"cons\": \"' + v[4] + '\",\n')
            j.write('    \"sugs\": \"' + v[5] + '\",\n')
            j.write('    \"location\": \"' + v[6] + '\",\n')
            j.write('    \"sizec\": \"' + v[7] + '\",\n')
            j.write('    \"sizeu\": \"' + v[8] + '\",\n')
            j.write('    \"slackdesc\": \"' + v[9] + '\"\n')
            j.write('  },\n')
    with open(tmpfile, 'r') as j, open(outputfile, "w") as jsonf:
        alllines = j.readlines()
        alllines[-1] = alllines[-1].replace('},', '}')
        jsonf.writelines(alllines)
        jsonf.write(']\n')
        jsonf.write('}\n')
        os.remove(tmpfile)

# to XML DB
def toxml():
    """
    Export PACKAGES.TXT to a XML database format.
    """
    with open(outputfile, 'w') as xmlf:
        xmlf.write('<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n')
        xmlf.write('<packages>\n')
        for k, v in sorted(pkgdic().iteritems()):
            xmlf.write('\t<package>\n')
            xmlf.write('\t\t<name>' + k + '</name>\n')
            xmlf.write('\t\t<version>' + v[0] + '</version>\n')
            xmlf.write('\t\t<arch>' + v[1] + '</arch>\n')
            xmlf.write('\t\t<release>' + v[2] + '</release>\n')
            xmlf.write('\t\t<deps>' + v[3] + '</deps>\n')
            xmlf.write('\t\t<cons>' + v[4] + '</cons>\n')
            xmlf.write('\t\t<sugs>' + v[5] + '</sugs>\n')
            xmlf.write('\t\t<location>' + v[6] + '</location>\n')
            xmlf.write('\t\t<sizec>' + v[7] + '</sizec>\n')
            xmlf.write('\t\t<sizeu>' + v[8] + '</sizeu>\n')
            xmlf.write('\t\t<slackdesc>' + v[9] + '</slackdesc>\n')
            xmlf.write('\t</package>\n')
        xmlf.write('</packages>\n')

# to SQLite DB
def tosqlite():
    """
    Export PACKAGES.TXT to a SQLite database.
    """
    # We initialize the con variable to None. In case we could not create a connection 
    # to the database (for example the disk is full), we would not have a connection 
    # variable defined. This would lead to an error in the finally clause.     
    conn = None
    # create the DB
    conn = sqlite3.connect(outputfile)
    cursor = conn.cursor()

    # create a table
    cursor.execute(
"""
CREATE TABLE pkgtable
(name TEXT, version TEXT, arch TEXT, release TEXT, deps TEXT, cons TEXT, 
sugs TEXT, location TEXT, sizec TEXT, sizeu TEXT, slackdesc TEXT)
""")
    conn = sqlite3.connect(outputfile)
    # fix sqlite3.ProgrammingError You must not use 8-bit bytestrings unless
    # you use a text_factory that can interpret 8-bit bytestrings
    # (like text_factory = str).
    conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    cursor = conn.cursor()
    # insert data
    for k, v in sorted(pkgdic().iteritems()):
        cursor.execute("""INSERT INTO pkgtable (
name , version , arch, release, deps, cons, sugs, location, sizec, sizeu, 
slackdesc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        [k, v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9]])
    # save data to database
    conn.commit()
    conn.close()

def clean_pkgtxt():
    # remove old PACKAGES.TXT
    if os.path.isfile(pkgtxt):
        os.remove(pkgtxt)
        print "Remove old ", pkgtxt

def clean_outputfile():
    # Delete old files
    if os.path.isfile(outputfile):
        os.remove(outputfile)
        print outputfile, 'is being updated.'
    else:
        print outputfile, 'is being built.'

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
    elif allrepo and target == 'salix':
        sys.exit(
            "The allrepo variable is useless with the salix one, aborting.")
    elif allrepo:
        clean_pkgtxt()
        pkgtxturl(repo, target, release, expa)
        pkgtxturl(repo, target, release, expa='/extra/')
        pkgtxturl(repo, target, release, expa='/patches/')
    else:
        clean_pkgtxt()
        pkgtxturl(repo, target, release, expa)

    clean_outputfile()

    # Check ARGVS
    if convert == 'csv':
        tocsv()
    elif convert == 'json':
        tojson()
    elif convert == 'xml':
        toxml()
    elif convert == 'sqlite':
        tosqlite()
    else:
        sys.exit('You have to choose a valid database format, aborting.')

if __name__ == '__main__':
    main()
