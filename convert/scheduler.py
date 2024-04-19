import os
import json
import tqdm
import pickle
import random
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    assert 0 == os.system(f"rclone --config rclone.conf copy haosus3:objaverse-xl/meta/groups.pkl .nk8s/")
    with open(".nk8s/groups.pkl", "rb") as fi:
        groups: dict = pickle.load(fi)

    work = [json.dumps(x) for x in tqdm.tqdm(groups.items())]
    del groups
    random.shuffle(work)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
