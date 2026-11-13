# 5. Sistem Güncelleme, Temel Paketler, Disk Genişletme

> Durum: ✅ Tamamlandı (2026-11-13). Çalıştırılan komutlar ve çıktıları [LOG.md](../LOG.md)'de.

## 5.0 Önce durumu okuyun

Değişiklik yapmadan önce mevcut durumu görün:

```bash
uname -r
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
sudo vgs; sudo lvs
df -h /
swapon --show
timedatectl
sudo apt-get update && apt list --upgradable
```

## 5.1 Sistem güncellemesi

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confold full-upgrade
cat /var/run/reboot-required.pkgs 2>/dev/null   # yeniden başlatma istenmiş mi?
```

- `DEBIAN_FRONTEND=noninteractive`: SSH üzerinden çalışırken ekrana soru çıkıp takılmaz.
- `--force-confold`: değiştirdiğiniz ayar dosyaları (netplan, sshd) korunur.
- **NVIDIA sürücüsünden önce yapın.** Sürücü DKMS ile çalışan kernel'e göre derlenir.

## 5.2 Saat dilimi

```bash
sudo timedatectl set-timezone Europe/Istanbul
timedatectl    # "System clock synchronized: yes" ve "NTP service: active" olmalı
```

## 5.3 Temel araçlar

```bash
sudo apt-get -y install build-essential git curl htop btop nvtop tmux unzip pciutils
```

| Paket | Neden |
|---|---|
| `build-essential` | NVIDIA DKMS modülü ve bazı Python paketleri derlemek için `gcc`/`make` |
| `nvtop` | GPU kullanımını izleme |
| `htop`, `btop` | CPU/RAM izleme |
| `tmux` | SSH koparsa uzun işlemler ölmez |
| `git`, `curl`, `unzip`, `pciutils` | Genel araçlar, `lspci` |

## 5.4 Disk genişletme (gerekirse)

Ubuntu installer LVM'de bazen diskin yarısını ayırır. `sudo vgs` çıktısında `VFree` 0 değilse:

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
```

Bu kurulumda kurulum sırasında tüm disk seçildiği için **gerekmedi** (`VFree 0`).

## 5.5 Swap

24.04 varsayılan olarak `/swap.img` dosyası oluşturur (bu kurulumda 8 GB). 32 GB RAM için yeterli.

## 5.6 Otomatik güvenlik güncellemeleri

`unattended-upgrades` varsayılan olarak kurulu ve açık. Kontrol:

```bash
cat /etc/apt/apt.conf.d/20auto-upgrades
grep -vE '^\s*//|^\s*$' /etc/apt/apt.conf.d/50unattended-upgrades
```

- Varsayılan: sadece Ubuntu ana ve güvenlik depoları.
- `Automatic-Reboot` tanımlı değil, varsayılanı `false`. Sunucu habersiz yeniden başlamaz.
- Kernel güvenlik güncellemesi gelirse NVIDIA modülü DKMS ile yeniden derlenir (adım 6'da kontrol).

## 5.7 Yeniden başlatma

```bash
sudo systemctl reboot
# geri geldikten sonra:
uptime; uname -r; ls /var/run/reboot-required; systemctl --failed
```
