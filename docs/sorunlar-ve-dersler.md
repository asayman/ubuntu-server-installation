# Sorunlar, Çözümler, Doğrular / Yanlışlar

Kurulum boyunca karşılaşılan her sorun buraya eklenir. Format:
**Belirti → Neden → Çözüm → Sonuç.**

## Bilinen tuzaklar (kuruluma başlamadan önce)

### LVM kök birimi ~100 GB oluşturuluyor
- **Belirti:** 480 GB diske kurulum sonrası `df -h /` ~98 GB gösterir.
- **Neden:** Ubuntu installer `ubuntu-lv`'yi volume group'un tamamı kadar oluşturmaz.
- **Çözüm:** Kurulumda `ubuntu-lv → Edit → Size: max`. Ya da sonradan
  `lvextend -l +100%FREE` + `resize2fs`. Bkz. [02](02-ubuntu-kurulum.md).

### Secure Boot ve NVIDIA
- **Belirti:** Sürücü kurulduktan sonra `nvidia-smi` → `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver`.
  `mokutil --sb-state` → `SecureBoot enabled`.
- **Neden:** DKMS ile derlenen modül imzasız; Secure Boot yüklemeyi reddeder. MOK kaydı açılışta
  mavi "Perform MOK management" ekranında fiziksel onay ister.
- **Çözüm:** BIOS'ta Secure Boot'u kapatmak (bu repoda tercih edilen). Alternatif: Ubuntu'nun
  önceden imzalı `linux-modules-nvidia-*` paketlerini kullanmak veya MOK kaydını konsoldan yapmak.

### Docker'ı snap olarak kurmak
- **Yanlış:** Kurulumdaki "Featured server snaps" ekranından `docker` seçmek.
- **Neden:** Snap Docker, NVIDIA Container Toolkit yapılandırmasıyla sorun çıkarır.
- **Doğru:** Docker'ı resmi `download.docker.com` apt deposundan kurmak.

### netplan `gateway4`
- **Yanlış:** Eski rehberlerdeki `gateway4: 192.168.1.1`.
- **Doğru:** `routes: [{to: default, via: 192.168.1.1}]`.

### `ssh.service` inactive görünmesi
- **Belirti:** `systemctl status ssh` → inactive (dead), ama bağlantı çalışıyor.
- **Neden:** 24.04'te socket activation (`ssh.socket`).
- **Sonuç:** Sorun değil.

## Kurulum sırasında yaşananlar

### Custom storage layout ekranında takılmak
- **Belirti:** "To continue you need to: Mount a filesystem at / / Select a boot disk".
  Disk eski Windows bölümleriyle (ESP, MSR, NTFS) listeleniyor.
- **Neden:** "Custom storage layout" her şeyin elle yapılmasını ister (boot disk, /boot, VG, LV, `/`).
- **Doğru:** `Back` → **Use an entire disk** → hedef disk (USB değil!) → **Set up this disk as an LVM group**
  → özet ekranında `ubuntu-lv` → Edit → Size: max.
- **Yanlış:** Kurulum USB'sini (Kingston vb.) hedef disk seçmek.

### Uzaktan `netplan apply` sonrası SSH zaman aşımı
- **Belirti:** `ssh: connect to host 192.168.68.118 port 22: Operation timed out`
- **Neden:** DHCP → statik geçişinde arayüz birkaç saniye yeniden yapılandırılıyor.
- **Çözüm:** Birkaç saniye bekleyip yeniden bağlanmak. Önlem olarak `systemd-run --on-active=180`
  ile otomatik geri alma zamanlayıcısı kurmak (bkz. [03](03-sabit-ip.md#36-alternatif-ssh-üzerinden-uzaktan-uygulama)).
- **Sonuç:** IP aynı kaldığı için ikinci denemede bağlantı geldi.

### Yanlış arayüz adı
- **Yanlış:** Dokümandaki örneği (`eno1`) olduğu gibi kullanmak.
- **Doğru:** `ip -br a` ile `UP` olan arayüzü bulmak. HP Z4 G4'te kablo `eno2`'deydi, `eno1` DOWN.


## NVIDIA sürücüsü

### `ubuntu-drivers install --gpgpu` sonrası `nvidia-smi` yok
- **Belirti:** Sürücü kuruldu ama `nvidia-smi: command not found`.
- **Neden:** `--gpgpu` sadece `nvidia-headless-no-dkms-XXX` ve hazır kernel modülünü kurar.
- **Çözüm:** `sudo apt install nvidia-utils-XXX-server` (aynı sürüm numarası).

### Persistence mode kapalı geliyor
- **Belirti:** `nvidia-persistenced` aktif ama `nvidia-smi -q` → `Persistence Mode: Disabled`.
- **Neden:** Ubuntu paketi servisi `--no-persistence-mode` ile başlatıyor.
- **Çözüm:** systemd override ile `--persistence-mode` (bkz. [06](06-nvidia-surucu.md#63-persistence-mode)).
- **Yanlış:** `/lib/systemd/system/nvidia-persistenced.service` dosyasını doğrudan düzenlemek.
  Paket güncellemesinde değişiklik silinir.

### "recommended" sürücü masaüstü varyantı
- `ubuntu-drivers devices` masaüstü için `nvidia-driver-XXX-open` önerir.
- Ekransız sunucuda `--gpgpu` + `-server-open` kullanın. Masaüstü grafik paketleri gelmez.

## Docker

### `usermod -G` ile sudo yetkisini kaybetmek
- **Yanlış:** `sudo usermod -G docker $USER`. Kullanıcı diğer gruplarından (`sudo` dahil) çıkarılır.
- **Doğru:** `sudo usermod -aG docker $USER` (`-a` = append).
- Grup üyeliği yeni oturumda geçerli olur. Yeni SSH bağlantısı açın.

### Container içinde CUDA sürümü
- Container imajının CUDA sürümü sunucudaki sürücünün desteklediği en yüksek sürümü
  (`nvidia-smi` → `CUDA Version`) aşmamalı. Aşarsa container `CUDA driver version is insufficient` hatası verir.

## Python / uv

### Yavaş internette `uv pip install` zaman aşımı
- **Belirti:** `error: Failed to download ... cause: operation timed out` (PyTorch CUDA paketleri, `pypi.nvidia.com`).
- **Neden:** `uv` çok sayıda dosyayı paralel indirir; varsayılan HTTP timeout 30 sn.
- **Çözüm:** `export UV_HTTP_TIMEOUT=300 UV_CONCURRENT_DOWNLOADS=2` ve komutu tekrar deneyen bir döngü.
  Uzun kurulumları `tmux` içinde çalıştırın; SSH koparsa kurulum durmaz.

### `import ultralytics` → `libGL.so.1` hatası
- **Belirti:** `ImportError: libGL.so.1: cannot open shared object file: No such file or directory` (`cv2` import sırasında).
- **Neden:** `ultralytics` normal `opencv-python` paketini kurar. Bu paket grafik kütüphanesi `libGL` ister.
  Ekransız Ubuntu Server'da `libGL` kurulu gelmez.
- **Çözüm:** `sudo apt-get install -y --no-install-recommends libgl1`.
- **Alternatif:** `opencv-python-headless`. Ama `ultralytics` güncellenince normal opencv geri gelebilir.
