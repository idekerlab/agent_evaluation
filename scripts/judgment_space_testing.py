import sys
import os
import json
import numpy as np

# Add the parent directory of the current script to the Python path
cwd = os.getcwd()
dirname = os.path.dirname(cwd)
print(f'adding current directory to path: {cwd}')
sys.path.append(cwd)
print(f'adding parent to path: {dirname}')
sys.path.append(dirname)
print(f'Python path: {sys.path}')
print(sys.path)

