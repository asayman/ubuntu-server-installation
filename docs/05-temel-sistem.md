# 5. Sistem Güncelleme, Temel Paketler, Disk Genişletme

> Durum: ⏳ SSH bağlantısı sağlandıktan sonra yapılacak. Çalıştırılan komutlar ve çıktıları
> [LOG.md](../LOG.md)'ye işlenecek.

Planlanan adımlar:

1. `apt update && apt full-upgrade`, yeniden başlatma
2. Saat dilimi (`Europe/Istanbul`), NTP kontrolü
3. Temel araçlar: `build-essential`, `git`, `curl`, `htop`, `btop`, `nvtop`, `tmux`, `unzip`, `pciutils`
4. `ubuntu-lv` diski tamamını kullanmıyorsa `lvextend` + `resize2fs`
5. Swap kontrolü
6. Otomatik güvenlik güncellemeleri (`unattended-upgrades`) — kernel güncellemesinde NVIDIA
   DKMS modülünün yeniden derlenmesi kontrolü
