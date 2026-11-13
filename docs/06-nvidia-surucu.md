# 6. NVIDIA Sürücüsü

> Durum: ⏳ Yapılacak.

Planlanan yaklaşım:

- Ubuntu deposundaki imzalı sürücü paketleri: `ubuntu-drivers list --gpgpu`
- Sunucu (headless) olduğu için `nvidia-driver-XXX-server` veya `-server-open` varyantı
  (RTX A4000 Ampere, open kernel module destekli)
- Doğrulama: `nvidia-smi`, `nvidia-smi -q | grep -i persistence`
- Persistence mode (`nvidia-persistenced`)
- Kernel güncellemelerinde modülün sorunsuz yüklendiğinin kontrolü
