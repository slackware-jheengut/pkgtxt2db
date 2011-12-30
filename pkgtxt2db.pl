#!/usr/bin/env perl
#
# spkg2db.pl
#
# copyright 2011 Frédéric Galusik <fredg~at~salixos~dot~org>
#
# License: BSD Revised
#
# This perl module will convert the Slackware/Salix PACKAGES.TXT file
# to some various database format : CSV,  
#

use strict;
use warnings;

use LWP::Simple;


my $download_mirror = "http://salix.enialis.net";
my $arch = "i486";
my $release = "13.37";
my $pkgtxt = "/tmp/PACKAGES.TXT";
my $url = "$download_mirror/$arch/$release/PACKAGES.TXT";

sub get_pkgtxt
{
	my ($url,$pkgtxt) = @_;
	mirror($url, $pkgtxt) or die "Error: could not fetch $url\n";
}
get_pkgtxt($url,$pkgtxt);


open FILE, "<$pkgtxt" or die $!;
my @data = <FILE>;
close (FILE);

my $pname;
my $plocation;
my $pdep;
my $pdesc;
my $psizec;
my $psizeu;

sub mkdadb {
		my $self = shift;
		my $dbtype = $_;
		foreach (@data) {
				chomp $_;
				if ($_ =~ /^$/){
						next;
				}
				if ($_ =~ /(^PACKAGE NAME:\s\s)(.*)(\.t[glx]z)/) {
						$pname = $2;
				}
				if ($_ =~ /(^PACKAGE LOCATION:\s\s\.)(.*)/) {
						$plocation = $2;
				}
				if ($_ =~ /(^PACKAGE REQUIRED:\s\s)(.*)/) {
						$pdep = $2;
				}
				if ($_ =~ /(^PACKAGE\sSIZE\s\(compressed\):\s\s)(.*)/) {
						$psizec = $2;
				}
				if ($_ =~ /(^PACKAGE\sSIZE\s\(uncompressed\):\s\s)(.*)/) {
						$psizeu = $2;
				}
				else {
						next;
				}
				tocsv();
		}
}
sub tocsv {
		print "$pname\@$plocation\@$pdep\@$psizec\@$psizeu\n";
}

mkdadb();

