# Kurulum Günlüğü

Her kayıt: tarih, adım, çalıştırılan komut, çıktı (kısaltılmış), hata varsa çözümü, sonuç.
Kullanıcı adı, MAC adresi ve seri numaraları maskelenmiştir (`<kullanici>` vb.). Yerel ağ IP'si (192.168.68.x) özel ağ adresidir, internetten erişilemez; olduğu gibi bırakılmıştır.

---

## 2026-11-13 — Adım 1: ISO ve USB (Windows)

- Kaynak: https://ubuntu.com/download/server → Previous Releases → 24.04.2
- Dosya: `ubuntu-24.04.2-live-server-amd64.iso`
- Araç: Rufus, GPT + UEFI (non CSM), ISO Image mode
- Sonuç: ✅ USB hazır

## 2026-11-13 — Repo oluşturuldu

- Dokümantasyon iskeleti (adım 1-9), sorunlar dosyası ve bu günlük oluşturuldu.

## 2026-11-13 — Adım 2.1: BIOS (HP Z4 G4)

- Makine: HP Z4 G4 Workstation. BIOS'a `F10` ile girildi.
- Secure Boot: ✅ kapatıldı.
- SATA: HP BIOS'ta AHCI/RAID listesi yok; tek seçenek "SATA Controller RAID Mode" (on/off).
  - Karar: **Off** = AHCI modu.
- Wake On LAN: **Boot to Hard Drive** seçildi. Boot to Network = PXE (istenmiyor). Normal Boot Order = USB/ağ önde ise oradan açılmaya çalışabilir.
- S5 Maximum Power Savings: Disabled olmalı. Açıksa WoL kapalı makinede çalışmaz.
- Ders: HP iş istasyonlarında "AHCI" adlı bir seçenek aramayın. RAID Mode kapalı = AHCI.

## 2026-11-13 — Adım 2.3: Storage ekranı

- Installer'ın gördüğü diskler:
  - `SAMSUNG_MZVLB512HBJQ-000H1` (Samsung PM981a **NVMe**, 476.939G). Hedef disk.
    Üzerinde eski Windows bölümleri var: ESP 100M, MSR 16M, NTFS 476.196G, NTFS (recovery) 643M.
  - `Kingston_DataTraveler_3.0` 57.796G: kurulum USB'si (dokunulmaz).
  - `Generic_STORAGE_DEVICE` 0B: dahili kart okuyucu (önemsiz).
- Disk NVMe olduğu için BIOS'taki "SATA Controller RAID Mode" ayarı bu diski etkilemez.
- Sorun: "Custom storage layout" seçildi. Ekran "To continue you need to: Mount a filesystem at / ·
  Select a boot disk" diyerek ilerlemiyor. Custom modda ESP, /boot, VG ve LV elle oluşturulmalı.
- Çözüm: `Back` ile guided ekrana dönüp **Use an entire disk** (Samsung) + **Set up this disk as an
  LVM group** seçmek; özet ekranında `ubuntu-lv` boyutunu max yapmak.

- Guided ayarlar: Use an entire disk (Samsung 476.939G), LVM: ✅, LUKS şifreleme: ❌
  (şifreli disk her açılışta konsolda parola ister, uzaktan yönetimi engeller).
- `ubuntu-lv` Edit → Size: max yapıldı. Sonuç özeti:

| Mount | Boyut | Tip | Cihaz |
|---|---|---|---|
| `/` | 473.886G | ext4 | LVM `ubuntu-vg/ubuntu-lv` |
| `/boot` | 2.000G | ext4 | nvme partition 2 |
| `/boot/efi` | 1.049G | fat32 | nvme partition 1 (ESP) |

- Sonuç: ✅ Diskin tamamı kullanılıyor. Eski Windows bölümleri silinecek (onaylandı).

## 2026-11-13 — Adım 2.4: Kalan installer ekranları

Sonradan sunucuda doğrulananlar:
- Server name: `gpu-server` (`hostname` çıktısı).
- OpenSSH server kurulu ve çalışıyor (Mac'ten port 22 açık, `OpenSSH_9.6p1`).
- SSH şifre ile giriş açık (`/etc/cloud/cloud.cfg.d/99-installer.cfg` → `ssh_pwauth: true`).
  Anahtar girişi çalıştıktan sonra kapatılacak (docs/04, bölüm 4.7).

## 2026-11-13 — Adım 2.5: Kurulum tamamlandı, ilk kontroller

Konsolda (kullanıcı):

| Kontrol | Sonuç |
|---|---|
| `lsb_release -a` | Ubuntu 24.04.2 LTS |
| `lspci \| grep -i nvidia` | NVIDIA RTX A4000 görünüyor |
| `df -h /` | Size 466G, Used 11G ✅ (LVM max ayarı tuttu) |
| `ip -br a` | DHCP: `192.168.68.118/24` |

İstemciden (Mac) erişim kontrolü:

```bash
$ ping -c 2 192.168.68.118
2 packets transmitted, 2 packets received, 0.0% packet loss
$ nc -z 192.168.68.118 22
Connection to 192.168.68.118 port 22 [tcp/ssh] succeeded!
$ ssh-keyscan -t ed25519 192.168.68.118
# 192.168.68.118:22 SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.2
$ route -n get default | grep gateway
    gateway: 192.168.68.1
```

- Sonuç: ✅ Sunucu ağda, OpenSSH 9.6p1 çalışıyor (kurulumda "Install OpenSSH server" seçildi).
- Not: 192.168.68.0/24 ağı, TP-Link Deco mesh sistemlerinin varsayılan ağıdır.
- Karar: Sabit IP olarak mevcut adres `192.168.68.118` korunacak. Router'da DHCP rezervasyonu +
  sunucuda netplan statik ayar yapılacak (IP çakışmasını önlemek için ikisi birlikte).

## Adım 3-4: Sabit IP ve SSH (devam)

### SSH anahtarı (istemci: Mac)

Mevcut anahtar yerine bu sunucuya özel yeni anahtar oluşturuldu:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/gpu_server -N "" -C "mac-to-gpu-server" -q
ls -l ~/.ssh/gpu_server*
# -rw-------  ~/.ssh/gpu_server
# -rw-r--r--  ~/.ssh/gpu_server.pub
```

- Neden ayrı anahtar: sunucuya özel erişim tek başına iptal edilebilir; diğer sunuculara erişimi etkilemez.
- Parola (passphrase) boş: SSH üzerinden otomasyon (etkileşimsiz komut) için. Daha güvenlisi
  parola + `ssh-agent` (macOS'ta `UseKeychain yes`).
- Karar: Router'a şu an erişim yok. Sabit IP **sadece netplan** ile verilecek (`192.168.68.118`).
  Router'da DHCP rezervasyonu daha sonra yapılacak.
  - Risk: Rezervasyon yapılana kadar router bu IP'yi başka cihaza verebilir (düşük ihtimal; router
    genelde aynı MAC'e aynı IP'yi tutar).

### SSH bağlantısı ve geçici şifresiz sudo (kullanıcı)

```bash
ssh-copy-id -i ~/.ssh/gpu_server.pub <kullanici>@192.168.68.118
ssh -i ~/.ssh/gpu_server <kullanici>@192.168.68.118
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/90-setup-nopasswd
sudo chmod 440 /etc/sudoers.d/90-setup-nopasswd
sudo visudo -c        # parsed OK
```

- Sonuç: ✅ Tüm komutlar çalıştı, `visudo -c` → `parsed OK`.
- Gizlilik: Gerçek kullanıcı adı repoda `<kullanici>` olarak maskelenmiştir.

İstemci `~/.ssh/config` (Mac; mevcut dosya önce yedeklendi):

```
Host gpu-server
    HostName 192.168.68.118
    User <kullanici>
    IdentityFile ~/.ssh/gpu_server
    IdentitiesOnly yes
    ServerAliveInterval 30
```

Test:

```bash
$ ssh -o BatchMode=yes gpu-server 'hostname; sudo -n true && echo SUDO_OK; uname -r'
gpu-server
SUDO_OK
6.8.0-149-generic
```

- Sonuç: ✅ Şifresiz SSH + şifresiz sudo çalışıyor. Kernel `6.8.0-149-generic` (GA kernel).

---

## 2026-11-13 — Adım 3: Sabit IP (netplan, SSH üzerinden)

### Mevcut durum

```bash
$ ip -br a
lo     UNKNOWN  127.0.0.1/8 ::1/128
eno2   UP       192.168.68.118/24 metric 100 fe80::.../64
eno1   DOWN
$ cat /etc/netplan/50-cloud-init.yaml
network:
  version: 2
  ethernets:
    eno2:
      dhcp4: true
$ resolvectl dns
Link 2 (eno2): 64.6.64.6 64.6.65.6 192.168.68.1
$ ls /etc/cloud/cloud-init.disabled
/etc/cloud/cloud-init.disabled
$ sudo ethtool eno2 | grep Wake-on
	Supports Wake-on: pumbg
	Wake-on: g
```

Gözlemler:
- HP Z4 G4'te iki onboard ethernet var: **eno1** (boş) ve **eno2** (kablo takılı). Dokümandaki
  örnek `eno1` değil, gerçek arayüz `eno2`. → Her zaman `ip -br a` ile kontrol edin.
- Ubuntu installer, ilk açılıştan sonra cloud-init'i zaten devre dışı bırakıyor
  (`/etc/cloud/cloud-init.disabled`). Yine de `99-disable-network-config.cfg` ek güvence olarak eklendi.
- Wake-on-LAN (`g` = magic packet) işletim sisteminde zaten aktif.

### Uygulama (uzaktan, otomatik geri alma ile)

`netplan try` etkileşimli onay (Enter) ister; etkileşimsiz SSH'ta kullanılamaz. Bunun yerine
önce **180 saniyelik otomatik geri alma zamanlayıcısı** kuruldu, sonra `netplan apply` yapıldı:

```bash
echo "network: {config: disabled}" | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
sudo cp /etc/netplan/50-cloud-init.yaml /root/50-cloud-init.yaml.bak
sudo tee /etc/netplan/01-static.yaml <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    eno2:
      dhcp4: false
      dhcp6: false
      wakeonlan: true
      addresses:
        - 192.168.68.118/24
      routes:
        - to: default
          via: 192.168.68.1
      nameservers:
        addresses: [192.168.68.1, 1.1.1.1, 8.8.8.8]
EOF
sudo chmod 600 /etc/netplan/01-static.yaml
sudo rm /etc/netplan/50-cloud-init.yaml
sudo netplan generate                       # GENERATE_OK

# Güvenlik ağı: 180 sn içinde iptal edilmezse eski DHCP ayarına dön
sudo systemd-run --unit=netplan-rollback --on-active=180 /bin/sh -c \
  "rm -f /etc/netplan/01-static.yaml; cp /root/50-cloud-init.yaml.bak /etc/netplan/50-cloud-init.yaml; netplan apply"

sudo nohup netplan apply >/tmp/netplan-apply.log 2>&1 &
```

Karşılaşılan durum:

```
ssh: connect to host 192.168.68.118 port 22: Operation timed out
```

- Neden: `netplan apply` arayüzü DHCP'den statiğe geçirirken bağlantı birkaç saniye kesildi;
  hemen ardından açılan yeni SSH bağlantısı zaman aşımına uğradı.
- Çözüm: Birkaç saniye bekleyip tekrar denemek. Port 22 ilk denemede açıktı.

Doğrulama:

```bash
$ ip -br a show eno2
eno2   UP   192.168.68.118/24 fe80::.../64
$ ip route
default via 192.168.68.1 dev eno2 proto static        # "proto dhcp" değil, static ✅
192.168.68.0/24 dev eno2 proto kernel scope link src 192.168.68.118
$ resolvectl dns eno2
Link 2 (eno2): 192.168.68.1 1.1.1.1 8.8.8.8
$ ping -c2 1.1.1.1      → 0% loss
$ ping -c2 ubuntu.com   → 0% loss (DNS çalışıyor)
$ networkctl status eno2
State: routable (configured)
eno2: DHCP lease lost                                 # beklenen: DHCP bırakıldı
```

Geri alma zamanlayıcısı iptal edildi:

```bash
sudo systemctl stop netplan-rollback.timer
```

Yeniden başlatma testi:

```bash
$ ssh gpu-server 'sudo systemctl reboot'
# ~55 sn sonra port 22 açık
$ ssh gpu-server 'uptime; ip -br a show eno2; ip route | head -1'
 up 0 min
eno2   UP   192.168.68.118/24
default via 192.168.68.1 dev eno2 proto static
```

- Sonuç: ✅ Sabit IP `192.168.68.118` yeniden başlatma sonrası korunuyor, internet + DNS çalışıyor.
- Yapılacak (kullanıcı): Router'da `192.168.68.118` için DHCP rezervasyonu (MAC: eno2), çakışmayı önlemek için.

---

## 2026-11-13 — Adım 5: Temel sistem (SSH üzerinden)

### 5.0 Durum tespiti (salt okuma)

```bash
$ uname -r
6.8.0-149-generic
$ lsblk / sudo vgs / sudo lvs
nvme0n1p3 473.9G LVM2_member → ubuntu-vg/ubuntu-lv 473.9G  (VFree 0)
$ df -h /
/dev/mapper/ubuntu--vg-ubuntu--lv  466G   11G  432G   3% /
$ swapon --show
/swap.img file 8G
$ timedatectl
Time zone: Etc/UTC, System clock synchronized: yes, NTP service: active
$ sudo apt-get update -qq && apt list --upgradable | wc -l
98   # başlık satırı dahil → 97 paket
$ dpkg -l unattended-upgrades
ii  unattended-upgrades 2.9.1+nmu4ubuntu1
```

- LVM zaten diskin tamamını kullanıyor (kurulumda seçilmişti). `lvextend` **gerekmedi**.
- 8 GB swap dosyası var, 32 GB RAM için yeterli. Değiştirilmedi.

### 5.1 Sistem güncellemesi

```bash
# önce kernel güncellemesi var mı?
$ apt list --upgradable | grep -E "linux-(image|headers|generic|modules)"
(boş)  # kernel zaten güncel
$ sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::=--force-confold full-upgrade
...
Service restarts being deferred: systemd-logind, dbus, unattended-upgrades, ModemManager
$ cat /var/run/reboot-required.pkgs
apparmor
```

- `noninteractive` + `--force-confold`: SSH üzerinden soru çıkıp takılmasın, mevcut ayar dosyaları korunsun.
- Neden NVIDIA'dan önce: sürücü DKMS ile çalışan kernel'e göre derlenir; önce kernel'i güncel tutmak gereksiz yeniden derlemeyi önler.

### 5.2 Saat dilimi

```bash
$ sudo timedatectl set-timezone Europe/Istanbul
Time zone: Europe/Istanbul (+03, +0300)
```

### 5.3 Temel araçlar

```bash
$ sudo DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential git curl htop btop nvtop tmux unzip pciutils
gcc 13.3.0 | git 2.43.0 | tmux 3.4 | nvtop 3.0.2
```

### 5.6 Otomatik güvenlik güncellemeleri (kontrol)

```bash
$ cat /etc/apt/apt.conf.d/20auto-upgrades
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
$ grep -v '//' /etc/apt/apt.conf.d/50unattended-upgrades
Allowed-Origins: noble, noble-security, ESM apps/infra security
# Automatic-Reboot tanımlı değil → varsayılan false
```

- Varsayılan uygun: sadece Ubuntu depoları, habersiz yeniden başlatma yok. Değiştirilmedi.
- NVIDIA kurulumundan sonra kernel güncellemesinde DKMS yeniden derlemesi kontrol edilecek (adım 6).

### 5.7 Yeniden başlatma

```bash
$ ssh gpu-server 'sudo systemctl reboot'   # ~50 sn sonra SSH geri geldi
$ uptime; uname -r; ip -br -4 a show eno2; ls /var/run/reboot-required; systemctl --failed
 up 0 min
6.8.0-149-generic
eno2  UP  192.168.68.118/24
ls: cannot access '/var/run/reboot-required': No such file or directory
(failed unit yok)
```

- Sonuç: ✅ Adım 5 tamamlandı.

---

## 2026-11-13 — Adım 6: NVIDIA sürücüsü (SSH üzerinden)

### 6.0 Seçenekler (salt okuma)

```bash
$ lsmod | grep nouveau
nouveau  3100672  0          # açık kaynak sürücü yüklü
$ sudo ubuntu-drivers list --gpgpu
nvidia-driver-{580,595,615}-server-open / -server / -open / (düz)
$ sudo ubuntu-drivers devices | grep recommended
driver : nvidia-driver-595-open - distro non-free recommended   # masaüstü önerisi
```

- Not: `udevadm hwdb is deprecated` ve `aplay command not found` uyarıları zararsız.
- Karar: **595-server-open**. 580 en kararlı ama en yeni CUDA imajlarını çalıştıramayabilir; 615 en yeni ama daha az test edilmiş.

### 6.1 Kurulum

```bash
$ sudo DEBIAN_FRONTEND=noninteractive ubuntu-drivers install --gpgpu nvidia:595-server-open
nvidia-headless-no-dkms-595-server-open
linux-modules-nvidia-595-server-open-generic
$ sudo apt-get -y install nvidia-utils-595-server     # --gpgpu nvidia-smi kurmuyor
$ dpkg -l | grep nvidia
linux-modules-nvidia-595-server-open-6.8.0-149-generic 6.8.0-149.149
nvidia-headless-no-dkms-595-server-open 595.91.07-0ubuntu0.24.04.1
nvidia-utils-595-server 595.91.07-0ubuntu0.24.04.1
...
$ cat /lib/modprobe.d/*nvidia* | grep nouveau
blacklist nouveau
```

### 6.2 Yeniden başlatma ve doğrulama

```bash
$ ssh gpu-server 'sudo systemctl reboot'   # ~50 sn sonra SSH geri geldi
$ lsmod | grep -E "^(nvidia|nouveau)"
nvidia_uvm, nvidia_drm, nvidia_modeset, nvidia   # nouveau yok ✅
$ nvidia-smi
NVIDIA-SMI 595.91.07   Driver Version: 595.91.07   CUDA Version: 13.2
0  NVIDIA RTX A4000   Off | 00000000:15:00.0 On | 41% 61C P0 51W/140W | 17MiB/16376MiB
```

### 6.3 Persistence mode

```bash
$ nvidia-smi -q | grep -i persistence
Persistence Mode : Disabled
$ systemctl is-active nvidia-persistenced
active          # servis çalışıyor ama mod kapalı
$ systemctl cat nvidia-persistenced | grep ExecStart
ExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --no-persistence-mode --verbose
```

- Neden: Ubuntu paketi `--no-persistence-mode` ile başlatıyor.
- Çözüm: systemd override (paket dosyasına dokunmadan):

```bash
$ sudo mkdir -p /etc/systemd/system/nvidia-persistenced.service.d
$ printf "[Service]\nExecStart=\nExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --persistence-mode --verbose\n" \
    | sudo tee /etc/systemd/system/nvidia-persistenced.service.d/override.conf
$ sudo systemctl daemon-reload && sudo systemctl restart nvidia-persistenced
$ nvidia-smi -q | grep -i "Persistence Mode"
Persistence Mode : Enabled
$ nvidia-smi --query-gpu=pstate,temperature.gpu,power.draw --format=csv
P8, 58, 14.01 W
```

- Sonuç: ✅ Adım 6 tamamlandı. Override'ın yeniden başlatma sonrası kalıcılığı adım 7'deki yeniden başlatmada doğrulanacak.

---

## 2026-11-13 — Adım 7: Docker + NVIDIA Container Toolkit (SSH üzerinden)

### 7.0 Durum

```bash
$ command -v docker; dpkg -l | grep -E "docker|containerd|podman"
docker yok    # snap veya docker.io da yok
```

### 7.1 Docker resmi deposu

```bash
$ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$ gpg --show-keys --with-fingerprint /etc/apt/keyrings/docker.asc
      9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88   # Docker'ın yayınladığı değerle aynı ✅
$ cat /etc/apt/sources.list.d/docker.sources
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
$ apt-cache policy docker-ce
Candidate: 5:29.9.3-1~ubuntu.24.04~noble
```

### 7.2 Docker Engine

```bash
$ sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
$ docker --version; docker compose version
Docker version 29.9.3, build 5457199
Docker Compose version v5.7.1
$ systemctl is-enabled docker containerd
enabled
enabled
$ sudo docker run --rm hello-world
Hello from Docker!
```

### 7.3 docker grubu

- Karar (kullanıcı): `docker` grubuna ekle. Fiilen şifresiz root yetkisi olduğu bilinerek seçildi
  (tek kullanıcılı ev sunucusu). Alternatifler: `sudo docker`, rootless Docker.

```bash
$ sudo usermod -aG docker "$USER"
# yeni SSH oturumu:
$ id -nG
<kullanici> adm cdrom sudo dip plugdev lxd docker
$ docker ps          # sudo olmadan çalıştı ✅
```

### 7.4 NVIDIA Container Toolkit

```bash
$ curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
$ gpg --show-keys --with-fingerprint /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
pub   rsa4096 2017-09-28 [SCE]
      C95B 321B 61E8 8C18 09C4  F759 DDCA E044 F796 ECB0
uid   NVIDIA CORPORATION (Open Source Projects) <cudatools@nvidia.com>
$ cat /etc/apt/sources.list.d/nvidia-container-toolkit.list
deb [signed-by=...] https://nvidia.github.io/libnvidia-container/stable/deb/$(ARCH) /
#deb [signed-by=...] .../experimental/deb/$(ARCH) /     # experimental kapalı
$ sudo apt-get -y install nvidia-container-toolkit
$ nvidia-ctk --version
NVIDIA Container Toolkit CLI version 1.20.2
```

### 7.5 nvidia runtime

```bash
$ sudo nvidia-ctk runtime configure --runtime=docker
level=info msg="Wrote updated config to /etc/docker/daemon.json"
$ cat /etc/docker/daemon.json
{ "runtimes": { "nvidia": { "args": [], "path": "nvidia-container-runtime" } } }
$ sudo systemctl restart docker
$ docker info | grep -i runtimes
 Runtimes: io.containerd.runc.v2 nvidia runc
```

### 7.6 GPU testi

```bash
$ docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 \
    nvidia-smi --query-gpu=name,driver_version,memory.total,persistence_mode --format=csv
NVIDIA RTX A4000, 595.91.07, 16376 MiB, Enabled
```

- İmaj CUDA 13.0 ≤ sürücü üst sınırı 13.2 → uyumlu.

### 7.7 Yeniden başlatma sonrası

```bash
$ ssh gpu-server 'sudo systemctl reboot'   # ~50 sn
$ systemctl is-active docker nvidia-persistenced
active
active
$ nvidia-smi -q | grep -i "Persistence Mode"
Persistence Mode : Enabled            # adım 6 override'ı kalıcı ✅
$ docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 nvidia-smi -L
GPU 0: NVIDIA RTX A4000 (UUID: GPU-<maskelendi>)
$ systemctl --failed
(failed unit yok)
```

- Sonuç: ✅ Adım 7 tamamlandı.

---

## 2026-11-13 — Adım 8: Python ortamı

### Kararlar

- Yaklaşım: `uv` sanal ortamı, doğrudan sunucuda (proje başına ayrı venv). Docker değil.
- Notebook: VS Code Remote-SSH + `ipykernel`. JupyterLab sonra kurulacak.
- PyTorch: `cu130` deposu (`torch 2.14.1+cu130`). Sürücü üst sınırı CUDA 13.2.

### 8.1 uv

```bash
$ curl -LsSf https://astral.sh/uv/install.sh -o ~/tmp/uv-install.sh   # önce indir, incele
$ head ~/tmp/uv-install.sh
APP_VERSION="0.13.8"
$ sh ~/tmp/uv-install.sh
$ uv --version
uv 0.13.8 (x86_64-unknown-linux-gnu)
```

- Not: `ssh gpu-server 'command -v uv'` boş döner. Etkileşimsiz SSH `~/.bashrc` PATH satırını okumaz.
  Tam yol `~/.local/bin/uv` veya `bash -lc` kullanın.

### 8.2 PyTorch kurulumu (tmux içinde, arka planda)

- İnternet hızı düştü (tüm ev ağı, Mac dahil: 10-300 KB/s). Sunucu kaynaklı değil.
- Ayrı bulgu: `ethtool eno2` → `Speed: 100Mb/s`. Kart 1 Gb/s destekliyor; kablo/port kontrol edilecek.
- 1. deneme hata:

```
error: Failed to download `nvidia-cufft==12.0.0.61`
  cause: operation timed out
```

- Neden: `uv` aynı anda 10+ dosya indiriyor; yavaş bağlantıda bir dosya 30 sn (varsayılan timeout) veri alamıyor.
- Çözüm: `UV_HTTP_TIMEOUT=300`, `UV_CONCURRENT_DOWNLOADS=2`, komut başına 5 tekrar deneme.
  Script `~/setup-08.sh`, `tmux` oturumu `setup8`, çıktı `~/setup-08.log`.

```bash
tmux new-session -d -s setup8 "bash ~/setup-08.sh > ~/setup-08.log 2>&1"
grep "^###" ~/setup-08.log     # STEP / RETRY / DONE / FAILED satırları
```

- Sonuç (`grep "^###" ~/setup-08.log`):

```
### STEP 1/4 venv 15:24:34
### STEP 2/4 torch+torchvision (cu130) 15:24:34
### RETRY 1/5 15:56:03
### STEP 3/4 ultralytics+ipykernel 18:24:42
### STEP 4/4 GPU testi 18:28:46
### FAILED (satır 22) 18:28:53
```

- torch + torchvision indirmesi yavaş internette yaklaşık 3 saat sürdü (1 tekrar deneme).
- Paketler kuruldu, GPU testi `import ultralytics` satırında düştü:

```
  File ".../site-packages/cv2/__init__.py", line 153, in bootstrap
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

- Neden: `ultralytics` normal `opencv-python` paketini kurar. Bu paket `libGL.so.1` ister.
  Ekransız sunucuda `libGL` yok.
- Seçenekler: (a) `apt install libgl1`, (b) `opencv-python` yerine `opencv-python-headless`.
  İkisi de yaklaşık 40-50 MB indirme. (b) `ultralytics` güncellenince normal opencv'yi geri getirebilir.
  Karar: (a), kalıcı çözüm.

```bash
$ sudo apt-get install -s -y --no-install-recommends libgl1 | grep newly
0 upgraded, 20 newly installed, 0 to remove and 3 not upgraded.   # ~40 MB (mesa, llvm)
```

### 8.2b libgl1 + GPU testi tekrar

- Script `~/setup-08b.sh`, `tmux` oturumu `setup8b`, çıktı `~/setup-08b.log`:

```bash
sudo apt-get update -o Acquire::Retries=5
sudo apt-get install -y --no-install-recommends -o Acquire::Retries=5 libgl1
cd ~/projects/yolo && .venv/bin/python - <<PY
import torch, torchvision, ultralytics, cv2
...
x = torch.randn(4096, 4096, device="cuda"); y = x @ x; torch.cuda.synchronize()
PY
```

- Çıktı:

```
torch 2.14.1+cu130 | torchvision 0.29.1+cu130 | ultralytics 8.4.212 | cv2 5.0.0
cuda available: True | torch CUDA: 13.0
device: NVIDIA RTX A4000
matmul ok: (4096, 4096)
### DONE 15:30:50
```

- Sonuç: ✅ Adım 8.2 tamamlandı. venv: `~/projects/yolo/.venv` (Python 3.12).

## 2026-11-14 — Adım 8.3: Model dosyaları, FFmpeg, EgoBlur ortamı

### 8.3a Model ve test videoları başka makineden kopyalandı

- Karar: modeller internetten tekrar indirilmedi. Elimdeki dosyalar LAN üzerinden `rsync` ile kopyalandı.

```bash
$ ssh gpu-server 'mkdir -p ~/data/models ~/data/egoblur ~/data/videos'
$ R="rsync -a --partial --exclude=._* --exclude=.DS_Store"
$ $R <kaynak>/ego_blur_*.jit   gpu-server:data/egoblur/   # EgoBlur gen1 + gen2 (lp, face)
$ $R <kaynak>/*.pt             gpu-server:data/models/    # YOLO modelleri
$ $R <kaynak>/*.mp4            gpu-server:data/videos/    # test videoları
$ ssh gpu-server 'mkdir -p ~/egoblur && ln -sfn ~/data/egoblur ~/egoblur/models'
```

- 4 EgoBlur `.jit` dosyası (her biri ~420 MB).
- LAN kopyalama hızı yalnızca ~3 MB/s oldu. Neden henüz araştırılmadı (`eno2` 100 Mb/s bağlantı, bkz. 8.2).

### 8.3b FFmpeg + NVENC/NVDEC + EgoBlur venv

- Script `~/setup-08c.sh`, çıktı `~/setup-08c.log`:

```bash
sudo apt-get install -y --no-install-recommends -o Acquire::Retries=5 ffmpeg time libnvidia-encode-595-server libnvidia-decode-595-server
cd ~/egoblur && uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python "torch==2.14.1+cu130" "torchvision==0.29.1+cu130" --index-url https://download.pytorch.org/whl/cu130
uv pip install --python .venv/bin/python --no-deps egoblur==2.0.1
uv pip install --python .venv/bin/python moviepy==1.0.3 opencv-python-headless numpy av vrs tqdm decorator imageio imageio-ffmpeg proglog
```

- torch aynı sürüm (8.2'deki), `uv` önbelleğinden geldi. Tekrar indirme olmadı. Kurulum ~2 dk.
- `egoblur 2.0.1` paketi `torch==2.9.1` sabitliyor. `--no-deps` ile kuruldu, bağımlılıklar elle verildi.
  gen1 ve gen2 modelleri torch 2.14.1 ile çalıştı.
- Sonuç:

```
### STEP 1/4 apt: ffmpeg + libnvidia-encode/decode 15:39:43
### STEP 2/4 egoblur venv 15:40:38
### STEP 3/4 kontrol: ffmpeg GPU 15:41:45
### STEP 4/4 kontrol: egoblur import 15:41:45
### DONE 15:41:52
```

```
$ ffmpeg -version | head -1
ffmpeg version 6.1.1-3ubuntu5
$ ffmpeg -hide_banner -encoders | grep nvenc
 V....D av1_nvenc   NVIDIA NVENC av1 encoder (codec av1)
 V....D h264_nvenc  NVIDIA NVENC H.264 encoder (codec h264)
 V....D hevc_nvenc  NVIDIA NVENC hevc encoder (codec hevc)
```

- Not: sürücü `--gpgpu` ile kurulduğu için NVENC/NVDEC kütüphaneleri (`libnvidia-encode`, `libnvidia-decode`)
  gelmez. FFmpeg ile GPU video kodlama için bu iki paket ayrıca kuruldu.

## 2026-11-14 — Adım 8.4: GPU hız testi

- Testler `tmux` içinde, sırayla, GPU boşken çalıştı. `nvidia-smi` ile GPU kullanımı, VRAM ve güç örneklendi.
- Girdi: 2560x1440 bir araç kamerası videosu, ilk 600 kare. Yalnızca model çıkarımı (bulanıklaştırma yok).

### 8.4a gen2 ilk deneme hataları

- 1. hata: gen1 için yazılmış test kodu modeli yüklerken `m.eval()` çağırıyor. gen2 `.jit` dosyası "frozen" olduğu için hata verdi.
  Çözüm:

```python
try:
    m.eval()
except RuntimeError:  # gen2 .jit is frozen: already in eval mode
    pass
```

- 2. hata: gen2 modeli tensor değil, detectron2 girdi listesi bekliyor:

```
RuntimeError: forward() Expected a value of type 'List[Dict[str, Tensor]]' for argument 'batched_inputs' but instead found type 'Tensor'.
```

- Çözüm: gen2 için paketin kendi `EgoblurDetector` sınıfı (`gen2.script.predictor`) kullanıldı
  (GPU'da 1200 piksele yeniden boyutlandırma + NMS). Çağrı `patch_instances(fields=PATCH_INSTANCES_FIELDS)`
  içinde olmalı. Resmi demo da böyle yapıyor.

### 8.4b Sonuçlar (RTX A4000)

| Model | ms/kare | kare/sn | GPU ort. | VRAM maks. | Güç ort. |
|---|---|---|---|---|---|
| EgoBlur plaka gen1 fp32 | 335.7 | 3.0 | 93% | 2.3 GB | 132 W |
| EgoBlur plaka gen1 fp16 | 181.9 | 5.5 | 87% | 1.7 GB | 129 W |
| EgoBlur plaka + yüz gen1 fp16 | 374.0 | 2.7 | 92% | 2.1 GB | 134 W |
| EgoBlur plaka gen2 fp32, batch 1 | 97.4 | 10.3 | 85% | 1.1 GB | 128 W |
| EgoBlur plaka gen2 fp16, batch 1 | 63.7 | 15.7 | 76% | 1.0 GB | 127 W |
| EgoBlur plaka gen2 fp16, batch 4 | 57.8 | 17.3 | 73% | 1.9 GB | 125 W |
| EgoBlur plaka + yüz gen2 fp16, batch 4 | 107.2 | 9.3 | 81% | 2.3 GB | 129 W |
| YOLOv8n plaka, 640, half | 13.6 | 73.5 | 11% | 0.2 GB | 54 W |
| YOLOv8n plaka, 1440, half | 16.6 | 60.2 | 20% | 0.3 GB | 64 W |
| YOLOv8x yüz, 1440, half | 44.3 | 22.6 | 69% | 0.6 GB | 122 W |

- fp16, fp32'den 1.8 kat hızlı (gen1).
- gen1 tam çözünürlükte çalışır. gen2 (`EgoblurDetector`) görüntüyü 1200 piksele küçültür. Hız farkının
  çoğu buradan gelir. Tespit kalitesi bu testte ölçülmedi.
- Güç: kartın varsayılan ve azami güç sınırı 140 W (`nvidia-smi -q -d POWER`). EgoBlur testlerinde kart bu sınıra yakın çalıştı.

## 2026-11-16 — Adım 8.5: Kopyalanan dosyaların bütünlük kontrolü (md5)

- Neden: kopyalama yavaştı (~3 MB/s), uzun sürdü. Dosyaların bozulmadığını doğrulamak gerekiyordu.

```bash
$ ssh gpu-server 'cd ~/data/videos && md5sum *.mp4' | awk '{print $1, $2}' | sort -k2 > srv.md5                   # sunucu
$ md5 -r <kaynak>/*.mp4 | awk '{sub(".*/","",$2); print $1, $2}' | sort -k2 > src.md5                             # kaynak makine (macOS)
$ diff src.md5 srv.md5 && echo ALL_MATCH
ALL_MATCH
```

- 7 videonun hepsi eşleşti.
- Sonuç: ✅ Adım 8 tamamlandı.

---

## 2026-11-16 — Adım 9.1-9.3: Ollama kurulumu, UFW

- `install.sh` incelendi, çalıştırılmadı. Aynı adımlar elle yapıldı. Komutlar: [docs/09](docs/09-lokal-llm.md).

```
### STEP 1/2 indirme v0.40.16 10:03:11
### STEP 2/2 sha256 10:25:08
ollama-linux-amd64.tar.zst: OK
### DONE 10:25:11
```

- UFW açıldı: OpenSSH (her yerden), 11434/tcp (yalnız yerel ağ). `systemd-run` ile 180 sn'lik emniyet kuruldu,
  yeni SSH girişi çalışınca iptal edildi.
- Servis ayarları: `OLLAMA_HOST=0.0.0.0:11434`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_NUM_PARALLEL=1`.
- GPU algılandı:

```
msg="inference compute" library=CUDA compute=8.6 description="NVIDIA RTX A4000" driver=13.2 total="15.6 GiB" available="15.4 GiB"
```

## 2026-11-16 — Adım 9.4: Model indirme

- Sorun: `ollama pull` yavaş hatta takıldı. Ana blob (5.5 GB) tek bağlantılı `curl` ile indirildi; 6 kez kesilip devam etti.

```
### STEP 1/4 blob indirme (tek bağlantı) 10:58:37
### RETRY 6 13:25:25 1080 MB
### STEP 2/4 sha256 + blob klasörüne taşıma 18:00:45
sha256-370c2879...d39c: OK
### STEP 3/4 ollama pull (kalan küçük dosyalar) 18:00:58
gemma4:e4b    dc35e8d9c606    6.6 GB
### STEP 4/4 open-webui imajı 18:30:42
### DONE 19:09:10
```

## 2026-11-23 — Adım 9.4: Model GPU testi

- `POST /api/generate`, `gemma4:e4b` (Q4_K_M, 7.5B), kısa Türkçe soru, `think=false`, iki kez:

| Çalıştırma | Yükleme | Çıktı token | token/sn |
|---|---|---|---|
| 1 | 64.7 sn | 142 | 117.5 |
| 2 | 0.002 sn | 149 | 109.8 |

- `ollama ps`: `100% GPU`, bağlam 4096. `nvidia-smi`: 4757 MiB toplam (llama-server 4732 MiB), 63 °C.
- API başka makineden de yanıt verdi (`/api/version` → `0.40.16`).

## 2026-11-23 — Adım 9.5: Open WebUI

- 1. deneme (`RAG_EMBEDDING_MODEL_AUTO_UPDATE` yok): 4 dakika sonra hâlâ `unhealthy`, 8080 kapalı.
  Log, HuggingFace'ten `all-MiniLM-L6-v2` modelinin ONNX/OpenVINO dosyalarının indiğini gösterdi.
  Gereken `model.safetensors` imajın içinde zaten vardı.
- Çözüm: container ve yeni oluşturulan boş volume silindi, `-e RAG_EMBEDDING_MODEL_AUTO_UPDATE=false` ile yeniden kuruldu.

```
health 200, 21s
```

- 8080/tcp UFW'de yalnız yerel ağa açıldı. Başka makineden `http://<sunucu-ip>:8080/` → 200, sürüm `0.13.3`.
- Container içinden Ollama erişimi: `/api/tags` → `gemma4:e4b`.
- Tarayıcı önce "site can't be reached" verdi. Aynı anda aynı makineden `curl` → 200; istek sunucu loguna hiç düşmedi.
  Sonra açıldı. Kesin neden doğrulanmadı.
- Yönetici hesabı oluşturuldu, arayüzden sohbet testi yapıldı: yanıt yaklaşık 3 sn (kullanıcı gözlemi).
- Arayüzdeki kullanım bilgisi (tek yanıt): 141.9 token/sn çıktı (717 token), 1174.8 token/sn girdi (2051 token),
  model yükleme 4.65 sn, toplam 14.2 sn.

## 2026-11-23 — Adım 9.6: Bağlam uzunluğu 16384

- Neden: arayüzdeki tek yanıtta girdi + çıktı 2768 token tuttu; 4096 bağlam çabuk doluyor.

```bash
echo 'Environment="OLLAMA_CONTEXT_LENGTH=16384"' | sudo tee -a /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

| Bağlam | VRAM | token/sn (2 çalıştırma) | GPU |
|---|---|---|---|
| 4096 | 4757 MiB | 117.5 / 109.8 | %100 |
| 16384 | 5157 MiB | 107.1 / 116.4 | %100 |

- Sonuç: ✅ Adım 9 tamamlandı.

## 2026-11-25 — Adım 9.7: Bağlam uzunluğu 65536

- Neden: kod asistanı (harness) istemleri birkaç adımda 7-8 bin token'a ulaştı.
- İstek bazında `num_ctx` ile ölçüldü (bağlamın yaklaşık %80'i dolu, `think=false`, boyut başına tek çalıştırma):

| Bağlam | İstem (token) | VRAM | İstemi okuma | Üretim |
|---|---|---|---|---|
| 16384 | 12935 | 5159 MiB | 2.4 sn | 166.6 token/sn |
| 32768 | 26344 | 5479 MiB | 4.9 sn | 153.3 token/sn |
| 65536 | 53789 | 5833 MiB | 11.8 sn | 129.8 token/sn |
| 131072 | 108669 | 6969 MiB | 31.3 sn | 99.0 token/sn |

```bash
sudo sed -i 's/OLLAMA_CONTEXT_LENGTH=16384/OLLAMA_CONTEXT_LENGTH=65536/' /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

- Hata: yedek `cp -n` ile alındı; aynı adda eski bir dosya olduğu için yeni yedek oluşmadı.
  Eski yedekte bağlam satırı yok, geri yükleme için kullanılmamalı.
- Sonuç: ✅ `ollama ps` → bağlam 65536, %100 GPU, 5795 MiB VRAM.

## 2026-11-25 — Adım 9.8: Ollama 0.40.16 → 0.40.18

- Neden: `ollama pull inkling-2-mini:26b-a5b-iq4_NL` → `412: The model you are attempting to pull requires a newer version of Ollama.`
- Arşiv (1.65 GB) `tmux` içinde indirildi, `sha256sum -c` → `OK`.
- Eski sürüm `/usr/local/ollama-backup-0.40.16` altına taşındı (2.4 GB), yenisi `/usr/local`'a açıldı, servis başlatıldı.
- Sonuç: ✅ `0.40.18`, `library=CUDA` (RTX A4000). `gemma4:e4b` yanıt verdi: %100 GPU, 5735 MiB VRAM. Open WebUI container'ı `healthy`.
- Inkling indirmesi kabul edildi ve başladı (17.6 GB, yaklaşık 4 MB/sn). NVIDIA'da çalışıp çalışmadığı henüz denenmedi:
  `0.40.17` notları "Apple silicon only" diyor, `0.40.18` notları bu konuda bir şey söylemiyor.

## 2026-11-25 — Kod asistanı denemesi: DeepSeek Harness + gemma4:e4b

- `dsh` `0.2.2-rc.5` (geliştirici önizlemesi). Windows'ta Web UI, ayrıca sunucuda geçici `node:24-bookworm` container'ında headless.

| Test (Web UI) | Sonuç |
|---|---|
| 1. Tek satırlık hata | Düzeltildi (kullanıcı bildirdi) |
| 2. İki dosyaya yayılan iki hata | Düzeltildi, test dosyasına dokunulmadı, kullanıcı `PASS` bildirdi |
| 3. Kurallardan yeni özellik yazma | Başarısız: proxy'siz 133/243; proxy ile ilk turda hiç araç çağrısı yok, uyarıdan sonra 238/243 ama kendi testleri geçmedi |

- Kök neden: model `description` yerine `justification` gönderiyor, `dsh` çağrıyı reddediyor. Argümanları onaran yerel proxy yazıldı.

| Container karşılaştırması (4'er çalıştırma) | Doğrudan | Proxy |
|---|---|---|
| Hata düzeltme: reddedilen/başarısız çağrı | 17 / 35 | 0 / 19 |
| Hata düzeltme: model testi çalıştırdı | 1 / 4 | 4 / 4 |
| Test 3: başarısız çağrı | 20 / 41 | 2 / 27 |
| Test 3: gizli kontrol (243 üzerinden) | 237, 238, 234, 137 | 236, 242, 243, 233 |
| Test 3: kendi testleri geçti | 1 / 4 | 2 / 4 |

- Proxy'li 4. test 3 çalıştırması 150 sn sınırına takıldı. Örnek sayısı az; gizli kontrol farkı kod kalitesi için kanıt sayılmaz.
- 243 kontrolün çoğu gidiş-dönüş denemesidir; yüzde yanıltıcıdır. Test 3'ü tam geçen çalıştırma olmadı.
- Sonuç: ⚠️ Küçük, gözetimli hata düzeltmede kullanılabilir. Kurallardan özellik yazmada güvenilir değil.

---

## Sıradaki adım

- Kapanan işler (2026-11-23, kullanıcı bildirdi): router'da MAC-IP rezervasyonu daha önce yapılmış.
  `eno2` 100 Mb/s: sınır Wi-Fi router'ın portunda, mevcut donanımla artırılamıyor.
- Karar (2026-11-23, kullanıcı): SSH şifre girişi açık kalacak, adımlardan çıkarıldı.
- Açık işler: kurulum sonunda `/etc/sudoers.d/90-setup-nopasswd` kaldırılacak.
- Açık işler (2026-11-25): Inkling'i A4000'de yükleyip ölçmek (VRAM, CPU/GPU paylaşımı, token/sn); Pi harness'ını iki modelle denemek.
  Sonra `/usr/local/ollama-backup-0.40.16`, `~/tmp/ollama18` ve kurulum betikleri silinecek.
