#!/usr/bin/perl -w

=pod
description: convert blast's result from -m7 (xml) to -m8 (tabular, without comment lines)
author: Zhang Fangxian, zhangfx@genomics.cn
created date: 20090910
modified date: 20101127, 20091029, 20091025
=cut

use strict;
use Getopt::Long;

my ($input, $output, $help);

GetOptions(
	"input:s" => \$input,
	"output:s" => \$output,
	"help|?" => \$help,
);

if (!defined $input || !defined $output || defined $help) {
	die << "USAGE";
description: convert blast's result from -m7 (xml) to -m8 (tabular, without comment lines)
usage: perl $0 [options]
options:
	-input <file> *   input file(s), blast's result in format -m7, use "*" to match several files
	-output <file> *  output tabular file

	-help             help information
e.g.:
	perl $0 -input "*.xml" -output m8.tab
USAGE
}

# check input files
if (!glob($input)) {
	die "no input files: $input\n";
}

# main
open OUT, "> $output" or die $!;

for (glob($input)) {
	open IN, "< $_" or die$!;
	my $gap = 0;
	my ($query, $hitId, $hitDef, $bits, $evalue, $qFrom, $qTo, $hFrom, $hTo, $frame, $identity, $length);
	while (<IN>) {
		if (/<(Iteration_query-def)>(.*)<\/\1/) {
			$query = $2;
		} elsif (/<(Hit_id)>(.*)<\/\1/) {
			$hitId = $2;
		} elsif (/<(Hit_def)>([^\s]*).*<\/\1/) {
			$hitDef = $2;
		} elsif (/<(Hsp_bit-score)>(.*)<\/\1/) {
			$bits = $2;
		} elsif (/<(Hsp_evalue)>(.*)<\/\1/) {
			$evalue = $2;
		} elsif (/<(Hsp_query-from)>(.*)<\/\1/) {
			$qFrom = $2;
		} elsif (/<(Hsp_query-to)>(.*)<\/\1/) {
			$qTo = $2;
		} elsif (/<(Hsp_hit-from)>(.*)<\/\1/) {
			$hFrom = $2;
		} elsif (/<(Hsp_hit-to)>(.*)<\/\1/) {
			$hTo = $2;
		} elsif (/<(Hsp_query-frame)>(.*)<\/\1/){ # frame, added by Huang Fei, huangfei@genomics.cn
			$frame = $2;
		} elsif (/<(Hsp_identity)>(.*)<\/\1/) {
			$identity = $2;
		} elsif (/<(Hsp_gaps)>(.*)<\/\1/) {
			$gap = $2;
		} elsif (/<(Hsp_align-len)>(.*)<\/\1/) {
			$length = $2;
		} elsif (/<\/Hsp>/) {
			my $percent = sprintf("%.2f", $identity / $length * 100);
			my $hit = ($hitId =~ /gi/)? $hitId : $hitDef;
			print OUT "$query\t$hit\t$percent\t$length\t" . ($length - $identity) . "\t$gap\t$qFrom\t$qTo\t$hFrom\t$hTo\t$evalue\t$bits\t$frame\n";
			$gap = 0;
		}
	}
	close IN;
}

close OUT;

exit 0;
