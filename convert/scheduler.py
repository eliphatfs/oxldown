import os
import pickle
import random
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    assert 0 == os.system(f"rclone --config rclone.conf copy haosus3:objaverse-xl/meta/groups.pkl .nk8s/")
    with open(".nk8s/groups.pkl", "rb") as fi:
        groups: dict = pickle.load(fi)

    work = list(groups.items())
    random.shuffle(work)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
