# Ubuntu Server 24.04 + NVIDIA GPU: Lokal AI / YOLO / EgoBlur Sunucusu Kurulumu

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
| 7 | [Docker + NVIDIA Container Toolkit](docs/07-docker-nvidia.md) | SSH üzerinden | ⏳ |
| 8 | [Python ortamı, PyTorch, YOLO, EgoBlur](docs/08-pytorch-yolo-egoblur.md) | SSH üzerinden | ⏳ |
| 9 | [Lokal LLM (Ollama vb.)](docs/09-lokal-llm.md) | SSH üzerinden | ⏳ |
| 10 | [(Opsiyonel) Ağ dışından erişim: Tailscale](docs/10-uzaktan-erisim-tailscale.md) | SSH üzerinden | ⏸ Opsiyonel |

- Tüm çalıştırılan komutlar ve çıktıları: [LOG.md](LOG.md)
- Karşılaşılan sorunlar, doğrular/yanlışlar: [docs/sorunlar-ve-dersler.md](docs/sorunlar-ve-dersler.md)

## Bu repoyu kendi kurulumunuzda kullanırken

- Dokümanlarda geçen `192.168.1.50`, `gpu-server`, `kullanici` gibi değerler **örnektir**.
  Kendi ağınıza ve kullanıcı adınıza göre değiştirin.
- Arayüz adı (`eno1`, `enp0s31f6` vb.) donanıma göre değişir; `ip a` ile kendinizinkini bulun.

## Lisans

[MIT](LICENSE)
