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
STEPS:
1. Vary the interarrival time in the files network.py and adversary.py
2. Use the following values for now:
	[2, 10, 25, 50, 75, 100]
3. After each run rename the logfiles and databases directories to logfiles_<interarrival time> and databases_<interarrival time>
4. Run the clean step after this to intialize empty databases and logfiles directories