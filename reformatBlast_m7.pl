#!/usr/bin/perl -w

=pod
description: reformat blastout in format -m 7 (xml) for blast2go.jar
author: Zhang Fangxian, zhangfx@genomics.cn
created date: 20090917
modified date: 20101127, 20091026
=cut

use strict;
use Getopt::Long;

my ($input, $size, $output, $help);

GetOptions("input:s" => \$input, "size:i" => \$size, "output:s" => \$output, "help|?" => \$help);
$size = 100 if (!defined $size);

if (!defined $input || defined $help) {
	die << "USAGE";
description: reformat blastout in format -m 7 (xml) for blast2go.jar
usage: perl $0 [options]
options:
	-input <file> *  input file, output of blast in format -m 7 (xml)
	-size <int>      limit the size of <Iteration> elements in one <BlastOutput> element, default is 100
	-output <file>   output file, default is ./[-input].2.xml

	-help|?          help information
e.g.:
	perl $0 -input 1.xml -size 100 -output 2.xml
USAGE
}

if (!-f $input) {
	die "file $input not exists\n";
}

$output ||= &getFileName($input) . ".2.xml";

open IN, "< $input" or die $!;
open OUT, "> $output" or die $!;

my ($flag, $head, @iterations);
while (<IN>) {
	if (/<\?|<!/) {
		print OUT $_;
		next;
	}
	last if (/<\/BlastOutput_iterations>/);
	if (/<BlastOutput>/) {
			$flag = 1;
			$head = $_;
	} elsif (/<Iteration>/) {
			$flag = 2;
			push @iterations, $_;
	} else {
		if ($flag == 1) {
			$head .= $_;
		} elsif ($flag == 2) {
			$iterations[-1] .= $_;
		}
		if (/<\/Iteration>/ && @iterations == $size) {
			print OUT $head . join("", @iterations);
			print OUT << "XMLCODE";
\t</BlastOutput_iterations>
</BlastOutput>
XMLCODE
			@iterations = ();
		}
	}
}

if (@iterations > 0) {
	print OUT $head . join("", @iterations);
	print OUT << "XMLCODE";
\t</BlastOutput_iterations>
</BlastOutput>
XMLCODE
	@iterations = ();
}

close OUT;
close IN;

exit 0;

sub getFileName {
	my ($file_name) = @_;
	$file_name = (split /[\/\\]/, $file_name)[-1];
	$file_name =~ s/\.[^\.]*$//;
	return $file_name;
}
