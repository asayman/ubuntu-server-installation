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

