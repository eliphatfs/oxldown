FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -q install -y -f build-essential pkg-config vlan automake autoconf dkms git rclone
ENV TORCH_CUDA_ARCH_LIST="6.1 7.5 8.0 8.6 8.9 9.0+PTX"
ENV FORCE_CUDA="1"
RUN pip install ninja git+https://github.com/eliphatfs/diffrp.git git+https://github.com/eliphatfs/kubetk.git
RUN python -c "from nvdiffrast.torch.ops import _get_plugin; _get_plugin()"
RUN python -c "from diffrp.plugins import mikktspace; mikktspace.execute"
