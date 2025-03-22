#!/usr/bin/env python3

class BloomFilter:
	def __init__(self, size, hash_count):
		"""
		Initializes a Bloom Filter with the given size and number of hash functions.

		Args:
			size: The size of the bit array.
			hash_count: The number of hash functions to use.
		"""
		self.size = size
		self.hash_count = hash_count
		self.bit_array = [0] * size

	def add(self, item):
		"""
		Adds an item to the Bloom Filter.

		Args:
			item: The item to add.
		"""
		for i in range(self.hash_count):
			hash_value = hash(str(item) + str(i)) % self.size
			self.bit_array[hash_value] = 1

	def check(self, item):
		"""
		Checks if an item might be in the Bloom Filter.

		Args:
			item: The item to check.

		Returns:
			True if the item might be in the Bloom Filter, False otherwise.
		"""
		for i in range(self.hash_count):
			hash_value = hash(str(item) + str(i)) % self.size
			if self.bit_array[hash_value] == 0:
				return False
		return True

# Example usage:
bloom_filter = BloomFilter(1000, 5)  # Create a Bloom Filter with size 1000 and 5 hash functions

# Add some items
bloom_filter.add("apple")
bloom_filter.add("banana")
bloom_filter.add("cherry")

# Check if items might be in the Bloom Filter
print(bloom_filter.check("apple"))  # Output: True
print(bloom_filter.check("banana"))  # Output: True
print(bloom_filter.check("cherry"))  # Output: True
print(bloom_filter.check("orange"))  # Output: False (might be a false positive)

# Check for potential false positives
print(bloom_filter.check("apricot"))  # Might return True even if "apricot" was not added
