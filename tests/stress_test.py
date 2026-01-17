import concurrent.futures
import time
import requests
import random
import multiprocessing

# Configuration
API_URL = "http://localhost:8000/search"
CONCURRENT_REQUESTS = 50
DIMENSION = 1536

def send_request(req_id):
    query = [random.random() for _ in range(DIMENSION)]
    payload = {"query": query, "k": 5}
    
    start = time.time()
    try:
        resp = requests.post(API_URL, json=payload)
        resp.raise_for_status()
        latency = time.time() - start
        return latency
    except Exception as e:
        print(f"Req {req_id} failed: {e}")
        return None

def run_stress_test():
    print(f"Starting Stress Test with {CONCURRENT_REQUESTS} concurrent requests...")
    print(f"Target: {API_URL}")
    
    start_total = time.time()
    latencies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(send_request, i) for i in range(CONCURRENT_REQUESTS)]
        
        for future in concurrent.futures.as_completed(futures):
            lat = future.result()
            if lat is not None:
                latencies.append(lat)
                
    total_time = time.time() - start_total
    
    if not latencies:
        print("All requests failed. Is server running?")
        return

    avg_latency = sum(latencies) / len(latencies)
    throughput = len(latencies) / total_time
    
    print("\n--- Results ---")
    print(f"Total Requests: {len(latencies)}")
    print(f"Total Time:     {total_time:.4f}s")
    print(f"Avg Latency:    {avg_latency:.4f}s")
    print(f"Throughput:     {throughput:.2f} req/s")
    
    # Analysis
    # If GIL was blocking, Total Time ~= Sum(Latencies)
    # If Parallel, Total Time << Sum(Latencies)
    
    sum_latencies = sum(latencies)
    print(f"\nSum of Latencies: {sum_latencies:.4f}s")
    print(f"Concurrency Factor: {sum_latencies / total_time:.2f}x")
    
    cpu_count = multiprocessing.cpu_count()
    print(f"Theoretical Max Concurrency (Physical Cores): {cpu_count}")

    if (sum_latencies / total_time) > 1.5:
        print("\n✅ PASS: System demonstrates concurrent processing (Factor > 1.5x)")
    else:
        print("\n⚠️ WARNING: Concurrency low. Check if GIL release is working or if tasks are too small.")

if __name__ == "__main__":
    run_stress_test()
