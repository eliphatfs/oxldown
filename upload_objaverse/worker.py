import os
import sys
import time
import shutil
import kubetk.arch.worker as wk



def read(x):
    shutil.copyfile(x, os.path.basename(x))


def write(local):
    try:
        for i in range(5):
            ret = os.system(f"rclone --config rclone.conf copy {local} haosus3:objaverse-xl/data/objaverse/")
            if ret == 0:
                break
            time.sleep(i + 1)
        else:
            assert ret == 0, "rclone error %d" % ret
    finally:
        os.remove(local)


if __name__ == '__main__':
    ip = sys.argv[-1]
    wk.run_pipelined_worker(f"http://{ip}:9105", [
        (read, 2),
        (write, 2)
    ])
