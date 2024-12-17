#!/usr/bin/env python3

from bitarray import bitarray

class BloomFilter:
    def __init__(self, size, hash_count):
        """
        Initializes a Bloom Filter.

        Args:
            size: The size of the bit array.
            hash_count: The number of hash functions to use.
        """
        self.size = size
        self.hash_count = hash_count
        self.bits = bitarray(size)
        self.bits.setall(0)

    def add(self, item):
        """
        Adds an item to the Bloom Filter.

        Args:
            item: The item to add.
        """
        for i in range(self.hash_count):
            hash_value = hash(str(item) + str(i)) % self.size
            self.bits[hash_value] = 1

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
            if not self.bits[hash_value]:
                return False
        return True

# Example usage for Brainflayer
def generate_bloom_filter_for_brainflayer(brainflayer_data, size, hash_count):
    """
    Generates a Bloom Filter for Brainflayer data.

    Args:
        brainflayer_data: A list of Brainflayer data points.
        size: The size of the bit array.
        hash_count: The number of hash functions to use.

    Returns:
        A Bloom Filter object.
    """
    bloom_filter = BloomFilter(size, hash_count)
    for data_point in brainflayer_data:
        bloom_filter.add(data_point)
    return bloom_filter

# Example usage:
# Assuming brainflayer_data is a list of your Brainflayer data points
bloom_filter = generate_bloom_filter_for_brainflayer(brainflayer_data, 1000000, 5) 

# Check if a data point might be in the Bloom Filter
data_point_to_check = "your_data_point"
if bloom_filter.check(data_point_to_check):
    print("Data point might be in the Bloom Filter.")
else:
    print("Data point is definitely not in the Bloom Filter.") 
