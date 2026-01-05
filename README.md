# CS451_M3_tools
These are some tools that I made to test more easily different scenarios a varying number of proposals and hosts, with a comparator to check that the outputs are coherent.  
Put those files in the corresponding directories as indicated.
# latticeConfigProducer.py: 
  takes x y a b c  
  x = number of config files  
  y = max number of integers per proposal line  
  a = number of proposal lines  
  b, c = vs, ds  
  Makes x config files where the first line is a b c and then for a lines chooses up to y integers selected randomly from [1, 2*x] to constitue a proposal 
# comparator.py: 
  takes x y  
  x: number of hosts  
  y: number of proposals  
  Checks pairwise whether all the logs that contain the decisions for each shot are coherent (checks that each host's decision in line i of all the outputs is included     one way or the other in the other line i decision of other hosts)
# gen-hosts.sh: 
  takes x (and generates x lines with <id> localhost <port>)  
  x: number of hosts
# la_run.sh: 
  doesn't take anything, fetches the hosts and finds their corresponding configs in order to ./run.sh with the right arguments 
