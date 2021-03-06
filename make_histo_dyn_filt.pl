#!/usr/bin/perl
# Create an histogram from a columnar file
# 
# it is possible to combine colums to filter rows
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
    printf("Usage: make_histo.pl <file> <expr> <filter> <min> <max> <bins>\n");
    printf("       file can be - to read from stdin\n");
    printf("       <expr> and <filter> are perl expressions \n");
    printf("       involving the @d variable. \n");
    printf("       e.g., expr = @d[0]/@d[1] and filter=@d[0]>0 \n");
    
    exit(1);
}


$filename=$ARGV[0];
$command=$ARGV[1];
$filter=$ARGV[2];
$min=$ARGV[3];
$max=$ARGV[4];
$bins=$ARGV[5];

print "#making histogram $filename $command $filter $min $max $bins\n";
#for($i=0;$i<=$bins;$i++)
#{
#        $tot[$i]=0;
#}
#$total++;

$step=($max-$min)/$bins;
$totdat=0;

for($i=0;$i<=$bins;$i++)
{
   $tot[$i] = 0;
}
open(IN_file,$filename) or die ("can't open $filename\n");
while (($line = <IN_file>)) {
#        chomp ($line);
        @d = split(' ', $line);
        if(eval($filter))
        {
           $dat=eval($command);
	   $totdat += $dat;
           $index=int(($dat-$min)/$step);
           if($index<0)
           {
                   $index=0;
           } else {
              if($index>$bins)
              {
                      $index=$bins;
              }
           }

           $tot[$index]++;        
           $total++;
        }
}

$average = $totdat/$total;
print "#samples = $total; #sum = $totdat; #average= $average\n";
$cumul=0;

printf "#bin\t range\ttotbin\tdist\tcum\n";
for($i=0;$i<=$bins;$i++)
{
        $range=$min+$i*$step;
	$cumul=$cumul + $tot[$i]/$total;
        printf "$i\t %.5f\t$tot[$i]\t%.5f\t%.5f\n",$range,$tot[$i]*100/$total, $cumul;
#        printf "$i $range $tot[$i] $tot[$i]*100/$total  $cumul\n";
}
 
