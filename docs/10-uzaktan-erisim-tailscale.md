# 10. (Opsiyonel) Ağ Dışından Uzaktan Erişim: Tailscale

> Durum: ⏸ Opsiyonel, henüz kurulmadı/test edilmedi. Kurulursa sonuçlar [LOG.md](../LOG.md)'ye işlenecek.

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

## Kurulum (planlanan)

Sunucuda:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh      # ekrana çıkan linki tarayıcıda açıp hesabınızla onaylayın
tailscale ip -4              # 100.x.y.z
tailscale status
```

İstemcide (Mac/Windows/telefon): Tailscale uygulamasını kurup aynı hesapla giriş yapın.

Bağlantı:

```bash
ssh kullanici@gpu-server         # MagicDNS ile
# veya
ssh kullanici@100.x.y.z
```

Önerilen ayarlar (Tailscale admin paneli):
- Sunucu için **Disable key expiry** (aksi halde 180 günde bir yeniden giriş gerekir).
- MagicDNS açık.

## Test kontrol listesi

- [ ] Yerel ağ dışından (örn. telefon hotspot) `ssh gpu-server` çalışıyor
- [ ] `tailscale status` doğrudan bağlantı gösteriyor (`direct`, `relay` değil)
- [ ] Yeniden başlatma sonrası Tailscale otomatik bağlanıyor (`systemctl is-enabled tailscaled`)

## Uzaktan açma (Wake on LAN) notu

WoL paketi yalnızca yerel ağda yayılır; internetten doğrudan gönderilemez. Ağ dışından açmak için
yerel ağda sürekli açık bir cihaz (Raspberry Pi, NAS, WoL destekli modem) gerekir: önce ona bağlanıp
oradan `wakeonlan <MAC>` gönderilir. Alternatif: sunucuyu sürekli açık tutmak
(BIOS: After Power Loss = Power On).
