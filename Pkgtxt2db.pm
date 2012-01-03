package Pkgtxt2db;

#
# Pkgtxt2db.pm
#
# This file is part of pkgtxt2db
# copyright 2011 Frédéric Galusik <fredg~at~salixos~dot~org>
#
# License: BSD Revised
#

use strict;
use warnings;

use LWP::Simple;

#
# Get the PACKAGES.TXT file
# 
#
# Salix
our $salix_mirror = "http://salix.enialis.net";
our $arch32 = "i486";
our $arch64 = "x86_64";
our $release = "13.37";
our $pkgtxt = "/tmp/salixPACKAGES.TXT";
our $url32 = "$salix_mirror/$arch32/$release/PACKAGES.TXT";
our $url64 = "$salix_mirror/$arch64/$release/PACKAGES.TXT";
# Slackware
our $slack_mirror="http://slackware.org.uk/slackware";
our $a32 = "slackware";
our $a64 = "slackware64";
our $slackurl32 = "$slack_mirror/${a32}-${release}/PACKAGES.TXT";
our $slackurl64 = "$slack_mirror/${a64}-${release}/PACKAGES.TXT";
our $slackpkgtxt = "/tmp/slackwarePACKAGES.TXT";

sub new {
    my $self = {};
    bless ($self);
    return $self;
}

# 
# build an array with all file lines
#
# Salix
# Pkgtxt2db->getsalix_d32()
#
sub getsalix_d32 {
    my $status = getstore($url32,$pkgtxt);
    if ( is_success($status) ) {
        print "PACKAGES.TXT downloaded correctly.\n";
    } else {
        print "PACKAGES.TXT not downloaded: $status\n";
    }
}
sub getsalix_d64 {
    my $status = getstore($url64,$pkgtxt);
    if ( is_success($status) ) {
        print "PACKAGES.TXT downloaded correctly.\n";
    } else {
        print "PACKAGES.TXT not dowloaded: $status\n";
    }
}

sub salix_data {
    open F, "<$pkgtxt" or die "No Salix PACKAGES.TXT file, aborting.\n";
    our @salix_d = <F>;
    close (F);
    return @salix_d;
}

# Slackware
# Pkgtxt2db->getslack_d32()
# 
sub getslack_d32 {
    my $status = getstore($slackurl32,$slackpkgtxt);
    if ( is_success($status) ) {
        print "PACKAGES.TXT downloaded correctly.\n";
    } else {
        print "PACKAGES.TXT not downloaded: $status\n";
    }
}
sub getslack_d64 {
    my $status = getstore($slackurl64,$slackpkgtxt);
    if ( is_success($status) ) {
        print "PACKAGES.TXT downloaded correctly.\n";
    } else {
        print "PACKAGES.TXT not downloaded: $status\n";
    }
}
sub slack_data {
    open G, "<$slackpkgtxt" or die $!;
    our @slack_d = <G>;
    close (G);
    return @slack_d;
}

#
# Make the hash of array database
#
# Salix DB
# Pkgtxt2db->mkdasalixdb()
#
our %pkgdb;

sub mkdasalixdb {
    our $self = shift;

    our @d = salix_data();
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
        else {
            next;
        }
            return %pkgdb;
    }
}

#
# Slackware DB
# Pkgtxt2db->mkdaslackdb()
#
our %slackdb;

sub mkdaslackdb {
    our $self = shift;

    our @da = slack_data();
    our $name;
    our $pkg;
   
    foreach (@da) {
        chomp $_;
        if ($_ =~ /^$/){
            next;
        }
        if ($_ =~ /(^PACKAGE NAME:\s\s)(.*)/) {
            $name = "$2";
            $name =~ /^(.*)-([^-]*)-([^-]*)-([^-]*).t[glx]z$/;
            $pkg = "$1";
            $slackdb{$pkg}[0] = "$name";
            $slackdb{$pkg}[1] = "$2";
            $slackdb{$pkg}[2] = "$3";
            $slackdb{$pkg}[3] = "$4";
            next;
        }
        if ($_ =~ /(^PACKAGE LOCATION:\s\s\.)(.*)/) {
            $slackdb{$pkg}[4] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE REQUIRED:\s\s)(.*)/) {
            $slackdb{$pkg}[5] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE\sSIZE\s\(compressed\):\s\s)(.*)/) {
            $slackdb{$pkg}[6] = "$2";
            next;
        }
        if ($_ =~ /(^PACKAGE\sSIZE\s\(uncompressed\):\s\s)(.*)/) {
            $slackdb{$pkg}[7] = "$2";
            next;
        }
        else {
            next;
        }
            return %slackdb;
    }
}

# 
# CSV
#
sub salix2csv {
    open(C, ">pkgtxt.csv") or die "Unable to open pkgtxt.csv for writing, aborting.";
    my $c = "\t";
    print C "pkgname${c}pkgver${c}arch${c}pkgrel${c}location${c}dep${c}sizeC${c}sizeU\n";
    for my $p ( sort keys %pkgdb ) {
        printf C "%s$c%s$c%s$c%s$c%s$c%s$c%s$c%s\n",
        $p, $pkgdb{$p}[1], $pkgdb{$p}[2], $pkgdb{$p}[3], $pkgdb{$p}[4], $pkgdb{$p}[5], $pkgdb{$p}[6], $pkgdb{$p}[7];
    }
    close (C);
    print "Salix pkgtxt.csv has been built.\n";
}

sub slack2csv {
    open(D, ">pkgtxt.csv") or die "Unable to open pkgtxt.csv for writing, aborting.";
    my $c = "\t";
    print D "pkgname${c}pkgver${c}arch${c}pkgrel${c}location${c}dep${c}sizeC${c}sizeU\n";
    for my $q ( sort keys %slackdb ) {
        printf D "%s$c%s$c%s$c%s$c%s$c%s$c%s$c%s\n",
        $q, $slackdb{$q}[1], $slackdb{$q}[2], $slackdb{$q}[3], $slackdb{$q}[4], $slackdb{$q}[5], $slackdb{$q}[6], $slackdb{$q}[7];
    }
    close (D);
    print "Slackware pkgtxt.csv has been built.\n";
}


#
# JSON
#
sub salix2json {
    my $out = "pkgtxt.json";
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
        print J "  \}\n";
    }
    print J "\]\n";
    close (J);
    print "Salix pkgtxt.json has been built.\n";
}

sub slack2json {
    my $out = "pkgtxt.json";
    my $nb = keys %slackdb;
    open(K, ">$out") or die "Unable to open $out for writing, aborting.";
    print K "\[\n"; 
    for my $q ( (keys %slackdb)[0..($nb-2)] ) {
        print K "  \{\n";
        print K "    \"pkgname\": \"$q\",\n";
        print K "    \"pkgver\": \"$slackdb{$q}[1]\",\n";
        print K "    \"arch\": \"$slackdb{$q}[2]\",\n";
        print K "    \"pkgver\": \"$slackdb{$q}[3]\",\n";
        print K "    \"location\": \"$slackdb{$q}[4]\",\n";
        print K "    \"dep\": \"$slackdb{$q}[5]\",\n";
        print K "    \"sizeC\": \"$slackdb{$q}[6]\",\n";
        print K "    \"sizeU\": \"$slackdb{$q}[7]\"\n";
        print K "  \},\n";
    }
    for my $q ( (keys %slackdb)[($nb-1)] ) {
        print K "  \{\n";
        print K "    \"pkgname\": \"$q\",\n";
        print K "    \"pkgver\": \"$slackdb{$q}[1]\",\n";
        print K "    \"arch\": \"$slackdb{$q}[2]\",\n";
        print K "    \"pkgver\": \"$slackdb{$q}[3]\",\n";
        print K "    \"location\": \"$slackdb{$q}[4]\",\n";
        print K "    \"dep\": \"$slackdb{$q}[5]\",\n";
        print K "    \"sizeC\": \"$slackdb{$q}[6]\",\n";
        print K "    \"sizeU\": \"$slackdb{$q}[7]\"\n";
        print K "  \}\n";
    }
    print K "\]\n";
    close (K);
    print "Slackware pkgtxt.json has been built.\n";
}


1;
