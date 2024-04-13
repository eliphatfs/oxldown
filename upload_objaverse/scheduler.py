import os
import kubetk.arch.scheduler as sc
from kubetk.helpers.parallel_walk import parallel_walk


work = []
done = set()


def callback(p: str):
    if p.endswith(".glb") and os.path.basename(p) not in done:
        work.append(p)


if __name__ == '__main__':
    with open("/datasets-slow1/done.txt") as fi:
        for line in fi:
            if line:
                done.add(line.strip().split(maxsplit=1)[1])
    parallel_walk(["/datasets-slow1/Objaverse/rawdata/hf-objaverse-v1/glbs/"], callback)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work, backoff=3))
