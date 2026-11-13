# 6. NVIDIA Sürücüsü

> Durum: ✅ Tamamlandı (2026-11-13). Sürücü `595.91.07` (`595-server-open`), CUDA üst sınırı 13.2.
> Komutlar ve çıktılar [LOG.md](../LOG.md)'de.

Ön koşul: Secure Boot kapalı (adım 2). Açıksa açılışta ekran başında MOK anahtarı onaylamak gerekir.

## 6.0 Seçenekleri görün

```bash
lsmod | grep -E "nouveau|nvidia"     # şu an hangi sürücü yüklü?
sudo ubuntu-drivers list --gpgpu     # sunucu (hesaplama) için seçenekler
sudo ubuntu-drivers devices          # masaüstü önerisi ("recommended")
```

Varyantlar:

| Ek | Anlamı |
|---|---|
| `-server` | Veri merkezi kolu, uzun destek. `--gpgpu` ile masaüstü paketleri gelmez. |
| `-open` | NVIDIA açık kernel modülü. Turing ve sonrası (Ampere/A4000 dahil) için NVIDIA önerisi. |

Sürüm kolu, çalıştırabileceğiniz en yeni CUDA sürümünü belirler (`nvidia-smi` → `CUDA Version`).
Bu kurulumda 580 / 595 / 615 vardı; orta yol olarak **595** seçildi.

## 6.1 Kurulum

```bash
sudo ubuntu-drivers install --gpgpu nvidia:595-server-open
sudo apt install nvidia-utils-595-server      # nvidia-smi; --gpgpu bunu kurmaz
```

- Kernel modülü `linux-modules-nvidia-595-server-open-generic` ile **hazır derlenmiş** gelir.
  DKMS derlemesi yok; kernel güncellemesinde eşleşen modül paketi de gelir.
- `nouveau` otomatik olarak blacklist'e alınır (`/lib/modprobe.d/`).

## 6.2 Yeniden başlatma ve doğrulama

```bash
sudo systemctl reboot
# geri geldikten sonra:
lsmod | grep -E "^(nvidia|nouveau)"   # nvidia var, nouveau yok
nvidia-smi
```

## 6.3 Persistence mode

Ubuntu paketi `nvidia-persistenced` servisini `--no-persistence-mode` ile başlatır.
Kalıcı mod kapalıyken her CUDA işi GPU'yu yeniden başlatır (gecikme).
Paket dosyasını değil, systemd override'ı değiştirin:

```bash
systemctl cat nvidia-persistenced | grep ExecStart     # mevcut parametreler
sudo mkdir -p /etc/systemd/system/nvidia-persistenced.service.d
printf "[Service]\nExecStart=\nExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --persistence-mode --verbose\n" \
  | sudo tee /etc/systemd/system/nvidia-persistenced.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart nvidia-persistenced
nvidia-smi -q | grep -i "Persistence Mode"     # Enabled
```

Boşta GPU `P8` durumuna iner (bu kurulumda ~14 W).
