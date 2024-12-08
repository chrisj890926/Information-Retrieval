## ***VSCODE Terminal***
```python
conda create -n yolov8_env python=3.9


conda activate yolov8_env # 激活conda環境

pip install ultralytics opencv-python 
# 帶有GUI功能的OpenCV

# 確認是否environment location 為 anaconda

pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/mps
# 安裝PyTorch及相關庫

conda install -n yolov8_env ipykernel
# 在內核中選擇yolov8_env(Python3.9.19) 
# interpreter也要記得一樣
```
