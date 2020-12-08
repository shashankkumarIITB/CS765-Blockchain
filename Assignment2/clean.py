import os, shutil

# Remove the contents of the database and logfile directories
if os.path.exists('./databases'):
	shutil.rmtree('./databases/') 
if os.path.exists('./logfiles'):
	shutil.rmtree('./logfiles/') 
if os.path.exists('./plots'):
	shutil.rmtree('./plots/') 

# Initialize empty directories
os.mkdir('./databases/')
os.mkdir('./logfiles/')
os.mkdir('./plots/')

