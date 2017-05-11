This directory holds miscellaneous tools to run performance-queries on mininet.

Sample queries are located in custom/per_flow_query and custom/per_packet_query, respectively.
 - The per_packet_query computes the queue length (at enqueue time) for every packet that passes through the switch and headed
   for the IP address for the h2 host in mininet. It is not a pure output of the Marple compiler:
    - The IP address for h2 is manually hardcoded
    - The query is instrumented with 3 special registers. These registers are read out in their entirety every 2 seconds,
       as a way to capture metadata that would otherwise be sent out on each packet.
       - `qlens`: stores the queue length (at enqueue time) for each packet.
       - `times`: stores the enqueue timestamp for each packet.
       - `idx`: stores the next index to write to for `qlens` and `times`. The registers have size 10000 and wrap around once full.
 - The per_flow_query computes aggregate stats for all flows passing through the switch. It computes total packets, number of flowlets, and the total time the flowlets were active.
   From these, we can get the average packet number and elapsed time per "burst".
   
 To run:
```
> sudo marple.py --pcap-dump=True --behavioral-exe=$BMV2/targets/simple_switch/simple_switch --json=$JSON --num-hosts=3
```
 Once the net is up, in a separate terminal, run the following to set the egress queue's rate limit (to 1000) and populate the forwarding tables (for 3 hosts):
```
> ./setup_tables 3
```
Then run the sequence of commands to start the fake HTTP client and UDP flooder.
Note: this requires sourdough to be installed. It is already installed if using the Amazon snapshot.
```
mininet> h1 $sourdough/examples/tcpserver $port1 &
mininet> h2 $sourdough/datagrump/receiver $port2 &
mininet> h3 $sourdough/datagrump/sender h2 $port2 &
mininet> h2 $sourdough/examples/tcpclient h1 $port1
```
The last command will print out the times for each subsequent "GET" request. Copy this output after completing the instructions below. 
The following instructions depend on which query you're running:

1. __Per_packet_query__: You have to collect snapshots of the 3 registers mentioned above. In a separate terminal, run:
  ```
  > ./record_register_continuous.sh 10000 qlens times
  ```
  This takes a snapshot of the registers every 2 seconds. The overhead seems pretty negligible but hasn't been robustly tested.
  The snapshots are stored in `register_values/`. Kill this script after you have a sufficient number of snapshots, kill the processes on the mininet hosts, and then quit out of mininet.
  Then run:
  ```
  > python parse_register_values.py > parsed_registers.txt
  ```
  This script will read the results of all your snapshots (assuming they start at 0 and increase by 1) and write out a list of (time, queue length)
  pairs, sorted by queue length. This is enough to feed into gnuplot or whatever other graphing tool you want.

1. __Per_flow_query__: Nothing needs to be done while the tcpclient is running. Simply run it for as long as you want, and kill
   it when you're done:
   ```
   mininet> h1 killall tcpserver
   mininet> h2 killall receiver
   ```
   Do NOT quit out of mininet. You need the switch to be running for the next part.
   
   Next, read the contents of all the registers you care about (from the last stage in your query). This will require you to
   dig around in the P4 to figure out which registers you care about. For the checked-in query, run the following:
   ```
   > record_register.sh 1024 regK_result_f0
   > record_register.sh 1024 regK_result_f1
   > record_register.sh 1024 regK_result_f2
   > record_register.sh 1024 regK_result_f3
   > record_register.sh 1024 regK_result_f4
   > record_register.sh 1024 regK_result_f5
   > record_register.sh 1024 regV_result_total_time
   > record_register.sh 1024 regV_result_total_size
   > record_register.sh 1024 regV_result_num_bursts
   ```
   The outputs are populated in the `results` folder in a file matching the register name. Note that 1024 is the size of the register.
   To consolidate these raw results into meaningful output, run:
   ```
   python interpret_register_results.py > interpreted_results.txt
   ```
   This groups all registers by index, and presents the ones that have meaningful values.
