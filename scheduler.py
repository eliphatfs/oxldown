import objaverse.xl as oxl
import kubetk.arch.scheduler as sc


work = []


if __name__ == '__main__':
    anno = oxl.get_annotations()
    print("Sample:", work[:10])
    sc.serve_scheduler(sc.WorkQueue(work))
