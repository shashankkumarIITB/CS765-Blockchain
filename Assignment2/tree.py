# Returns the latex string to generate the blockchain tree
import csv
from miner import GENESIS_BLOCK

# Files to read
files = ['database_3000.txt']

# X-coordinate of the figure
x_coordinate = 10
# Dictionary to map hash to node number i.e. count
hash_dict = {GENESIS_BLOCK['hash']: 0}
# Set of nodes
nodes = f'\\node (n0) at ({x_coordinate}, -10) {{1}}; \n'
# Set of edges
edges = ''
for file in files:
	with open(file) as csvfile:
		count = 1
		reader = csv.DictReader(csvfile)
		parent_hash = GENESIS_BLOCK['hash']
		for row in reader:
			# Maximum number of nodes in a graph permitted in latex is around 279
			if count > 250:
				break
			hash_dict[row['hash']] = count
			if row['hash_prev'] != parent_hash:
				nodes += f'\\node (n{count}) at ({x_coordinate + 10}, {count*-2 - 10}) {{{row["index"]}}}; \n'
			else:
				parent_hash = row['hash']
				nodes += f'\\node (n{count}) at ({x_coordinate}, {count*-2 - 10}) {{{row["index"]}}}; \n'
			edges += f'n{hash_dict[row["hash_prev"]]}/n{count},'
			count += 1

# Generate the latex script
tikz = f'\\documentclass{{article}} \n\\usepackage[paperwidth=21cm,paperheight=500cm,margin=1in]{{geometry}} \n\\usepackage{{tikz}} \n\\begin{{document}} \n\\begin{{tikzpicture}} \n[scale=.8,auto=left,every node/.style={{circle,fill=blue!20}}] \n'
tikz += nodes
tikz += f'\\foreach \\from/\\to in {{{edges[:-1]}}} \n\\draw (\\from) -- (\\to); \n'
tikz += f'\\end{{tikzpicture}} \n\\end{{document}}' 

# Write the string to file 'tree.tex'
with open('tree.tex', 'w+') as file:
	file.write(tikz)