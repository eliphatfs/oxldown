import os
import json
import random
import subprocess
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    assert 0 == os.system(f"rclone --config rclone.conf copy haosus3:objaverse-xl/meta/all_id_list.json .")
    with open("all_id_list.json") as fi:
        work = json.load(fi)
    # work = [work[220000], work[0], work[-1]]
    donetxt = subprocess.check_output("rclone --config rclone.conf ls haosus3:objaverse-xl/data/thingiverse/".split()).decode().splitlines()
    done = set()
    for line in donetxt:
        if line:
            done.add(line.strip().split(maxsplit=1)[1])
    work = [w for w in work if w.startswith('thingi') and w.split(":")[-1] not in done]
    random.shuffle(work)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
