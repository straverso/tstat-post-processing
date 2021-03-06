#!/usr/bin/perl
# Create an histogram from a columnar file
# 
# OUTPUT - a table with
# bin= the bin index
# range= the central value of this bin
# totbin = the number of samples in this bin
# dist = the probabilty of this bin (totbin/tot)
# cum = the PDF up to this point 
# 


if($#ARGV!=4)
{
    printf("Usage: make_histo.pl <file> <column> <min> <max> <bins>\n");
    printf("       file can be - to read from stdin\n");
    printf("       min and max can be \"auto\"\n");
    printf("       bin is the total number of bin.\n");
    printf("       If a value is larger than max, it is accumulated in the last bin too\n");
    
    exit(1);
}

$filename=$ARGV[0];
$param=$ARGV[1];
$min=$ARGV[2];
$max=$ARGV[3];
$bins=$ARGV[4];

if($max=~'auto')
{
   $max=-9999999;
   open(IN_file,$filename) or die ("can't open $filename\n");
   while (($line = <IN_file>)) {
        chomp ($line);
    if ($line !~ /#/)
    {
        @data = split(' ', $line);
        $dat=$data[$param-1];
        if($max<$dat)
        {
                $max=$dat;
        }
    }
   }
   close(IN_file);
}

if($min=~'auto')
{
   $min=99999999;
   open(IN_file,$filename) or die ("can't open $filename\n");
   while (($line = <IN_file>)) {
        chomp ($line);
    if ($line !~ /#/)
    {
        @data = split(' ', $line);
        $dat=$data[$param-1];
        if($min>$dat)
        {
                $min=$dat;
        }
    }
   }
   close(IN_file);
}

print "#making histogram $filename $param $min $max $bins\n";
for($i=0;$i<=$bins;$i++)
{
        $tot[$i]=0;
}
#$total++;

$step=($max-$min)/$bins;
$totdat=0;
$totdat2=0;

open(IN_file,$filename) or die ("can't open $filename\n");
while (($line = <IN_file>)) {
        chomp ($line);
    if ($line !~ /#/)
    {
        @data = split(' ', $line);
        $dat=$data[$param-1];
	$totdat += $dat;
	$totdat2 += $dat*$dat;
        $index=int(($dat-$min)/$step);
        if($index<0)
        {
                $index=0;
        }
        if($index>$bins)
        {
                $index=$bins;
        }

        $tot[$index]++;        
        $total++;
     }
}

$average = $totdat/$total;
$std = sqrt(($totdat2-$average*$average)/($average*$average));
print "#average= $average\t#std= $std\n";
$cumul=0;

printf "#bin\t range\ttotbin\tdist\tcum\n";
for($i=0;$i<=$bins;$i++)
{
        $range=$min+$i*$step;
	$cumul=$cumul + $tot[$i]/$total;
        printf "$i\t %.3f\t$tot[$i]\t%5.3f\t%5.3f\n",$range,$tot[$i]*100/$total, $cumul;
#        printf "$i $range $tot[$i] $tot[$i]*100/$total  $cumul\n";
}
 
