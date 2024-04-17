import uuid
import tqdm
import pickle
import collections
import objaverse.xl as oxl


def main():
    anno = oxl.get_annotations()
    breakpoint()
    anno.reset_index()

    FID = 0
    SRC = 1
    LIC = 2
    FTY = 3
    SHA = 4
    META = 5

    done = set()
    with open('.nk8s/thingi.txt') as fi:
        for line in fi:
            if line:
                done.add(line.strip().split(maxsplit=1)[1])

    groups = collections.defaultdict(list)
    for row in tqdm.tqdm(anno.to_numpy()):
        src = row[SRC]
        fty = row[FTY]
        if src == 'github':
            spl = row[FID].split("/")
            org, repo, commit_hash = spl[3], spl[4], spl[6]
            down = f"data/github/{org}/{repo}/{commit_hash}"
            visit = "/".join(spl[7:])
        elif src == 'sketchfab':
            fid = row[FID].split("/")[-1]
            down = f"data/objaverse/{fid}.glb"
            visit = f"{fid}.glb"
        elif src == 'thingiverse':
            fid = row[FID].split("fileId=")[-1]
            if fid not in done:
                continue
            down = f"data/thingiverse/{fid}"
            visit = f"{fid}"
        elif src == 'smithsonian':
            namespace = uuid.NAMESPACE_DNS
            fid = str(uuid.uuid5(namespace, row[FID])) + '.glb'
            down = f"data/smithsonian/{fid}"
            visit = fid
        else:
            assert False, src
        groups[down].append((down, visit, fty))

    pickle.dump(groups, open(".nk8s/groups.pkl", "wb"))

if __name__ == '__main__':
    main()
