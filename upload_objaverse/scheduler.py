import kubetk.arch.scheduler as sc
from kubetk.helpers.parallel_walk import parallel_walk


work = []


def callback(p: str):
    if p.endswith(".glb"):
        work.append(p)


if __name__ == '__main__':
    parallel_walk(["/datasets-slow1/Objaverse/rawdata/hf-objaverse-v1/glbs/"], callback)
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work, backoff=3))
