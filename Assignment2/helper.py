import random
import hashlib

# Returns a list of random integers in the range [begin, end] (both inclusive)
def getRandomList(begin, end, length):
	result = set()
	length = min(length, end - begin + 1)
	while len(result) < length:
		result.add(random.randint(begin, end))
	return list(result)

# Returns a hash of the string
def getHash(string):
	return hashlib.sha256(string.encode()).hexdigest()
	