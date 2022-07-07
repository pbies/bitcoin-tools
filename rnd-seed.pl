#!/usr/bin/env perl
use strict;
use warnings;
use File::Slurp;
use Time::HiRes qw(time);

sub measure_time(&) {
	my($btime, $etime);
	$btime = time();
	&{$_[0]}();
	$etime = time();
	warn "elapsed time was: ", ($etime - $btime)*1000, " ms\n";
};

my $seed="seed.txt";
my $result="result.txt";

open my $resulth, "> $result" or die "can't open $result: $!";

my @seed = read_file($seed);

# magic number
#srand(0);

measure_time {
	for (my $j=0; $j<=10000;$j++) {
		srand($j);
		for (my $i=1; $i <= 12; $i++) {
			my $rnd = int(rand(2048));
			my $item = $seed[$rnd];
			chomp $item;
			print $resulth "$item"." ";
		}
		print $resulth "\n";
	};
};

close $resulth;
