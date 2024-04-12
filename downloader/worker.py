import os
import sys
import time
import uuid
import shutil
import requests
import subprocess
import kubetk.arch.worker as wk


write_dir = '/objaverse-processed1/geometry_pkl'


def readonly_handler(func, path, execinfo): 
    os.chmod(path, 511)  #or os.chmod(path, stat.S_IWRITE) from "stat" module
    func(path)


def download_github(idt: str):
    repo_id_hash = idt
    org, repo, commit_hash = repo_id_hash.split("/")
    subprocess.check_call(["git", "clone", "-q", "--depth", "1", f"https://github.com/{org}/{repo}.git", commit_hash])
    subprocess.check_call(["git", "fetch", "-q", "origin", commit_hash], cwd=commit_hash)
    subprocess.check_call(["git", "reset", "--hard"], cwd=commit_hash)
    subprocess.check_call(["git", "checkout", "-q", commit_hash], cwd=commit_hash)
    subprocess.check_call(["git", "lfs", "pull"], cwd=commit_hash)
    shutil.rmtree(commit_hash + '/.git', onerror=readonly_handler)
    return commit_hash, 'github/' + idt


def download_thingi(idt: str):
    url = f"https://www.thingiverse.com/download:{idt}"
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(idt, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1048576): 
            f.write(chunk)
    time.sleep(5)
    return idt, 'thingiverse'


def download_smiths(idt: str):
    r = requests.get(idt, stream=True)
    r.raise_for_status()
    namespace = uuid.NAMESPACE_DNS
    oid = str(uuid.uuid5(namespace, idt)) + '.glb'
    with open(oid, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1048576): 
            f.write(chunk)
    return oid, 'smithsonian'


def download(x: str):
    src, idt = x.split(':', maxsplit=1)
    if src == 'github':
        return download_github(idt)
    if src == 'thingiverse':
        return download_thingi(idt)
    if src == 'smithsonian':
        return download_smiths(idt)
    assert False, src


def save(x: tuple):
    local, dst = x
    for i in range(6):
        print("upload", local, "to", dst, "attempt", i)
        ret = os.system(f"rclone --config rclone.conf copy {local} haosus3:objaverse-xl/data/{dst}")
        if 0 == ret:
            if os.path.isdir(local):
                shutil.rmtree(local, onerror=readonly_handler)
            else:
                os.remove(local)
            return
        print("failed, retrying in", 2 ** i)
        time.sleep(2 ** i)
    else:
        raise ValueError('rclone return status', ret)


if __name__ == '__main__':
    ip = sys.argv[-1]
    os.makedirs(write_dir, exist_ok=True)
    wk.run_pipelined_worker(f"http://{ip}:9105", [
        (download, 4),
        (save, 2)
    ])
