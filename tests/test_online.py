"""Host one world in a subprocess, join it from another, check both sides."""

import os
import subprocess
import sys
import time

TESTS = os.path.dirname(os.path.abspath(__file__))

host = subprocess.Popen([sys.executable, os.path.join(TESTS, "online_host.py")],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    ready = False
    deadline = time.time() + 20
    while time.time() < deadline:
        line = host.stdout.readline()
        if not line:
            break
        if "HOST READY" in line:
            ready = True
            break
    assert ready, "host failed to start"
    time.sleep(1.0)
    client = subprocess.run([sys.executable, os.path.join(TESTS, "online_client.py")],
                            capture_output=True, text=True, timeout=120)
    print(client.stdout)
    print(client.stderr, file=sys.stderr)
    assert "online OK" in client.stdout, "client checks failed"
finally:
    host.kill()
print("online e2e OK")
