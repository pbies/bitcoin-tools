#!/usr/bin/env perl

use strict; use warnings;

for my $i (0..255) {
    printf "%02x\n", $i;
}

for my $i (0..65535) {
    printf "%04x\n", $i;
}
