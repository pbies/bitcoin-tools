#!/usr/bin/env perl

# > output.txt

use strict; use warnings;
use Encode;

for my $i (0..255) {
    printf chr($i) . "\n";
}

for my $i (0..65535) {
    printf chr($i) . "\n";
}
