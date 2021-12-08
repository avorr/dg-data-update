#!/usr/bin/perl

use strict;
use warnings;

use Expect;

die "Must be 3 arguments" if ($#ARGV != 2);

my $host = $ARGV[0];            # HOST
my $login = $ARGV[1];           # LOGIN
my $password = $ARGV[2];        # PASSWORD

my $exp = Expect->spawn('/opt/forticlient/vpn', '--server=' . $host, '--user=' . $login, '-p') or die $!;
#$exp->log_stdout(0);
$exp->expect(2, 'password:');
$exp->send($password . "\n");
$exp->expect(2, 'Confirm (y/n)');
$exp->send('y' . "\n");
$exp->interact();
#$exp->soft_close();