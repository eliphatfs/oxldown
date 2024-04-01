import os
import json
import random
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    assert 0 == os.system(f"rclone --config rclone.conf copy haosus3:objaverse-xl/meta/all_id_list.json .")
    with open("all_id_list.json") as fi:
        work = json.load(fi)
    # work = [work[220000], work[0], work[-1]]
    random.shuffle(work)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
