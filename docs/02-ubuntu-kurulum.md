# 2. BIOS Ayarları ve Ubuntu Server 24.04.2 Kurulumu

Bu adım bilgisayarın başında (monitör + klavye) yapılır. Ethernet kablosu **takılı** olsun;
kurulum ağ ayarlarını ve paket aynalarını bu sırada yapılandırır.

## 2.1 BIOS / UEFI ayarları

W-2235 işlemcili iş istasyonları genelde Dell Precision 5820 / HP Z4 G4 / Lenovo P520 ailesidir.
BIOS'a giriş: Dell `F2`, HP `F10`, Lenovo `F1`. Boot menüsü: Dell `F12`, HP `F9`, Lenovo `F12`.

| Ayar | Önerilen | Neden |
|---|---|---|
| Boot mode | **UEFI** (Legacy/CSM kapalı) | Rufus'ta GPT + UEFI seçtik |
| **Secure Boot** | **Disabled** | NVIDIA sürücüsü Secure Boot açıkken MOK anahtar kaydı ister. Bu kayıt yeniden başlatmada **fiziksel ekranda** onay gerektirir; uzaktan (SSH) kurulumda takılır. Kapatmak işi basitleştirir. |
| SATA/Storage mode | **AHCI** (RAID/RST değil) | Ubuntu installer RST modunda diski görmeyebilir |
| AC Power Recovery | Power On / Last State (isteğe bağlı) | Elektrik kesintisinden sonra sunucu kendiliğinden açılsın |
| Wake on LAN | Enabled (isteğe bağlı) | Uzaktan açabilmek için |
| Primary display | PCIe / Auto | Monitör GPU'ya takılıysa |

> Secure Boot'u açık bırakmak isterseniz bkz. [sorunlar-ve-dersler.md](sorunlar-ve-dersler.md#secure-boot-ve-nvidia).

## 2.2 USB'den önyükleme

1. USB'yi takın, bilgisayarı açın, boot menüsü tuşuna basın.
2. `UEFI: <USB adı>` seçeneğini seçin (başında UEFI olmayanı seçmeyin).
3. GRUB menüsünde **Try or Install Ubuntu Server** seçin.

## 2.3 Kurulum ekranları (subiquity)

Klavye ile gezinme: `Tab`/ok tuşları, `Enter` seçer, `Space` kutucuk işaretler.

| Ekran | Seçim | Not |
|---|---|---|
| Language | **English** | Hata mesajlarını internette aramak kolaylaşır. |
| Installer update available | **Update to the new installer** | Ağ varsa önerilir. |
| Keyboard | Layout: **Turkish**, Variant: **Turkish** (Q klavye) | Bu ayar sadece fiziksel konsolu etkiler. |
| Type of installation | **Ubuntu Server** (minimized değil) | "Search for third-party drivers" kutusu **işaretlenmesin**: NVIDIA sürücüsünü SSH ile, kontrollü ve loglayarak kuracağız. |
| Network | Ethernet DHCP ile IP alsın (varsayılan) | Sabit IP'yi kurulum sonrası netplan ile vereceğiz (bkz. 03). İsterseniz burada `Edit IPv4 → Manual` ile de verebilirsiniz. |
| Proxy | Boş | |
| Mirror | Varsayılan (`tr.archive.ubuntu.com` olabilir) | Mirror testi geçmeli. |
| Storage | **Use an entire disk** + **Set up this disk as an LVM group** | Aşağıdaki **önemli** nota bakın. |
| Profile | Your name, Server name: `gpu-server`, Username, Password | Kullanıcı adını ve şifreyi not edin. |
| Upgrade to Ubuntu Pro | **Skip for now** | Sonradan bağlanabilir. |
| SSH configuration | **[X] Install OpenSSH server** | Zorunlu. "Import SSH key" ile GitHub kullanıcı adınızdan public key çekebilirsiniz (isteğe bağlı). "Allow password authentication over SSH" şimdilik açık kalsın. |
| Featured server snaps | **Hiçbirini seçmeyin** | Docker'ı snap yerine resmi apt deposundan kuracağız (NVIDIA toolkit ile uyum için). |

### ÖNEMLİ: LVM varsayılan olarak diskin tamamını kullanmaz

Storage özet ekranında `ubuntu-lv` mantıksal birimi **diskin tamamı değil, yaklaşık 100 GB**
olarak oluşturulur. Geri kalan alan volume group içinde boş kalır. 480 GB diskte bu, modeller ve
veri setleri için ciddi alan kaybıdır.

**Kurulum sırasında düzeltme:** Storage configuration ekranında
`USED DEVICES` altında `ubuntu-lv` satırına gelin → `Edit` → **Size** alanına maksimum değeri
yazın (alanın yanında max değer gösterilir) → `Save`.

**Kurulumdan sonra düzeltme** (atlandıysa, SSH aşamasında yapılacak):

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
df -h /
```

## 2.4 Kurulum sonu

1. "Installation complete!" görünce **Reboot Now**.
2. "Please remove the installation medium, then press ENTER" mesajında USB'yi çıkarıp `Enter`.
3. Açılışta cloud-init mesajları akabilir; login ekranı gelene kadar bekleyin, sonra `Enter`.
4. Kullanıcı adı ve şifre ile giriş yapın.

## 2.5 İlk kontroller (konsolda)

```bash
lsb_release -a          # Ubuntu 24.04.x LTS görünmeli
ip -br a                # Ağ arayüz adı ve DHCP IP'si (örn. eno1  UP  192.168.1.123/24)
lspci | grep -i nvidia  # RTX A4000 görünmeli
df -h /                 # Kök dizin boyutu (LVM notunu kontrol edin)
```

Bu çıktıların ekran görüntüsünü / notunu alın; `LOG.md`'ye işlenecek.

Sonraki adım: [03 - Sabit IP](03-sabit-ip.md)
