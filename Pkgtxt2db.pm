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
our $slack_mirror="ftp://ftp.osuosl.org/pub/slackware";
our $a32 = "slackware-";
our $a64 = "slackware64-";
our $slack32url = "$slack_mirror/$a32$release/PACKAGES.TXT";
our $slack64url = "$slack_mirror/$a64$release/PACKAGES.TXT";
our $slackpkgtxt = "/tmp/slackwarePACKAGES.TXT";

sub new {
    my $self = {};
    bless ($self);
    return $self;
}

# Pkgtxt2db->get_file($url,$pkgtxt)
sub get_file {
    our ($a,$b) = @_;
    mirror($a, $b) or die "Error: could not fetch $a\n";
}

# 
# make the file an array
#
# Salix
# Pkgtxt2db->salix_data()
sub salix_data {
    open F, "<$pkgtxt" or die $!;
    our @salix_d = <F>;
    close (F);
    return @salix_d;
}
# Slackware
# Pkgtxt2db->slack_data()
sub slack_data {
    open G, "<$slackpkgtxt" or die $!;
    our @slack_d = <G>;
    close (G);
    return @slack_d;
}


#
# Make the hash of array database
our %pkgdb;

sub mkdadb {
    our $self = shift;

    our @d = salix_data() unless defined(@d);
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
        if (@d = slack_data()) {
            our %slackdb = %pkgdb;
            return \%slackdb;
        } else {
            return %pkgdb;
        }
    }
}

# 
# CSV
#
sub s2csv {
    open(SACSV, ">pkgtxt.csv");
    my $c = "\t";
    print SACSV "pkgname${c}pkgver${c}arch${c}pkgrel${c}location${c}dep${c}sizeC${c}sizeU\n";
    for my $p ( sort keys %pkgdb ) {
        printf SACSV "%s$c%s$c%s$c%s$c%s$c%s$c%s$c%s\n",
        $p, $pkgdb{$p}[1], $pkgdb{$p}[2], $pkgdb{$p}[3], $pkgdb{$p}[4], $pkgdb{$p}[5], $pkgdb{$p}[6], $pkgdb{$p}[7];
    }
    close (SACSV);
}

sub s2json {
    open(SAJSON, ">pkgtxt.json");
    print SAJSON "\[\n";
    for my $p ( keys %pkgdb ) {
        print SAJSON "  \{\n";
        print SAJSON "    \"pkgname\": \"$p\",\n";
        print SAJSON "    \"pkgver\": \"$pkgdb{$p}[1]\",\n";
        print SAJSON "    \"arch\": \"$pkgdb{$p}[2]\",\n";
        print SAJSON "    \"pkgver\": \"$pkgdb{$p}[3]\",\n";
        print SAJSON "    \"location\": \"$pkgdb{$p}[4]\",\n";
        print SAJSON "    \"dep\": \"$pkgdb{$p}[5]\",\n";
        print SAJSON "    \"sizeC\": \"$pkgdb{$p}[6]\",\n";
        print SAJSON "    \"sizeU\": \"$pkgdb{$p}[7]\"\n";
        print SAJSON "  \},\n";
    }
    print SAJSON "\]\n";
    close (SAJSON);
}

1;
