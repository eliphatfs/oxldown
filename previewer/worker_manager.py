import os
import sys


if __name__ == '__main__':
    while 0 != os.system("python previewer/worker.py " + sys.argv[-1]):
        print("=" * 40)
