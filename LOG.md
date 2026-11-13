# Kurulum Günlüğü

Her kayıt: tarih, adım, çalıştırılan komut, çıktı (kısaltılmış), hata varsa çözümü, sonuç.
Kişisel/ağ bilgileri (gerçek IP, kullanıcı adı, MAC, seri no) maskelenmiştir.

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

