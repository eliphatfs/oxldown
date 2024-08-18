import os
import sys
import time
import json
import numpy
import pyexr
import torch
import trimesh
import subprocess
from typing import BinaryIO
import kubetk.arch.worker as wk
from trimesh.util import decode_text
from diffrp.rendering.camera import PerspectiveCamera
from diffrp.scene import Scene, ImageEnvironmentLight
from diffrp.loaders.gltf_loader import load_gltf_scene
from diffrp.rendering.surface_deferred import SurfaceDeferredRenderSession, SurfaceDeferredRenderSessionOptions
from diffrp.utils import gpu_f32, length, transform_point4x3, singleton_cached, float4, agx_base_contrast, ssaa_downscale, to_pil


_magic = {"gltf": 1179937895, "json": 1313821514, "bin": 5130562}
torch.set_grad_enabled(False)
light = ImageEnvironmentLight(1.0, gpu_f32([1.0, 1.0, 1.0]), gpu_f32(pyexr.read("previewer/city.exr")), render_skybox=False)
opts = SurfaceDeferredRenderSessionOptions(
    ibl_specular_samples=1024,
    max_layers=4
)


@singleton_cached
def light_cache():
    ibl_cache_scene = Scene().add_light(light)
    return SurfaceDeferredRenderSession(ibl_cache_scene, PerspectiveCamera(), options=opts).prepare_ibl()


def load_glb_header(
    file_obj: BinaryIO
):
    # read the first 20 bytes which contain section lengths
    head_data = file_obj.read(20)
    head = numpy.frombuffer(head_data, dtype="<u4")

    # check to make sure first index is gltf magic header
    if head[0] != _magic["gltf"]:
        raise ValueError("incorrect header on GLB file")

    # and second value is version: should be 2 for GLTF 2.0
    if head[1] != 2:
        raise NotImplementedError(f"only GLTF 2 is supported not `{head[1]}`")

    # overall file length
    # first chunk length
    # first chunk type
    length, chunk_length, chunk_type = head[2:]

    # first chunk should be JSON header
    if chunk_type != _magic["json"]:
        raise ValueError("no initial JSON header!")

    # uint32 causes an error in read, so we convert to native int
    # for the length passed to read, for the JSON header
    json_data = file_obj.read(int(chunk_length))
    # convert to text
    if hasattr(json_data, "decode"):
        json_data = decode_text(json_data)
    # load the json header to native dict
    return json.loads(json_data)


def download(x):
    path = "load/" + x + ".glb"
    subprocess.check_call(["rclone", "--config", "rclone-internal.conf", "copy", "haosus3:oxl-curated/glb/" + x + ".glb", "load/"])
    return x, path


def normalize(gltf: Scene):
    bmin = gpu_f32([1e30] * 3)
    bmax = gpu_f32([-1e30] * 3)
    world_v = [transform_point4x3(prim.verts, prim.M) for prim in gltf.objects]
    for verts, prim in zip(world_v, gltf.objects):
        bmin = torch.minimum(bmin, verts.min(0)[0])
        bmax = torch.maximum(bmax, verts.max(0)[0])
    center = (bmin + bmax) / 2
    radius = max(length(verts - center).max() for verts in world_v).item()
    T = trimesh.transformations.translation_matrix(-center.cpu().numpy())
    S = trimesh.transformations.scale_matrix(1 / radius)
    M = gpu_f32(S @ T)
    for prim in gltf.objects:
        prim.M = M @ prim.M
    return gltf


def load(bundle):
    for i in range(8):
        try:
            torch.zeros([1024, 1024, 4], device='cuda')
        except torch.cuda.OutOfMemoryError:
            print("Cuda OOM, waiting for it to resolve in", 2 ** i)
            if i == 7:
                print("OOM Timeout, restarting the container...")
                os._exit(2)
            time.sleep(2 ** i)
        except RuntimeError as exc:
            if 'cuda' in repr(exc).lower():
                print("Cuda runtime error, restarting the container...")
                os._exit(1)
    u5, path = bundle
    try:
        with open(path, 'rb') as fi:
            header = load_glb_header(fi)
        problems = {}
        unmet_req_ext = [x for x in header.get('extensionsRequired', []) if x != 'KHR_materials_pbrSpecularGlossiness']
        unmet_use_ext = [x for x in header.get('extensionsUsed', []) if x != 'KHR_materials_pbrSpecularGlossiness']
        if len(unmet_req_ext):
            problems['ure'] = unmet_req_ext
        if len(unmet_use_ext):
            problems['uue'] = unmet_use_ext
        for sampler in header.get('samplers', []):
            if sampler.get('wrapS', 10497) != 10497 or sampler.get('wrapT', 10497) != 10497:
                problems['pwe'] = 1
            if sampler.get('magFilter', 9729) != 9729 or sampler.get('minFilter', 9729) not in (9729, 9986, 9987):
                problems['pse'] = 1
        try:
            scene = load_gltf_scene(path, compute_tangents=True)
            if problems.get('pwe') == 1:
                for mo in scene.objects:
                    if ((mo.uv < 0) | (mo.uv > 1)).any():
                        problems['pwe'] = 2
                        break
        finally:
            if len(problems):
                wk.get_rpc_object(os.getenv("MDS_ADDR")).add_log(json.dumps(dict(
                    u5=u5, **problems
                )))
    finally:
        os.remove(path)
    return u5, scene


def render(bundle):
    u5, scene = bundle
    scene = normalize(scene)
    scene.add_light(light)
    cam = PerspectiveCamera.from_orbit(1024, 1024, 3.8, 30, 30, [0, 0, 0])
    rp = SurfaceDeferredRenderSession(scene, cam, opaque_only=False, options=opts)
    rp.set_prepare_ibl(light_cache())
    pbr_premult = rp.compose_layers(
        rp.pbr_layered() + [torch.zeros([1024, 1024, 3], device='cuda')],
        rp.alpha_layered() + [torch.zeros([1024, 1024, 1], device='cuda')]
    )
    pbr = ssaa_downscale(pbr_premult, 2)
    pbr = float4(agx_base_contrast(pbr.rgb / torch.clamp_min(pbr.a, 0.0001)), pbr.a)
    return u5, pbr


def serialize(bundle):
    u5, pbr = bundle
    path = "save/" + u5 + ".png"
    to_pil(pbr).save(path)
    return u5, path


def save(bundle: tuple):
    u5, path = bundle
    for i in range(6):
        print("upload", path, "to", u5, "attempt", i)
        ret = os.system(f"rclone --config rclone-internal.conf copy {path} haosus3:oxl-preview-v1/")
        if 0 == ret:
            return os.remove(path)
        print("failed, retrying in", 2 ** i)
        time.sleep(2 ** i)
    else:
        raise ValueError('rclone return status', ret)


if __name__ == '__main__':
    ip = sys.argv[-1]
    os.makedirs('save', exist_ok=True)
    wk.run_pipelined_worker(f"http://{ip}:9105", [
        (download, 16),
        (load, 1),
        (render, 1),
        (serialize, 2),
        (save, 4),
    ])
