#!/usr/bin/env python
import subprocess
import sys

# Run uvicorn
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'main:app',
    '--reload',
    '--host', '0.0.0.0',
    '--port', '8000'
])
