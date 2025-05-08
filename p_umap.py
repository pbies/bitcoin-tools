from p_tqdm import p_umap

def add(a, b):
	return a + b

added = p_umap(add, ['1', '2', '3'], ['a', 'b', 'c'])
# added is an array with '1a', '2b', '3c' in any order

# num_cpus
