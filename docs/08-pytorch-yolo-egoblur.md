# 8. Python Ortamı, PyTorch, YOLO, EgoBlur

> Durum: ✅ Tamamlandı (2026-11-16).

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

## 8.3 FFmpeg + NVENC/NVDEC

Sürücü `--gpgpu` ile kurulduğu için GPU video kodlama kütüphaneleri ayrıca kurulur:

```bash
sudo apt-get install -y --no-install-recommends ffmpeg libnvidia-encode-595-server libnvidia-decode-595-server
ffmpeg -hide_banner -encoders | grep nvenc     # h264_nvenc, hevc_nvenc, av1_nvenc
```

## 8.4 EgoBlur ortamı

Ayrı venv. torch 8.2'deki sürümle aynı, `uv` önbelleğinden gelir:

```bash
export PATH="$HOME/.local/bin:$PATH"
mkdir -p ~/egoblur && cd ~/egoblur
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python "torch==2.14.1+cu130" "torchvision==0.29.1+cu130" --index-url https://download.pytorch.org/whl/cu130
uv pip install --python .venv/bin/python --no-deps egoblur==2.0.1
uv pip install --python .venv/bin/python moviepy==1.0.3 opencv-python-headless numpy av vrs tqdm decorator imageio imageio-ffmpeg proglog
```

- `egoblur 2.0.1` paketi `torch==2.9.1` ister. `--no-deps` ile kurun, yoksa torch eski sürüme iner.
  gen1 ve gen2 modelleri torch 2.14.1 ile çalıştı.
- Modeller (`ego_blur_lp_gen1.jit`, `ego_blur_face_gen1.jit`, `*_gen2.jit`) Meta'dan ayrıca indirilir.
  Bu kurulumda başka bir makineden `rsync` ile kopyalandı.
- `torch.jit.load` öncesi `import torchvision` gerekir (`torchvision::nms` op kaydı).
- gen2 modeli düz tensor kabul etmez. Paketin `EgoblurDetector` sınıfını `patch_instances` içinde kullanın
  ([sorunlar-ve-dersler](sorunlar-ve-dersler.md#egoblur)).

## 8.5 Hız testi (RTX A4000, 140 W)

2560x1440 araç kamerası videosu, 600 kare, yalnızca model çıkarımı.

| Model | ms/kare | kare/sn | VRAM maks. |
|---|---|---|---|
| EgoBlur plaka gen1 fp32 | 335.7 | 3.0 | 2.3 GB |
| EgoBlur plaka gen1 fp16 | 181.9 | 5.5 | 1.7 GB |
| EgoBlur plaka + yüz gen1 fp16 | 374.0 | 2.7 | 2.1 GB |
| EgoBlur plaka gen2 fp16, batch 1 | 63.7 | 15.7 | 1.0 GB |
| EgoBlur plaka gen2 fp16, batch 4 | 57.8 | 17.3 | 1.9 GB |
| YOLOv8n plaka, 1440, half | 16.6 | 60.2 | 0.3 GB |

- fp16, fp32'den 1.8 kat hızlı (gen1).
- gen2 (`EgoblurDetector`), görüntüyü 1200 piksele küçültür. gen1 tam çözünürlükte çalışır. Hız farkının çoğu buradan gelir.
  Tespit kalitesi bu testte ölçülmedi.
- Plaka + yüz (iki model) süreyi yaklaşık iki katına çıkarır.

Ayrıntılar: [LOG.md](../LOG.md), Adım 8.4.
