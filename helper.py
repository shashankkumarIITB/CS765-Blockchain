import random

# Returns a list of random integers in the range [begin, end] (both inclusive)
def GetRandomList(begin, end, length):
  result = set()
  while len(result) < length:
    result.add(random.randint(begin, end))
  return list(result)
