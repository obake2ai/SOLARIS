### for docker
```
pip install nvidia-pyindex
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12

sudo apt install libcudnn8


export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; import torch; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__) + ":" + os.path.dirname(torch.__file__) +"/lib")'`
```
