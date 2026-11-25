# 9. Lokal LLM: Ollama + Open WebUI

> Durum: ✅ Tamamlandı (2026-11-23; Ollama yükseltmesi ve 64K bağlam 2026-11-25). Ollama `0.40.18`, `gemma4:e4b` (Q4_K_M), Open WebUI `0.13.3`.
> Komutlar ve çıktılar [LOG.md](../LOG.md)'de. Örnek ağ: `192.168.1.0/24`; kendi ağınıza göre değiştirin.

## 9.1 Ollama indirme

Yavaş hatta indirme yarıda kalabilir. Dosya devam ettirilebilir biçimde indirilir ve sha256 ile doğrulanır:

```bash
V=v0.40.18
U=https://github.com/ollama/ollama/releases/download/$V
mkdir -p ~/tmp/ollama && cd ~/tmp/ollama
until curl -fL -C - --speed-limit 10000 --speed-time 60 -O $U/ollama-linux-amd64.tar.zst; do sleep 10; done
curl -fsSL -o sha256sum.txt $U/sha256sum.txt
grep "ollama-linux-amd64.tar.zst$" sha256sum.txt | sed "s|\./||" | sha256sum -c -
```

## 9.2 Güvenlik duvarı (UFW)

Ollama API'sinde kimlik doğrulama yoktur. Yalnız yerel ağa açın. UFW'yi açmadan önce SSH iznini ekleyin:

```bash
sudo ufw allow OpenSSH
sudo ufw allow from 192.168.1.0/24 to any port 11434 proto tcp comment "ollama LAN"
# emniyet: SSH koparsa UFW 180 sn sonra kapanır
sudo systemd-run --on-active=180 --unit=ufw-failsafe ufw disable
sudo ufw enable
# YENİ bir terminalden SSH girişini deneyin; çalışıyorsa:
sudo systemctl stop ufw-failsafe.timer
```

## 9.3 Ollama kurulumu ve systemd servisi

```bash
zstd -dc ~/tmp/ollama/ollama-linux-amd64.tar.zst | sudo tar -xf - -C /usr/local
sudo useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama
sudo usermod -aG render,video ollama
sudo usermod -aG ollama "$(whoami)"
```

`/etc/systemd/system/ollama.service`:

```ini
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=default.target
```

`/etc/systemd/system/ollama.service.d/override.conf`:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_CONTEXT_LENGTH=65536"
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ollama
sudo journalctl -u ollama | grep "inference compute"   # library=CUDA görünmeli
```

## 9.4 Model

Normal hatta `ollama pull gemma4:e4b` yeterlidir. Yavaş hatta takılırsa büyük blob tek bağlantıyla indirilir:

```bash
D=370c2879f17648d337b0ab4e208fdce348e24d1060064e93d7645daafd56d39c
F=~/tmp/ollama/sha256-$D
until curl -sSfL -C - --speed-limit 10000 --speed-time 60 -o "$F" \
  "https://registry.ollama.ai/v2/library/gemma4/blobs/sha256:$D"; do sleep 30; done
echo "$D  $F" | sha256sum -c -
sudo install -o ollama -g ollama -m 644 "$F" /usr/share/ollama/.ollama/models/blobs/sha256-$D && rm "$F"
ollama pull gemma4:e4b     # kalan küçük katmanlar
```

Digest modelin sürümüne aittir; sonraki sürümlerde değişebilir.

Ölçüm (RTX A4000, kısa Türkçe soru, `think=false`, bağlam 4096, 2 çalıştırma): **110-118 token/sn**, %100 GPU, 4.7 GB VRAM.
İlk yükleme 65 sn, model bellekteyken anında.

### Bağlam uzunluğu

Varsayılan bağlam (4096) uzun sohbette çabuk dolar. Yukarıdaki `override.conf` 64K kullanır. Modelin sınırı 131072.

Ölçüm (2026-11-25, Ollama `0.40.16`, bağlamın yaklaşık %80'i dolu, boyut başına tek çalıştırma):

| Bağlam | İstem (token) | VRAM | İstemi okuma | Üretim |
|---|---|---|---|---|
| 16384 | 12935 | 5159 MiB | 2.4 sn | 167 token/sn |
| 32768 | 26344 | 5479 MiB | 4.9 sn | 153 token/sn |
| **65536** | 53789 | 5833 MiB | 11.8 sn | 130 token/sn |
| 131072 | 108669 | 6969 MiB | 31.3 sn | 99 token/sn |

Her boyutta istemin başlarına gizlenen kod bulundu. Bu basit bir testtir; uzun bağlamda akıl yürütme kalitesini göstermez.

Değiştirmek için:

```bash
F=/etc/systemd/system/ollama.service.d/override.conf
sudo cp $F ~/ollama-override.conf.$(date +%F-%H%M%S).bak
sudo sed -i 's/OLLAMA_CONTEXT_LENGTH=.*"/OLLAMA_CONTEXT_LENGTH=65536"/' $F
sudo systemctl daemon-reload && sudo systemctl restart ollama
systemctl show ollama -p Environment
```

Ayar sunucunun varsayılanıdır. İstemci tarafındaki bağlam ayarı (ör. kod asistanının `contextWindow` değeri) bunu aşmamalı.

### Ollama'yı yükseltme

Yeni modeller daha yeni Ollama isteyebilir (`412` hatası). Yeni arşivi 9.1'deki gibi ayrı bir klasöre indirip doğrulayın,
eskisini silmeden kenara taşıyın. Yeniden başlatma süren yanıtları keser.

```bash
B=/usr/local/ollama-backup-0.40.16       # eski sürüm
sudo systemctl stop ollama
sudo mkdir $B
sudo mv /usr/local/bin/ollama $B/ollama
sudo mv /usr/local/lib/ollama $B/lib-ollama
zstd -dc ~/tmp/ollama18/ollama-linux-amd64.tar.zst | sudo tar -xf - -C /usr/local
sudo systemctl start ollama
ollama --version && ollama list
sudo journalctl -u ollama --since "-2 min" | grep "inference compute"   # library=CUDA görünmeli
```

Geri dönüş (denenmedi): servisi durdurun, yeni `bin/ollama` ve `lib/ollama`'yı kaldırın, `$B` içindekileri geri taşıyın, servisi başlatın.
Yedek 2.4 GB yer tutar; yeni sürümden emin olunca silin.

## 9.5 Open WebUI

Docker'ın `-p` ile yayımladığı portlar UFW kurallarını atlar. Bu yüzden `--network=host` kullanılır:

```bash
docker run -d --name open-webui --network=host \
  -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
  -e RAG_EMBEDDING_MODEL_AUTO_UPDATE=false \
  -v open-webui:/app/backend/data \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
sudo ufw allow from 192.168.1.0/24 to any port 8080 proto tcp comment "open-webui LAN"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/health    # 200
```

- `http://<sunucu-ip>:8080` adresini açın. **İlk kayıt olan hesap yönetici olur**; hesabı hemen oluşturun.
- Veriler `open-webui` volume'undadır. Container silinip yeniden kurulsa da kalır.
