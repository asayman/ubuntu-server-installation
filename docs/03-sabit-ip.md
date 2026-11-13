# 3. Sabit IP Atama (netplan)

Sunucunun IP'si değişmemeli; aksi halde SSH bağlantısı her yeniden başlatmada kopabilir.
İki yol var:

- **A) Modem/router'da DHCP rezervasyonu:** MAC adresine sabit IP verilir. Sunucuda ayar gerekmez.
- **B) Sunucuda netplan ile statik IP** (bu dokümanda anlatılan). Seçilen IP, modemin
  DHCP havuzunun **dışında** olmalı; aksi halde IP çakışması olur.

## 3.1 Ağ bilgilerini toplama

```bash
ip -br a            # arayüz adı: örn. eno1
ip route            # "default via 192.168.1.1" → gateway
resolvectl status   # mevcut DNS sunucuları
```

Örnek değerler (kendi ağınıza göre değiştirin):

| Değer | Örnek |
|---|---|
| Arayüz | `eno1` |
| Sabit IP | `192.168.1.50/24` |
| Gateway | `192.168.1.1` |
| DNS | `1.1.1.1`, `8.8.8.8` |

## 3.2 cloud-init'in ağ ayarını ezmesini engelleme

Kurulum sonrası ağ ayarı `/etc/netplan/50-cloud-init.yaml` içindedir ve cloud-init tarafından
üretilir. cloud-init'in sonraki açılışlarda bu dosyayı yeniden yazmasını engelleyin:

```bash
echo 'network: {config: disabled}' | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
```

## 3.3 Netplan dosyası

Eski dosyayı yedekleyin ve yenisini yazın:

```bash
sudo mv /etc/netplan/50-cloud-init.yaml /root/50-cloud-init.yaml.bak
sudo nano /etc/netplan/01-static.yaml
```

İçerik (YAML'de **girinti boşluk ile** yapılır, Tab kullanmayın):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eno1:
      dhcp4: false
      dhcp6: false
      wakeonlan: true
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [1.1.1.1, 8.8.8.8]
```

Dosya izinleri (netplan 0644 izinli dosyalarda uyarı verir):

```bash
sudo chmod 600 /etc/netplan/01-static.yaml
```

`wakeonlan: true`: Wake on LAN için. BIOS'ta da Wake On LAN açık ve
S5 Maximum Power Savings kapalı olmalı (bkz. [02](02-ubuntu-kurulum.md)). Mac'ten uyandırma:
`brew install wakeonlan && wakeonlan <MAC_ADRESI>` (MAC adresi: `ip link show eno1`).

## 3.4 Uygulama

```bash
sudo netplan generate        # sözdizimi kontrolü, çıktı vermezse sorun yok
sudo netplan try             # 120 sn içinde Enter'a basılmazsa eski ayara döner (güvenli)
# Enter ile onaylayın
```

`netplan try` bağlantıyı koparırsa ayar otomatik geri alınır. Konsoldan çalıştığınız için risk düşüktür.

## 3.5 Doğrulama

```bash
ip -br a                   # eno1 ... 192.168.1.50/24
ip route                   # default via 192.168.1.1
ping -c 3 192.168.1.1      # gateway
ping -c 3 1.1.1.1          # internet
ping -c 3 ubuntu.com       # DNS
```

Hepsi cevap veriyorsa tamam. Bir kez `sudo reboot` yapıp IP'nin korunduğunu da kontrol edin.

## 3.6 (Alternatif) SSH üzerinden uzaktan uygulama

`netplan try` Enter onayı ister; etkileşimsiz SSH'ta çalışmaz. Uzaktan uygularken önce otomatik
geri alma zamanlayıcısı kurun, sonra uygulayın, yeni bağlantıyla doğrulayıp zamanlayıcıyı iptal edin:

```bash
sudo cp /etc/netplan/50-cloud-init.yaml /root/50-cloud-init.yaml.bak
# (yeni 01-static.yaml yazıldı, 50-cloud-init.yaml silindi, netplan generate OK)
sudo systemd-run --unit=netplan-rollback --on-active=180 /bin/sh -c \
  "rm -f /etc/netplan/01-static.yaml; cp /root/50-cloud-init.yaml.bak /etc/netplan/50-cloud-init.yaml; netplan apply"
sudo nohup netplan apply >/tmp/netplan-apply.log 2>&1 &
# birkaç saniye bekleyin, YENİ bir SSH bağlantısıyla doğrulayın:
ip route | head -1          # "proto static" görmelisiniz
sudo systemctl stop netplan-rollback.timer
```

Bu kurulumda kullanılan yöntem budur (bkz. [LOG.md](../LOG.md)).

## Sık hatalar

- `Error in network definition: ... expected mapping`: girinti hatası (Tab veya yanlış boşluk).
- `gateway4 has been deprecated`: eski rehberlerdeki `gateway4:` yerine `routes: - to: default` kullanın.
- `Permissions for /etc/netplan/... are too open`: `chmod 600` yapın.
- Arayüz adı yanlışsa ayar uygulanmaz; `ip -br a` çıktısındaki adı aynen yazın.
  Örn. HP Z4 G4'te iki port var (`eno1`, `eno2`); bu kurulumda kablo `eno2`'deydi.

Sonraki adım: [04 - SSH](04-ssh.md)
