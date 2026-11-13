# 1. ISO İndirme ve Rufus ile Önyüklenebilir USB Hazırlama

Ortam: Windows PC, en az 4 GB (tercihen 8 GB+) USB bellek. **USB üzerindeki her şey silinir.**

## 1.1 ISO indirme

1. https://ubuntu.com/download/server sayfasına gidin.
2. Sayfadaki **Previous Releases** (önceki sürümler) bağlantısından **24.04.2** sürümünü seçin.
3. `ubuntu-24.04.2-live-server-amd64.iso` dosyasını indirin (~3 GB).

> Not: 24.04.2 yerine güncel 24.04.x point release de kullanılabilir; hepsi aynı LTS'dir.
> Kurulumdan sonra `apt full-upgrade` ile sistem zaten en güncel pakete çıkar.

## 1.2 (Önerilen) ISO bütünlüğünü doğrulama

Aynı dizindeki `SHA256SUMS` dosyasındaki değerle karşılaştırın. Windows PowerShell:

```powershell
Get-FileHash .\ubuntu-24.04.2-live-server-amd64.iso -Algorithm SHA256
# veya
certutil -hashfile .\ubuntu-24.04.2-live-server-amd64.iso SHA256
```

Hash eşleşmezse dosyayı tekrar indirin. Bozuk ISO, kurulumda rastgele "squashfs error" gibi
hatalara yol açar.

## 1.3 Rufus ile USB'ye yazma

1. https://rufus.ie adresinden Rufus'u indirip çalıştırın (portable sürüm yeterli).
2. Ayarlar:

| Alan | Değer |
|---|---|
| Device | USB belleğiniz (doğru diski seçtiğinizden emin olun) |
| Boot selection | `ubuntu-24.04.2-live-server-amd64.iso` (SELECT ile) |
| Partition scheme | **GPT** |
| Target system | **UEFI (non CSM)** |
| File system | FAT32 (varsayılan) |

3. **START**'a basın.
4. Rufus "ISOHybrid image detected" sorusunu sorar:
   - **Write in ISO Image mode (Recommended)** seçin.
   - Eğer USB'den boot ederken sorun yaşarsanız, işlemi tekrarlayıp **DD Image mode** seçin.
5. Rufus ek dosya (GRUB/syslinux) indirmek isterse **Yes** deyin.
6. "Status: READY" görünce USB hazırdır.

## Sonuç

- [x] ISO indirildi (Previous Releases → 24.04.2)
- [x] Rufus ile USB'ye yazıldı

Sonraki adım: [02 - BIOS ve Ubuntu kurulumu](02-ubuntu-kurulum.md)
