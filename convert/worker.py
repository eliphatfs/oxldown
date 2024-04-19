import os
import sys
import time
import uuid
import json
import gzip
import shutil
import subprocess
import kubetk.arch.worker as wk

import cutil


def download(x):
    down, group = json.loads(x)
    xid = str(uuid.uuid4())
    subprocess.check_call(["rclone", "--config", "rclone-internal.conf", "copy", "haosus3:objaverse-xl/" + down, "load/" + xid])
    return group, xid


def submit_log(u5, meta: dict):
    wk.get_rpc_object(os.getenv("MDS_ADDR")).add_log(json.dumps(dict(u5=u5, **meta)))


def process(x):
    group, xid = x
    for down, main, fty in group:
        u5 = cutil.str_hash_to_uuid(down + '::' + main)
        try:
            visit = "load/" + xid + "/" + main
            sha = cutil.get_file_hash(visit)
            meta_info = dict(sha=sha)
            meta_info['bpy'] = subprocess.call([sys.executable, "convert/bpy_job.py", visit, fty, f"save/{u5}"], timeout=600)
            if fty == 'glb':
                shutil.copyfile(visit, f"save/{u5}.glb")
            if os.path.exists(f"save/{u5}.blend"):
                MEG = 2**20
                with open(f"save/{u5}.blend", 'rb') as f_in:
                    with gzip.open(f"save/{u5}.blend.gz", 'wb', compresslevel=1) as f_out:
                        shutil.copyfileobj(f_in, f_out, length=2*MEG)
                meta_info['blend'] = subprocess.call(["rclone", "--config", "rclone-internal.conf", "copy", f"save/{u5}.blend.gz", "haosus3:oxl-curated/blendgz"])
                os.remove(f"save/{u5}.blend")
                os.remove(f"save/{u5}.blend.gz")
            else:
                meta_info['blend'] = 'missing'
            if os.path.exists(f"save/{u5}.glb"):
                meta_info['glb'] = subprocess.call(["rclone", "--config", "rclone-internal.conf", "copy", f"save/{u5}.glb", "haosus3:oxl-curated/glb"])
                os.remove(f"save/{u5}.glb")
            else:
                meta_info['glb'] = 'missing'
            if os.path.exists(f"save/{u5}.json"):
                with open(f"save/{u5}.json") as fi:
                    meta_info.update(json.load(fi))
                os.remove(f"save/{u5}.json")
            submit_log(u5, meta_info)
        except Exception as exc:
            submit_log(u5, dict(error=repr(exc)))
    return xid


def readonly_handler(func, path, execinfo): 
    os.chmod(path, 511)  #or os.chmod(path, stat.S_IWRITE) from "stat" module
    func(path)


def clear(xid):
    shutil.rmtree('load/' + xid, onerror=readonly_handler)


if __name__ == '__main__':
    ip = sys.argv[-1]
    os.makedirs('save', exist_ok=True)
    wk.run_pipelined_worker(f"http://{ip}:9105", [
        (download, 2),
        (process, 1),
        (clear, 1)
    ])
