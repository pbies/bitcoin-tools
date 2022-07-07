#!/usr/bin/env perl

use strict; use warnings;

for (my $i = 0 ; $i <= 18000000000 ; $i++) {
	printf "%064x 0\n", $i;
}
