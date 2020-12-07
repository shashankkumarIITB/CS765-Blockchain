import os, shutil

# Remove the contents of the database and logfile directories
shutil.rmtree('./databases/') 
shutil.rmtree('./logfiles/') 

# Initialize empty directories
os.mkdir('./databases/')
os.mkdir('./logfiles/')

