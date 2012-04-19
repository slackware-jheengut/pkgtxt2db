package Pkgtxt2db;

#
# Pkgtxt2db.pm
#
# This file is part of pkgtxt2db
# copyright 2011 Frédéric Galusik <fredg~at~salixos~dot~org>
#
# License: BSD Revised
#
use 5.010;
use strict;
use warnings;

use LWP::Simple;

our $pkgtxt = "PACKAGES.TXT";
our @releases = ("13.37","current");
our $release;
our $url;
our $target;
our @targets = qw/salix32 salix64 slack32 slack64/;
our %pkgdb;
#
# Salix vars
#
our $salix32 = "salix32";
our $salix64 = "salix64";
our $salix_mirror = "http://salix.enialis.net";
#
# Slackware vars
#
our $slack32 = "slack32";
our $slack64 = "slack64";
our $slack_mirror="http://slackware.org.uk/slackware";
#

sub new {
    my $self = {};
    bless ($self);
    return $self;
}

#
# choose the release
#
sub checkrelease {
    if ($release ~~ @releases) {
        print "Release: $release\n";
    } else {
        die "Not a valid release, see --help\n";
        }
    }

#
# choose the target between salix or slackware, i486 or x86_64
#
sub checktarget {
    if ($target ~~ @targets) {
        print "Target: $target\n";
    } else {
        die "You must choose a valid target, see --help\n";
    }
}

#
# build an array with all file lines
#
# Get the PACKAGES.TXT file
# Pkgtxt2db->getpkgtxt()
#
sub getpkgtxt {
    if ($target eq $salix32) {
        $url = "$salix_mirror/i486/$release/$pkgtxt";
    } elsif ($target eq $salix64) {
        $url = "$salix_mirror/x86_64/$release/$pkgtxt";
    } elsif ($target eq $slack32) {
        $url = "$slack_mirror/slackware-${release}/$pkgtxt";
    } elsif ($target eq $slack64) {
        $url = "$slack_mirror/slackware64-${release}/$pkgtxt";
    }
    print "URL: $url\n";
    my $status = getstore($url,$pkgtxt);
    if ( is_success($status) ) {
        print "PACKAGES.TXT downloaded correctly.\n";
    } else {
        print "PACKAGES.TXT not downloaded: $status\n";
    }
}


#
# turn PACKAGES.TXT to a array
#
sub getdata {
    open F, "<$pkgtxt" or die "No PACKAGES.TXT file, aborting.\n";
    our @data = <F>;
    close (F);
    return @data;
}

#
# Make the hash of array database
#
# build the DB
# Pkgtxt2db->mkdadb()
#
sub mkdadb {
    our $self = shift;

    our @d = getdata();
    our $pname;
    our $pkgname;

    foreach (@d) {
        chomp $_;
        if ($_ =~ /^$/){
            next;
        }
        if ($_ =~ /(^PACKAGE NAME:\s\s)(.*)/) {
            $pname = "$2";
            $pname =~ /^(.*)-([^-]*)-([^-]*)-([^-]*).t[glx]z$/;
            $pkgname = "$1";
            $pkgdb{$pkgname}[0] = "$pname";
            $pkgdb{$pkgname}[1] = "$2";
            $pkgdb{$pkgname}[2] = "$3";
            $pkgdb{$pkgname}[3] = "$4";
            next;
        }
        if ($_ =~ /(^PACKAGE LOCATION:\s\s\.)(.*)/) {
            $pkgdb{$pkgname}[4] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE REQUIRED:\s\s)(.*)/) {
            $pkgdb{$pkgname}[5] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE\sSIZE\s\(compressed\):\s\s)(.*)/) {
            $pkgdb{$pkgname}[6] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE\sSIZE\s\(uncompressed\):\s\s)(.*)/) {
            $pkgdb{$pkgname}[7] = "$2";
            next;
        }
        if (($_ =~ /\Q${pkgname}\E:(.*)/) && (defined($pkgname))) {
            $pkgdb{$pkgname}[8] = $pkgdb{$pkgname}[8] . "$1";
            # clean space
            $pkgdb{$pkgname}[8] =~ s/ +/ /g;
            # clean xml output: & < > cannot be in a varchar
            $pkgdb{$pkgname}[8] =~ s/&/and/g;
            $pkgdb{$pkgname}[8] =~ s/(<)|(>)//g;
            # clean csv output: " in pkgdesc is shit
            $pkgdb{$pkgname}[8] =~ s/"/'/g;
            next;
        }
        else {
            next;
        }
            return %pkgdb;
    }
}

#
# CSV
#
sub tocsv {
    open(C, ">$target-$release.csv") or die "Unable to open $target-$release.csv for writing, aborting.";
    # choose the CSV separator, \t = tab \@ = @ ....
    # avoid the comma (,) as it is the separator for dependancies
    my $c = "\"\;\"";
    print C "\"pkgname${c}pkgver${c}arch${c}pkgrel${c}location${c}dep${c}sizeC${c}sizeU${c}Desc\"\n";
    for my $p ( sort keys %pkgdb ) {
        printf C "\"%s$c%s$c%s$c%s$c%s$c%s$c%s$c%s$c%s\"\n",
        $p, $pkgdb{$p}[1], $pkgdb{$p}[2], $pkgdb{$p}[3], $pkgdb{$p}[4], $pkgdb{$p}[5], $pkgdb{$p}[6], $pkgdb{$p}[7], $pkgdb{$p}[8];
    }
    close (C);
    print "$target-$release.csv has been built.\n";
}

#
# JSON
#
sub tojson {
    my $out = "$target-$release.json";
    my $n = keys %pkgdb;
    open(J, ">$out") or die "Unable to open $out for writing, aborting.";
    print J "\[\n";
    for my $p ( (keys %pkgdb)[0..($n-2)] ) {
        print J "  \{\n";
        print J "    \"pkgname\": \"$p\",\n";
        print J "    \"pkgver\": \"$pkgdb{$p}[1]\",\n";
        print J "    \"arch\": \"$pkgdb{$p}[2]\",\n";
        print J "    \"pkgver\": \"$pkgdb{$p}[3]\",\n";
        print J "    \"location\": \"$pkgdb{$p}[4]\",\n";
        print J "    \"dep\": \"$pkgdb{$p}[5]\",\n";
        print J "    \"sizeC\": \"$pkgdb{$p}[6]\",\n";
        print J "    \"sizeU\": \"$pkgdb{$p}[7]\"\n";
        print J "    \"pkgdesc\: \"$pkgdb{$p}[8]\"\n";
        print J "  \},\n";
    }
    for my $p ( (keys %pkgdb)[($n-1)] ) {
        print J "  \{\n";
        print J "    \"pkgname\": \"$p\",\n";
        print J "    \"pkgver\": \"$pkgdb{$p}[1]\",\n";
        print J "    \"arch\": \"$pkgdb{$p}[2]\",\n";
        print J "    \"pkgver\": \"$pkgdb{$p}[3]\",\n";
        print J "    \"location\": \"$pkgdb{$p}[4]\",\n";
        print J "    \"dep\": \"$pkgdb{$p}[5]\",\n";
        print J "    \"sizeC\": \"$pkgdb{$p}[6]\",\n";
        print J "    \"sizeU\": \"$pkgdb{$p}[7]\"\n";
        print J "    \"pkgdesc\: \"$pkgdb{$p}[8]\"\n";
        print J "  \}\n";
    }
    print J "\]\n";
    close (J);
    print "$target-$release.json has been built.\n";
}

sub toxml {
    my $outx = "$target-$release.xml";
    open(X, ">$outx") or die "Unable to open $outx for writing, aborting.";
    print X "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n";
    print X "<packages>\n";
    for my $p (keys %pkgdb) {
        print X "\t<package>\n";
        print X "\t\t<pkgname>$p</pkgname>\n";
        print X "\t\t<pkgver>$pkgdb{$p}[1]</pkgver>\n";
        print X "\t\t<arch>$pkgdb{$p}[2]</arch>\n";
        print X "\t\t<pkgver>$pkgdb{$p}[3]</pkgver>\n";
        print X "\t\t<location>$pkgdb{$p}[4]</location>\n";
        print X "\t\t<dep>$pkgdb{$p}[5]</dep>\n";
        print X "\t\t<sizeC>$pkgdb{$p}[6]</sizeC>\n";
        print X "\t\t<sizeU>$pkgdb{$p}[7]</sizeU>\n";
        print X "\t\t<pkgdesc>$pkgdb{$p}[8]</pkgdesc>\n";
        print X "\t</package>\n";
    }
    print X "</packages>\n";
}

1;
