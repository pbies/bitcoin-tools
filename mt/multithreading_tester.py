#!/usr/bin/env python3

import threading
import time
import queue
import concurrent.futures
import random
import math
from datetime import datetime
import json
import os

class MultithreadingTester:
	def __init__(self):
		self.results = []
		self.lock = threading.Lock()
		
	def worker_basic(self, worker_id, data_chunk, result_dict):
		"""Basic worker function that processes data"""
		start_time = time.time()
		
		# Simulate some CPU-intensive work
		processed_data = []
		for item in data_chunk:
			# Simulate processing: calculate factorial and square root
			result = math.factorial(min(item, 10))  # Limit factorial to avoid huge numbers
			sqrt_result = math.sqrt(abs(item))
			processed_data.append((item, result, sqrt_result))
		
		end_time = time.time()
		processing_time = end_time - start_time
		
		with self.lock:
			result_dict[worker_id] = {
				'items_processed': len(processed_data),
				'processing_time': processing_time,
				'data': processed_data[:3]  # Store first 3 results as sample
			}
		
		return len(processed_data), processing_time
	
	def worker_io_bound(self, worker_id, urls_to_simulate, result_dict):
		"""Simulate IO-bound work (like network requests)"""
		start_time = time.time()
		
		processed_urls = []
		for url in urls_to_simulate:
			# Simulate network latency
			time.sleep(random.uniform(0.01, 0.1))
			
			# Simulate processing the response
			response_size = random.randint(100, 5000)
			processed_urls.append((url, response_size))
		
		end_time = time.time()
		processing_time = end_time - start_time
		
		with self.lock:
			result_dict[worker_id] = {
				'urls_processed': len(processed_urls),
				'processing_time': processing_time,
				'sample_data': processed_urls[:2]
			}
		
		return len(processed_urls), processing_time
	
	def test_basic_threading(self, data_size=1000, num_threads=4):
		"""Test basic threading.Thread approach"""
		print(f"\n=== Testing Basic Threading (Data: {data_size}, Threads: {num_threads}) ===")
		
		# Generate test data
		data = list(range(1, data_size + 1))
		chunk_size = len(data) // num_threads
		chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
		
		threads = []
		results = {}
		start_time = time.time()
		
		# Create and start threads
		for i, chunk in enumerate(chunks):
			thread = threading.Thread(
				target=self.worker_basic,
				args=(f"thread_{i}", chunk, results)
			)
			threads.append(thread)
			thread.start()
		
		# Wait for all threads to complete
		for thread in threads:
			thread.join()
		
		total_time = time.time() - start_time
		
		# Calculate metrics
		total_items = sum(result['items_processed'] for result in results.values())
		avg_time = sum(result['processing_time'] for result in results.values()) / len(results)
		
		result_info = {
			'test_name': 'Basic Threading',
			'data_size': data_size,
			'num_threads': num_threads,
			'total_time': total_time,
			'total_items_processed': total_items,
			'avg_thread_time': avg_time,
			'efficiency': total_items / total_time if total_time > 0 else 0,
			'thread_results': results
		}
		
		self.results.append(result_info)
		return result_info
	
	def test_thread_pool_executor(self, data_size=1000, num_threads=4):
		"""Test ThreadPoolExecutor approach"""
		print(f"\n=== Testing ThreadPoolExecutor (Data: {data_size}, Threads: {num_threads}) ===")
		
		# Generate test data
		data = list(range(1, data_size + 1))
		chunk_size = len(data) // num_threads
		chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
		
		results = {}
		start_time = time.time()
		
		with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
			# Submit tasks
			future_to_chunk = {
				executor.submit(self.worker_basic, f"thread_{i}", chunk, results): chunk 
				for i, chunk in enumerate(chunks)
			}
			
			# Wait for all tasks to complete
			concurrent.futures.wait(future_to_chunk.keys())
		
		total_time = time.time() - start_time
		
		# Calculate metrics
		total_items = sum(result['items_processed'] for result in results.values())
		avg_time = sum(result['processing_time'] for result in results.values()) / len(results)
		
		result_info = {
			'test_name': 'ThreadPoolExecutor',
			'data_size': data_size,
			'num_threads': num_threads,
			'total_time': total_time,
			'total_items_processed': total_items,
			'avg_thread_time': avg_time,
			'efficiency': total_items / total_time if total_time > 0 else 0,
			'thread_results': results
		}
		
		self.results.append(result_info)
		return result_info
	
	def test_producer_consumer_pattern(self, num_producers=2, num_consumers=3, items_per_producer=100):
		"""Test producer-consumer pattern using Queue"""
		print(f"\n=== Testing Producer-Consumer (Producers: {num_producers}, Consumers: {num_consumers}) ===")
		
		work_queue = queue.Queue()
		results_queue = queue.Queue()
		stop_event = threading.Event()
		
		def producer(producer_id):
			"""Produce work items"""
			items_produced = 0
			for i in range(items_per_producer):
				work_item = f"item_{producer_id}_{i}"
				work_queue.put(work_item)
				items_produced += 1
				# Simulate variable production time
				time.sleep(random.uniform(0.001, 0.01))
			
			results_queue.put(('producer', producer_id, items_produced))
		
		def consumer(consumer_id):
			"""Consume work items"""
			items_processed = 0
			while not stop_event.is_set() or not work_queue.empty():
				try:
					work_item = work_queue.get(timeout=0.1)
					# Simulate processing time
					time.sleep(random.uniform(0.005, 0.02))
					items_processed += 1
					work_queue.task_done()
				except queue.Empty:
					continue
			
			results_queue.put(('consumer', consumer_id, items_processed))
		
		start_time = time.time()
		
		# Start producers
		producer_threads = []
		for i in range(num_producers):
			thread = threading.Thread(target=producer, args=(i,))
			producer_threads.append(thread)
			thread.start()
		
		# Start consumers
		consumer_threads = []
		for i in range(num_consumers):
			thread = threading.Thread(target=consumer, args=(i,))
			consumer_threads.append(thread)
			thread.start()
		
		# Wait for all producers to finish
		for thread in producer_threads:
			thread.join()
		
		# Signal consumers to stop
		stop_event.set()
		
		# Wait for all consumers to finish
		for thread in consumer_threads:
			thread.join()
		
		total_time = time.time() - start_time
		
		# Collect results
		producer_results = []
		consumer_results = []
		while not results_queue.empty():
			result_type, worker_id, count = results_queue.get()
			if result_type == 'producer':
				producer_results.append(count)
			else:
				consumer_results.append(count)
		
		total_produced = sum(producer_results)
		total_consumed = sum(consumer_results)
		
		result_info = {
			'test_name': 'Producer-Consumer Pattern',
			'num_producers': num_producers,
			'num_consumers': num_consumers,
			'items_per_producer': items_per_producer,
			'total_time': total_time,
			'total_items_produced': total_produced,
			'total_items_consumed': total_consumed,
			'efficiency': total_consumed / total_time if total_time > 0 else 0,
			'producer_counts': producer_results,
			'consumer_counts': consumer_results
		}
		
		self.results.append(result_info)
		return result_info
	
	def test_io_bound_workload(self, num_tasks=50, num_threads=5):
		"""Test IO-bound workload simulation"""
		print(f"\n=== Testing IO-bound Workload (Tasks: {num_tasks}, Threads: {num_threads}) ===")
		
		# Generate simulated URLs
		urls = [f"http://example.com/resource/{i}" for i in range(num_tasks)]
		chunk_size = len(urls) // num_threads
		chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
		
		results = {}
		start_time = time.time()
		
		with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
			# Submit tasks
			future_to_chunk = {
				executor.submit(self.worker_io_bound, f"thread_{i}", chunk, results): chunk 
				for i, chunk in enumerate(chunks)
			}
			
			# Wait for all tasks to complete
			concurrent.futures.wait(future_to_chunk.keys())
		
		total_time = time.time() - start_time
		
		# Calculate metrics
		total_urls = sum(result['urls_processed'] for result in results.values())
		avg_time = sum(result['processing_time'] for result in results.values()) / len(results)
		
		result_info = {
			'test_name': 'IO-bound Workload',
			'num_tasks': num_tasks,
			'num_threads': num_threads,
			'total_time': total_time,
			'total_urls_processed': total_urls,
			'avg_thread_time': avg_time,
			'efficiency': total_urls / total_time if total_time > 0 else 0,
			'thread_results': results
		}
		
		self.results.append(result_info)
		return result_info
	
	def generate_report(self):
		"""Generate a comprehensive report of all tests"""
		print("\n" + "="*80)
		print("MULTITHREADING PERFORMANCE REPORT")
		print("="*80)
		
		# Overall statistics
		total_tests = len(self.results)
		total_processing_time = sum(result['total_time'] for result in self.results)
		total_items_processed = sum(result.get('total_items_processed', 0) + 
								  result.get('total_items_consumed', 0) for result in self.results)
		
		print(f"\nOverall Statistics:")
		print(f"  Total Tests Run: {total_tests}")
		print(f"  Total Processing Time: {total_processing_time:.4f} seconds")
		print(f"  Total Items Processed: {total_items_processed}")
		print(f"  Overall Efficiency: {total_items_processed/total_processing_time:.2f} items/sec")
		
		# Detailed test results
		print(f"\nDetailed Test Results:")
		print("-" * 100)
		print(f"{'Test Name':<25} {'Data Size':<12} {'Threads':<8} {'Time (s)':<10} {'Items':<12} {'Efficiency':<12}")
		print("-" * 100)
		
		for result in self.results:
			test_name = result['test_name']
			data_size = result.get('data_size', result.get('num_tasks', result.get('items_per_producer', 0)))
			num_threads = result.get('num_threads', result.get('num_producers', 0) + result.get('num_consumers', 0))
			total_time = result['total_time']
			items_processed = result.get('total_items_processed', result.get('total_items_consumed', 0))
			efficiency = result['efficiency']
			
			print(f"{test_name:<25} {data_size:<12} {num_threads:<8} {total_time:<10.4f} "
				  f"{items_processed:<12} {efficiency:<12.2f}")
		
		# Performance comparison
		print(f"\nPerformance Comparison:")
		print("-" * 60)
		best_efficiency = max(self.results, key=lambda x: x['efficiency'])
		fastest_test = min(self.results, key=lambda x: x['total_time'])
		
		print(f"Most Efficient: {best_efficiency['test_name']} "
			  f"(Efficiency: {best_efficiency['efficiency']:.2f} items/sec)")
		print(f"Fastest Execution: {fastest_test['test_name']} "
			  f"(Time: {fastest_test['total_time']:.4f} seconds)")
		
		# Save detailed results to file
		self.save_detailed_report()
	
	def save_detailed_report(self):
		"""Save detailed results to JSON file"""
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"multithreading_report_{timestamp}.json"
		
		report_data = {
			'timestamp': datetime.now().isoformat(),
			'test_results': self.results,
			'summary': {
				'total_tests': len(self.results),
				'total_processing_time': sum(result['total_time'] for result in self.results),
				'total_items_processed': sum(result.get('total_items_processed', 0) + 
										   result.get('total_items_consumed', 0) for result in self.results)
			}
		}
		
		with open(filename, 'w') as f:
			json.dump(report_data, f, indent=2)
		
		print(f"\nDetailed report saved to: {filename}")

def main():
	"""Main function to run all multithreading tests"""
	tester = MultithreadingTester()
	
	print("Starting Multithreading Performance Tests...")
	print("This may take a few moments...")
	
	# Test 1: Basic threading with different configurations
	tester.test_basic_threading(data_size=1000, num_threads=2)
	tester.test_basic_threading(data_size=1000, num_threads=4)
	tester.test_basic_threading(data_size=2000, num_threads=4)
	
	# Test 2: ThreadPoolExecutor
	tester.test_thread_pool_executor(data_size=1000, num_threads=2)
	tester.test_thread_pool_executor(data_size=1000, num_threads=4)
	
	# Test 3: Producer-Consumer Pattern
	tester.test_producer_consumer_pattern(num_producers=2, num_consumers=3, items_per_producer=50)
	tester.test_producer_consumer_pattern(num_producers=3, num_consumers=5, items_per_producer=30)
	
	# Test 4: IO-bound workload
	tester.test_io_bound_workload(num_tasks=50, num_threads=5)
	tester.test_io_bound_workload(num_tasks=100, num_threads=10)
	
	# Generate comprehensive report
	tester.generate_report()

if __name__ == "__main__":
	main()
