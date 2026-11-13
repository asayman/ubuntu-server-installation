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

_(Kurulum ilerledikçe eklenecek.)_
