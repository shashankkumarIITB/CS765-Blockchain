import csv, os
from matplotlib import pyplot as plt

flooding = ['10', '20', '30']
interarrival_times = ['2', '10', '20', '30', '40', '50', '60']

# Port on which the adversary is mining
port_adversary = '5000'

# Directory structure
# 10 -> databases_10_<time_interarrival> -> database_<port>.txt
# 20 -> databases_20_<time_interarrival> -> database_<port>.txt
# 30 -> databases_30_<time_interarrival> -> database_<port>.txt
# Iterate over all the possible directories
for f in flooding:
	# Mining power utlization (MPU) = # blocks in longest chain / # blocks in blockchain including forks
	MPU = []
	# Fraction of the main chain mined by the adversary
	Fraction = []
	# Iterate over all the interarrival times for this flooding
	for t in interarrival_times:
		directory_path = f'./{f}/databases_{f}_{t}'
		# Fetch all the files in the directory
		# files = [os.path.join(directory_path, file) for file in os.listdir(directory_path)]
		files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))]
		# Mining power utilization for a particular node
		mpu = 0
		# Fracion of blocks mined by adversary as per a particular node
		fraction = 0
		for file in files:
			num_longest, num_blockchain, num_adversary = 1, 1, 0
			with open(file) as csvfile:
				reader = csv.DictReader(csvfile)
				for row in reader:
					num_blockchain += 1
					index = float(row['index'])
					if num_longest < index:
						num_longest = index
					if row['port'] == port_adversary:
						num_adversary += 1
			mpu += num_longest / num_blockchain
			fraction += num_adversary / num_blockchain
		# MPU entire network = average MPU per node in the network
		MPU.append(mpu / len(files)) 
		Fraction.append(fraction / len(files))

	# Plot for MPU for different values of interarrival times at a given flooding
	plt.ylabel(f'Mining Power Utilization')
	plt.xlabel('Interarrival Times')
	line, = plt.plot(interarrival_times, MPU, 'r')
	line.set_label(f'{f}% flooding')
	plt.legend()
	plt.title(f'MPU vs Interarrival times for {f}% flooding')
	plt.savefig(f'plots/MPU_{f}.png')
	plt.close()

	# Plot for fraction of blocks mined by adversary for different values of interarrival times at a given flooding
	plt.ylabel(f'Fraction of blocks mined by adversary')
	plt.xlabel('Interarrival Times')
	line, = plt.plot(interarrival_times, Fraction)
	line.set_label(f'{f}% flooding')
	plt.legend()
	plt.title(f'Fraction (adversary) vs Interarrival times for {f}% flooding')
	plt.savefig(f'plots/FractionAdversary_{f}.png')
	plt.close()