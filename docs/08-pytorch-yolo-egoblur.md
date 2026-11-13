# 8. Python Ortamı, PyTorch, YOLO, EgoBlur

> Durum: ⏳ Yapılacak.

Planlanan yaklaşım:

- Python ortam yöneticisi: `uv` (hızlı, izole sanal ortamlar)
- PyTorch CUDA wheel'leri (CUDA runtime wheel ile gelir; sistem geneline CUDA Toolkit
  yalnızca derleme gerekirse kurulacak)
- `torch.cuda.is_available()` ve basit benchmark
- Ultralytics YOLO: örnek görüntü/video üzerinde GPU inference
- EgoBlur (Meta): yüz ve plaka bulanıklaştırma modelleri, örnek video üzerinde çalıştırma
- FFmpeg (NVENC/NVDEC destekli video işleme)
