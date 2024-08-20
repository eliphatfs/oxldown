import os
import json
import random
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    # assert 0 == os.system(f"rclone --config rclone.conf copy haosus3:objaverse-xl/meta/u5s_glb.json .nk8s/")
    with open(".nk8s/u5s_delta.json", "r") as fi:
        work: list = json.load(fi)

    random.shuffle(work)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
