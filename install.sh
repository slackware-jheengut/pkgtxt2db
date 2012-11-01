#!/bin/sh

install -D -m 755 pkgtxt2db.py $DESTDIR/usr/bin/pkgtxt2db

# man page
txt2tags pkgtxt2db.t2t || return 1
install -D -m 644 pkgtxt2db.man $DESTDIR/usr/man/man1/pkgtxt2db.1
