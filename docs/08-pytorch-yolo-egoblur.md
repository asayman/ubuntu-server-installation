# 8. Python Ortamı, PyTorch, YOLO, EgoBlur

> Durum: 🔄 Devam ediyor. 8.1 ve 8.2 tamam.

## Yaklaşım

- Python ortam yöneticisi: `uv` (hızlı, izole sanal ortamlar). Proje başına ayrı venv, doğrudan sunucuda.
- PyTorch CUDA wheel'leri (CUDA runtime wheel ile gelir; sistem geneline CUDA Toolkit
  yalnızca derleme gerekirse kurulacak)
- Notebook: VS Code Remote-SSH + `ipykernel`.

## 8.1 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh -o ~/tmp/uv-install.sh   # önce indir, incele
sh ~/tmp/uv-install.sh
~/.local/bin/uv --version
```

Etkileşimsiz SSH (`ssh sunucu 'komut'`) `~/.bashrc` PATH satırını okumaz. Script içinde
`export PATH="$HOME/.local/bin:$PATH"` kullanın.

## 8.2 YOLO ortamı: PyTorch + Ultralytics

OpenCV için sistem kütüphanesi (ekransız sunucuda eksik):

```bash
sudo apt-get install -y --no-install-recommends libgl1
```

venv ve paketler (yavaş internet ayarları ile):

```bash
export PATH="$HOME/.local/bin:$PATH"
export UV_HTTP_TIMEOUT=300 UV_CONCURRENT_DOWNLOADS=2
mkdir -p ~/projects/yolo && cd ~/projects/yolo
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cu130
uv pip install --python .venv/bin/python ultralytics ipykernel
```

Uzun sürebilir (bu kurulumda yaklaşık 3 saat). `tmux` içinde çalıştırın.

GPU testi:

```bash
.venv/bin/python - <<PY
import torch, torchvision, ultralytics, cv2
print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))
x = torch.randn(4096, 4096, device="cuda"); y = x @ x; torch.cuda.synchronize()
print("matmul ok:", tuple(y.shape))
PY
```

Beklenen çıktı (bu kurulum):

```
2.14.1+cu130 13.0 True NVIDIA RTX A4000
matmul ok: (4096, 4096)
```

## Yapılacak

- Ultralytics YOLO: örnek görüntü/video üzerinde GPU inference
- FFmpeg (NVENC/NVDEC destekli video işleme)
- EgoBlur (Meta): yüz ve plaka bulanıklaştırma modelleri, örnek video üzerinde çalıştırma
