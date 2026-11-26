# 10. (Opsiyonel) Ağ Dışından Uzaktan Erişim: Tailscale

> Durum: ✅ Kuruldu ve test edildi (Tailscale 1.104.7). LAN içi, ağ dışı (hotspot) ve yeniden başlatma testleri geçti.
> Ayrıntılar: [LOG.md](../LOG.md).

## Neden Tailscale

- WireGuard tabanlı mesh VPN. Modemde **port açmak gerekmez**.
- **CGNAT** arkasında da çalışır (Türkiye'de birçok ev internet hattı CGNAT'tır).
- Sunucu sabit bir `100.x.y.z` IP ve `gpu-server` adı alır; her yerden aynı adresle erişilir.
- SSH, Ollama API, Jupyter gibi servisler internete açılmadan yalnızca kendi cihazlarınızdan erişilir.
- Kişisel kullanım ücretsiz. Koordinasyon sunucusu Tailscale'dedir; trafik uçtan uca şifrelidir.
  Tam bağımsızlık istenirse self-hosted **Headscale** kullanılabilir.

## Alternatifler (kısa karşılaştırma)

| Yöntem | Port açma | CGNAT'ta çalışır | Not |
|---|---|---|---|
| Tailscale | Gerekmez | Evet | En kolay |
| Kendi WireGuard sunucusu | Gerekir (UDP) | Hayır | Public IP + DDNS gerekir |
| Cloudflare Tunnel | Gerekmez | Evet | Web (HTTP) servisleri için ideal, domain gerekir |
| VPS üzerinden ters SSH tüneli (`autossh -R`) | Gerekmez | Evet | Bakımı size ait, ek gecikme |
| Modemde 22. portu açmak | Gerekir | Hayır | **Önerilmez**: bot saldırıları |

CGNAT kontrolü: modem arayüzündeki WAN IP ile https://ifconfig.me sonucunu karşılaştırın.
Farklıysa CGNAT vardır.

## Kurulum

Önce https://login.tailscale.com adresinden ücretsiz hesap açın (Google/Microsoft/GitHub ile giriş).

Sunucuda (SSH üzerinden):

```bash
curl -fsSL https://tailscale.com/install.sh | sh   # apt deposunu ekler, paketi kurar, tailscaled'i açar
tailscale version
systemctl is-enabled tailscaled                    # enabled
sudo tailscale up --hostname=gpu-server
# To authenticate, visit:
#     https://login.tailscale.com/a/<kod>
```

Ekrana çıkan linki tarayıcıda açıp hesabınızla cihazı onaylayın. Onaydan sonra komut `Success.` yazar.
SSH oturumu kapanırsa `tailscale up` da kapanır; uzun süre beklenecekse arka planda çalıştırın:
`sudo nohup tailscale up --hostname=gpu-server > /tmp/ts-up.log 2>&1 &` ve linki `cat /tmp/ts-up.log` ile okuyun.

```bash
tailscale ip -4     # 100.x.y.z
tailscale status    # gpu-server ve diğer cihazlarınız listelenir
```

İstemcide (Windows/Mac/telefon): https://tailscale.com/download adresinden uygulamayı kurup **aynı hesapla**
giriş yapın.

### `--ssh` kullanmadık

`tailscale up --ssh`, sunucudaki OpenSSH yerine **Tailscale SSH**'ı devreye alır: kimlik doğrulama SSH anahtarı
yerine Tailscale hesabı ve ACL ile yapılır. Burada mevcut anahtar tabanlı OpenSSH korunmak istendiği için
`--ssh` eklenmedi; Tailscale yalnızca ağ katmanı olarak kullanılıyor.

## Bağlantı

```bash
ssh -i ~/.ssh/<anahtar> kullanici@gpu-server     # MagicDNS (kısa ad)
ssh -i ~/.ssh/<anahtar> kullanici@100.x.y.z      # Tailscale IP
# Tam ad: gpu-server.<tailnet>.ts.net
```

İlk bağlantıda yeni ad/IP için host key sorulur. Kabul etmeden önce parmak izinin LAN üzerinden bilinen
anahtarla aynı olduğunu doğrulayın:

```bash
ssh-keyscan -t ed25519 gpu-server 2>/dev/null | ssh-keygen -lf -
# SHA256:... LAN IP için gördüğünüz parmak iziyle aynı olmalı
```

Ollama API de tailnet üzerinden erişilebilir: `curl http://gpu-server:11434/api/version`.

### Güvenlik duvarı notu (UFW)

UFW'de Ollama (11434) ve Open WebUI (8080) yalnızca `192.168.68.0/24`'e açık olsa bile tailnet'ten
erişilebilir. Sebep: `tailscaled`, iptables'a kendi `ts-input` zincirini ekler ve `tailscale0` arayüzünden
gelen trafiği UFW kurallarından önce kabul eder. Yani **tailnet'teki her cihaz sunucudaki tüm portlara
erişebilir**. Kişisel tailnet için sorun değildir; cihaz paylaşacaksanız Tailscale admin panelinden
ACL ile kısıtlayın. İnternete herhangi bir port açılmaz.

## Önerilen ayarlar (Tailscale admin paneli)

- Machines → gpu-server → **Disable key expiry**. Doğrulama: `tailscale status --json` çıktısında `Self` altında
  `KeyExpiry` alanı olmamalı (`Peer` altındaki tarihler diğer cihazlarındır). Aksi halde anahtar 180 gün sonra düşer ve sunucuda
  yeniden `tailscale up` gerekir (fiziksel/LAN erişimi olmadan bu yapılamaz).
- MagicDNS açık (yeni hesaplarda varsayılan olarak açık).

## Test kontrol listesi

- [x] `tailscale status` her iki cihazı gösteriyor (sunucu + Windows)
- [x] `tailscale ping gpu-server` → `pong ... via <LAN-IP>:41641`, `status` → `active; direct` (relay değil)
- [x] `ssh kullanici@gpu-server` (MagicDNS) ve `ssh kullanici@100.x.y.z` çalışıyor
- [x] Host key parmak izi LAN'daki ile aynı
- [x] Ollama API tailnet üzerinden yanıt veriyor
- [x] `systemctl is-enabled tailscaled` → `enabled`
- [x] Yerel ağ dışından (telefon hotspot) `ssh gpu-server` ve Ollama API çalışıyor; bağlantı yine `direct`
      (`<ev-public-IP>:41641` üzerinden, yani hat CGNAT değil)
- [x] Yeniden başlatma sonrası Tailscale otomatik bağlanıyor (SSH ~45 sn'de geri geldi)
- [x] Admin panelinde key expiry kapatıldı (`tailscale status --json` → `Self` altında `KeyExpiry` yok)

## Uzaktan açma (Wake on LAN) notu

WoL paketi yalnızca yerel ağda yayılır; internetten doğrudan gönderilemez. Ağ dışından açmak için
yerel ağda sürekli açık bir cihaz (Raspberry Pi, NAS, WoL destekli modem) gerekir: önce ona bağlanıp
oradan `wakeonlan <MAC>` gönderilir. Alternatif: sunucuyu sürekli açık tutmak
(BIOS: After Power Loss = Power On).
