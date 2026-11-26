# Ubuntu Server 24.04 + NVIDIA GPU: Lokal AI / YOLO / EgoBlur Sunucusu Kurulumu

[English](README.md) | **Türkçe**

Eski bir 3D tasarım iş istasyonunu, sıfırdan **Ubuntu Server 24.04.2 LTS** kurarak
GPU üzerinde lokal model (LLM, YOLO, EgoBlur vb.) çalıştıran bir sunucuya dönüştürme sürecinin
adım adım kaydıdır. Her komut, karşılaşılan hata, çözümü ve sonucu not edilmiştir.
Benzer bir sürece ihtiyaç duyan herkes kullanabilir.

## Donanım

| Bileşen | Değer |
|---|---|
| CPU | Intel Xeon W-2235 @ 3.80 GHz (6 çekirdek / 12 thread) |
| RAM | 32 GB |
| Disk | 480 GB SSD |
| GPU | NVIDIA RTX A4000 16 GB (Ampere, GA104) |
| OS | Ubuntu Server 24.04.2 LTS (amd64) |

## Yol Haritası

| # | Adım | Kim yapar | Durum |
|---|---|---|---|
| 1 | [ISO indirme ve Rufus ile USB hazırlama](docs/01-usb-hazirlama.md) | Kullanıcı (Windows) | ✅ Tamamlandı |
| 2 | [BIOS ayarları ve Ubuntu Server kurulumu](docs/02-ubuntu-kurulum.md) | Kullanıcı (fiziksel) | ✅ Tamamlandı |
| 3 | [Sabit IP atama (netplan)](docs/03-sabit-ip.md) | SSH üzerinden | ✅ Tamamlandı |
| 4 | [SSH servisi, anahtar ile uzaktan bağlantı](docs/04-ssh.md) | Kullanıcı | ✅ Tamamlandı |
| 5 | [Sistem güncelleme, temel paketler, disk genişletme](docs/05-temel-sistem.md) | SSH üzerinden | ✅ Tamamlandı |
| 6 | [NVIDIA sürücüsü](docs/06-nvidia-surucu.md) | SSH üzerinden | ✅ Tamamlandı |
| 7 | [Docker + NVIDIA Container Toolkit](docs/07-docker-nvidia.md) | SSH üzerinden | ✅ Tamamlandı |
| 8 | [Python ortamı, PyTorch, YOLO, EgoBlur](docs/08-pytorch-yolo-egoblur.md) | SSH üzerinden | ✅ |
| 9 | [Lokal LLM: Ollama + Open WebUI](docs/09-lokal-llm.md) | SSH üzerinden | ✅ Tamamlandı |
| 10 | [(Opsiyonel) Ağ dışından erişim: Tailscale](docs/10-uzaktan-erisim-tailscale.md) | SSH üzerinden + kullanıcı (hesap onayı) | ✅ Tamamlandı |

- Tüm çalıştırılan komutlar ve çıktıları: [LOG.md](LOG.md)
- Karşılaşılan sorunlar, doğrular/yanlışlar: [docs/sorunlar-ve-dersler.md](docs/sorunlar-ve-dersler.md)

## Kod asistanı testleri: Pi ve opencode

Sunucudaki üç yerel model (`gemma4:e4b`, `inkling-pi:32k`, `bonsai-pi:64k`), Windows PC'deki iki kod asistanıyla
([Pi](https://pi.dev) `1.6.0` ve [opencode](https://opencode.ai) `2.4.2`) aynı üç görevde denendi:
tek satırlık hata, iki dosyaya yayılmış hata ve kurallardan yeni özellik (3 çalıştırma).
Sonuçlar modelin sözüyle değil, `git diff` ve modelin görmediği kontrol betikleriyle değerlendirildi.

| Test 3: kurallardan yeni özellik (3 çalıştırma) | Pi | opencode |
|---|---|---|
| **inkling-pi:32k** | 243/243 ×3, ASCII kuralı 2/3 | 1. çalıştırma zaman aşımı (sıkıştırma ayarı), sonra 243/243 ×2, tam temiz |
| **bonsai-pi:64k** | 243/243 ×3, ASCII kuralı 0/3 | 243/243 ×3, ASCII kuralı 2/3, 2-4 kat yavaş |
| **gemma4:e4b** | 238/243 ×3, araç çağrısı kayboldu | 243, 241, 238; kendi testleri zayıf |

Test 1 ve 2'yi her harness'ta her model geçti (Pi'de Gemma test 1'de bir yardım mesajıyla).
Kısaca: kod yazmak için **Inkling**, uzun bağlam için **Bonsai**, hızlı ve gözetimli küçük düzeltmeler için **Gemma**.

- İstemler, başlangıç dosyaları, kontrol betikleri, tüm tablolar ve harness ayarları: [bench/](bench/README.tr.md)
- Komutlar ve ayrıntılar: [LOG.md](LOG.md)

## Bu repoyu kendi kurulumunuzda kullanırken

- Dokümanlarda geçen `192.168.1.50`, `gpu-server`, `kullanici` gibi değerler **örnektir**.
  Kendi ağınıza ve kullanıcı adınıza göre değiştirin.
- Arayüz adı (`eno1`, `enp0s31f6` vb.) donanıma göre değişir; `ip a` ile kendinizinkini bulun.

## Lisans

[MIT](LICENSE)
