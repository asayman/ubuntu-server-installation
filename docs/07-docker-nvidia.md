# 7. Docker + NVIDIA Container Toolkit

> Durum: ⏳ Yapılacak.

Planlanan yaklaşım:

- Docker Engine resmi apt deposundan (snap değil)
- Kullanıcıyı `docker` grubuna ekleme
- `nvidia-container-toolkit` kurulumu, `nvidia-ctk runtime configure --runtime=docker`
- Doğrulama: `docker run --rm --gpus all nvidia/cuda:<tag> nvidia-smi`
