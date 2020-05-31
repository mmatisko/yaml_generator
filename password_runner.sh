#!/usr/bin/expect
set cmd [lrange $argv 1 end]
set val [lindex $argv 0]

eval spawn $cmd
expect "template:"
send "$val\r";
interact
