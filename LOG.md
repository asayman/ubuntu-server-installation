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

## Adım 2: Ubuntu kurulumu

_(Kullanıcı tarafından yapılacak. Not: installer ekranında yapılan seçimler, `df -h /`, `ip -br a`,
`lspci | grep -i nvidia` çıktıları buraya eklenecek.)_
