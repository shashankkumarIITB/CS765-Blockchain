-------------------------------------------------------------------------------
TEAM:
-------------------------------------------------------------------------------
Shashank Kumar (170050031)
Mahesh Lomror (170050050)
Krishna Yadav (170050032)
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
RUN:
-------------------------------------------------------------------------------
To run the experiments, run the following scripts in three separate terminal windows:
	python3 seed.py -- To create a seed instance
	python3 network.py -- To establish a network of 10 peers and interconnect them
	python3 adversary.py -- To run the adversary

To clean databases, logfiles and plots, use the following script:
	python3 clean.py

-------------------------------------------------------------------------------
FAQs:
-------------------------------------------------------------------------------
** The code has been extensively commented. So, we don't think there is a need to repeat the same here.

** To change the flooding configuration, refer to adversary.py.

** Vary the interarrival time in the files network.py and adversary.py.

** The following values of interarrival times have been used:
	[2, 10, 20, 30, 40, 50, 60]

** After each run rename the logfiles and databases directories to logfiles_<interarrival time> and databases_<interarrival time>

** Run the clean step after each run to intialize empty database, logfile and plot directories.

** To generate the plots, run the following script. The plots will be saved in plots directory.
	python3 plot.py 

** To generate the blockchain tree, run the below script. This will create a file tree.tex with the latex code to be compiled on overleaf.
	python3 tree.py

** Instead of using databases to save the blockchain, we have stored it in text files. This makes the code run faster owing to the fact 
	that it is a threading intensive assignment.

** Use databases_10_2.txt to visualize the blockchain tree since it contains a couple of forks.

-------------------------------------------------------------------------------
How the nodes determine the longest chain?
-------------------------------------------------------------------------------
Apart from saving the database information in text files, the nodes also maintain a local dictionary to store blocks. 
Each data block in this dictionary contains the following information:
1. Block corresponding to the blockchain
2. Hash of the block
3. Length at which the block was received
4. Host and port number of the machine that created the block 
When the node is supposed to create a new block, it loops over the dictionary to find the data block with the maximum length. It then 
creates a block using this block as the parent block. In case of ties, the block that came first in the dictionary is preferred.
