import os
import sys
proj_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(proj_root)
import toychain


resource_dir = os.path.join(proj_root, 'test/resource')
