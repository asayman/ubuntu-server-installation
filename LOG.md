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

## Sıradaki adım

- Adım 5: `apt full-upgrade`, saat dilimi, temel paketler ([docs/05](docs/05-temel-sistem.md)).
- Açık işler: router'da DHCP rezervasyonu (kullanıcı), kurulum sonunda
  `/etc/sudoers.d/90-setup-nopasswd` kaldırılacak, SSH şifre girişi kapatılacak.

