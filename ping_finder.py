from ping3 import ping
import socket
import struct
import concurrent.futures
import os

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def ping_ip(ip):
    response = ping(ip)
    if response is not None and response is not False:
        return f'{ip} is online'
    else:
        return f'{ip}'

start_ip = ip2int("192.168.0.1")
end_ip = ip2int("192.168.0.255")

results = []

with concurrent.futures.ThreadPoolExecutor(max_workers=255) as executor:
    future_to_ip = {executor.submit(ping_ip, int2ip(ip)): int2ip(ip) for ip in range(start_ip, end_ip + 1)}
    for future in concurrent.futures.as_completed(future_to_ip):
        ip = future_to_ip[future]
        try:
            data = future.result()
        except Exception as exc:
            data = f'{ip} generated an exception: {exc}'
        finally:
            print(data)
            results.append(data)

# Sort IP addresses
results.sort(key=lambda s: list(map(int, s.split()[0].split('.'))))

# Check if result.txt already exists and if so, write to result-2.txt instead
if os.path.exists('result.txt'):
    result_file = 'result-2.txt'
else:
    result_file = 'result.txt'

with open(result_file, 'w') as file:
    for result in results:
        file.write(result + '\n')

# If we wrote to result-2.txt, compare it with result.txt and write any differences to diff.txt
if result_file == 'result-2.txt':
    with open('result.txt', 'r') as f1, open('result-2.txt', 'r') as f2:
        old_results = f1.readlines()
        new_results = f2.readlines()

    diffs = []
    for old, new in zip(old_results, new_results):
        if len(old) != len(new):
            if len(new) > len(old):
                diffs.append(f'{new.strip().split()[0]} now online')
            else:
                diffs.append(f'{old.strip().split()[0]} now offline')

    if diffs:
        with open('diff.txt', 'w') as file:
            for diff in diffs:
                file.write(diff + '\n')
    else:
        print('No differences found.')
