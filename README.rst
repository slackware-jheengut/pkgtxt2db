Pkgtxt2db
#########

Pkgtxt2db is a utility for Slackware and Slackware based operating system only.

It can be use to convert PACKAGES.TXT to various database formats:
Are supported:

* CSV
* JSON
* SQLITE
* XML

It relies on the ParsePkgtxt Python Class:
https://github.com/fredg/ParsePkgtxt

Download:
---------
Sources tarballs and Slackware packages can be found there:

http://people.salixos.org/fredg/packages/Pkgtxt2db/

GIT:
----
git clone git@github.com:fredg/pkgtxt2db.git

GENERAL OPTIONS
---------------

    -h, --help
    	Simple help
    --version
        Print pkgtxt2db version
    -u, --update
        It will fetch and download a new PACKAGES.TXT from your choosen repository.
    -t, --target
        Choose between slackware or salix repositories.
    --repo
    	Choose the arch repository, it can be i486 or x86_64
    -r, --release
        Choose the slackware or salix release. It can be: current (if exist),
        14.0, 13.37, ..., 13.0
    -e, --expa
        Choose between the patches or extra Slackware repository
    -c, --convert
        Choose your database format, it can be:
                   	- csv   : Convert PACKAGES.TXT to a CSV database
			- json  : Convert PACKAGES.TXT to a JSON database
			- sqlite: Convert PACKAGES.TXT to a SQLITE database
			- xml   : Convert PACKAGES.TXT to a XML database
    -o, --output
        Choose the name of the output file.  If none is choosen, packages will be used.

COMMAND LINE USAGE
------------------

Here are some usages examples.

	pkgtxt2db -u -t slackware --repo x86_64 -r 14.0 -c sqlite -o slackware64
    
It will fetch and convert PACKAGES.TXT from the Slackware64 14.0 repository to a SQLITE
database: slackware64.sqlite.

	pkgtxt2db -c csv

It will convert the PACKAGES.TXT found in your directory to a CSV database (; separated):
packages.csv.  You can open it with libreoffice ;)

