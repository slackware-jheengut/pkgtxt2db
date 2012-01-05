#!/bin/sh

PERLVER=5.12.3
PERLDIR=usr/lib${LIBDIRSUFFIX}/perl5/$PERLVER

install -D -m 755 pkgtxt2db $DESTDIR/usr/bin/pkgtxt2db
install -D -m 644 Pkgtxt2db.pm $DESTDIR/$PERLDIR/Pkgtxt2db/Pkgtxt2db.pm

