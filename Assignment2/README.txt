-------------------------------------------------------------------------------
To run the experiments, run the following scripts in three separate windows:
-------------------------------------------------------------------------------
python3 seed.py
python3 network.py
python3 adversary.py

-------------------------------------------------------------------------------
To clean database and logfile directories, use the following script:
-------------------------------------------------------------------------------
python3 clean.py

-------------------------------------------------------------------------------
Steps:
-------------------------------------------------------------------------------
1. Vary the interarrival time in the files network.py and adversary.py
2. Use the following values of interarrival times:
	[2, 10, 20, 30, 40, 50, 60]
3. After each run rename the logfiles and databases directories to logfiles_<interarrival time> and databases_<interarrival time>
4. Run the clean step after this to intialize empty databases and logfiles directories

-------------------------------------------------------------------------------
Mahesh Lomror - 10% flooding configuration
Krishna Yadav - 20% and 30% flooding configuration
To change the flooding configuration, refer to adversary.py