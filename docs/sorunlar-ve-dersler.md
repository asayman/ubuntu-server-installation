# Sorunlar, Çözümler, Doğrular / Yanlışlar

Kurulum boyunca karşılaşılan her sorun buraya eklenir. Format:
**Belirti → Neden → Çözüm → Sonuç.**

## Bilinen tuzaklar (kuruluma başlamadan önce)

### LVM kök birimi ~100 GB oluşturuluyor
- **Belirti:** 480 GB diske kurulum sonrası `df -h /` ~98 GB gösterir.
- **Neden:** Ubuntu installer `ubuntu-lv`'yi volume group'un tamamı kadar oluşturmaz.
- **Çözüm:** Kurulumda `ubuntu-lv → Edit → Size: max`. Ya da sonradan
  `lvextend -l +100%FREE` + `resize2fs`. Bkz. [02](02-ubuntu-kurulum.md).

### Secure Boot ve NVIDIA
- **Belirti:** Sürücü kurulduktan sonra `nvidia-smi` → `NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver`.
  `mokutil --sb-state` → `SecureBoot enabled`.
- **Neden:** DKMS ile derlenen modül imzasız; Secure Boot yüklemeyi reddeder. MOK kaydı açılışta
  mavi "Perform MOK management" ekranında fiziksel onay ister.
- **Çözüm:** BIOS'ta Secure Boot'u kapatmak (bu repoda tercih edilen). Alternatif: Ubuntu'nun
  önceden imzalı `linux-modules-nvidia-*` paketlerini kullanmak veya MOK kaydını konsoldan yapmak.

### Docker'ı snap olarak kurmak
- **Yanlış:** Kurulumdaki "Featured server snaps" ekranından `docker` seçmek.
- **Neden:** Snap Docker, NVIDIA Container Toolkit yapılandırmasıyla sorun çıkarır.
- **Doğru:** Docker'ı resmi `download.docker.com` apt deposundan kurmak.

### netplan `gateway4`
- **Yanlış:** Eski rehberlerdeki `gateway4: 192.168.1.1`.
- **Doğru:** `routes: [{to: default, via: 192.168.1.1}]`.

### `ssh.service` inactive görünmesi
- **Belirti:** `systemctl status ssh` → inactive (dead), ama bağlantı çalışıyor.
- **Neden:** 24.04'te socket activation (`ssh.socket`).
- **Sonuç:** Sorun değil.

## Kurulum sırasında yaşananlar

### Custom storage layout ekranında takılmak
- **Belirti:** "To continue you need to: Mount a filesystem at / / Select a boot disk".
  Disk eski Windows bölümleriyle (ESP, MSR, NTFS) listeleniyor.
- **Neden:** "Custom storage layout" her şeyin elle yapılmasını ister (boot disk, /boot, VG, LV, `/`).
- **Doğru:** `Back` → **Use an entire disk** → hedef disk (USB değil!) → **Set up this disk as an LVM group**
  → özet ekranında `ubuntu-lv` → Edit → Size: max.
- **Yanlış:** Kurulum USB'sini (Kingston vb.) hedef disk seçmek.

### Uzaktan `netplan apply` sonrası SSH zaman aşımı
- **Belirti:** `ssh: connect to host 192.168.68.118 port 22: Operation timed out`
- **Neden:** DHCP → statik geçişinde arayüz birkaç saniye yeniden yapılandırılıyor.
- **Çözüm:** Birkaç saniye bekleyip yeniden bağlanmak. Önlem olarak `systemd-run --on-active=180`
  ile otomatik geri alma zamanlayıcısı kurmak (bkz. [03](03-sabit-ip.md#36-alternatif-ssh-üzerinden-uzaktan-uygulama)).
- **Sonuç:** IP aynı kaldığı için ikinci denemede bağlantı geldi.

### Yanlış arayüz adı
- **Yanlış:** Dokümandaki örneği (`eno1`) olduğu gibi kullanmak.
- **Doğru:** `ip -br a` ile `UP` olan arayüzü bulmak. HP Z4 G4'te kablo `eno2`'deydi, `eno1` DOWN.


## NVIDIA sürücüsü

### `ubuntu-drivers install --gpgpu` sonrası `nvidia-smi` yok
- **Belirti:** Sürücü kuruldu ama `nvidia-smi: command not found`.
- **Neden:** `--gpgpu` sadece `nvidia-headless-no-dkms-XXX` ve hazır kernel modülünü kurar.
- **Çözüm:** `sudo apt install nvidia-utils-XXX-server` (aynı sürüm numarası).

### Persistence mode kapalı geliyor
- **Belirti:** `nvidia-persistenced` aktif ama `nvidia-smi -q` → `Persistence Mode: Disabled`.
- **Neden:** Ubuntu paketi servisi `--no-persistence-mode` ile başlatıyor.
- **Çözüm:** systemd override ile `--persistence-mode` (bkz. [06](06-nvidia-surucu.md#63-persistence-mode)).
- **Yanlış:** `/lib/systemd/system/nvidia-persistenced.service` dosyasını doğrudan düzenlemek.
  Paket güncellemesinde değişiklik silinir.

### "recommended" sürücü masaüstü varyantı
- `ubuntu-drivers devices` masaüstü için `nvidia-driver-XXX-open` önerir.
- Ekransız sunucuda `--gpgpu` + `-server-open` kullanın. Masaüstü grafik paketleri gelmez.

## Docker

### `usermod -G` ile sudo yetkisini kaybetmek
- **Yanlış:** `sudo usermod -G docker $USER`. Kullanıcı diğer gruplarından (`sudo` dahil) çıkarılır.
- **Doğru:** `sudo usermod -aG docker $USER` (`-a` = append).
- Grup üyeliği yeni oturumda geçerli olur. Yeni SSH bağlantısı açın.

### Container içinde CUDA sürümü
- Container imajının CUDA sürümü sunucudaki sürücünün desteklediği en yüksek sürümü
  (`nvidia-smi` → `CUDA Version`) aşmamalı. Aşarsa container `CUDA driver version is insufficient` hatası verir.

## Python / uv

### Yavaş internette `uv pip install` zaman aşımı
- **Belirti:** `error: Failed to download ... cause: operation timed out` (PyTorch CUDA paketleri, `pypi.nvidia.com`).
- **Neden:** `uv` çok sayıda dosyayı paralel indirir; varsayılan HTTP timeout 30 sn.
- **Çözüm:** `export UV_HTTP_TIMEOUT=300 UV_CONCURRENT_DOWNLOADS=2` ve komutu tekrar deneyen bir döngü.
  Uzun kurulumları `tmux` içinde çalıştırın; SSH koparsa kurulum durmaz.

### `import ultralytics` → `libGL.so.1` hatası
- **Belirti:** `ImportError: libGL.so.1: cannot open shared object file: No such file or directory` (`cv2` import sırasında).
- **Neden:** `ultralytics` normal `opencv-python` paketini kurar. Bu paket grafik kütüphanesi `libGL` ister.
  Ekransız Ubuntu Server'da `libGL` kurulu gelmez.
- **Çözüm:** `sudo apt-get install -y --no-install-recommends libgl1`.
- **Alternatif:** `opencv-python-headless`. Ama `ultralytics` güncellenince normal opencv geri gelebilir.

## EgoBlur

### `egoblur` paketi torch'u eski sürüme indiriyor
- **Belirti:** `uv pip install egoblur==2.0.1` mevcut torch 2.14.1 yerine `torch==2.9.1` kurar (büyük indirme).
- **Çözüm:** `uv pip install --no-deps egoblur==2.0.1`, sonra gerekli paketleri elle kurun
  (`moviepy==1.0.3 opencv-python-headless numpy av vrs tqdm ...`). Modeller torch 2.14.1 ile çalıştı.

### gen2 `.jit` modelinde `m.eval()` hatası
- **Belirti:** gen1 için yazılmış kod gen2 modelini yüklerken `m.eval()` satırında `RuntimeError` verir.
- **Neden:** gen2 `.jit` dosyası "frozen" TorchScript. Zaten eval modunda, `training` bir sabit.
- **Çözüm:** `m.eval()` çağrısını `try/except RuntimeError` içine alın.

### gen2 modeli tensor kabul etmiyor
- **Belirti:** `RuntimeError: forward() Expected a value of type 'List[Dict[str, Tensor]]' for argument 'batched_inputs' but instead found type 'Tensor'.`
- **Neden:** gen2 bir detectron2 modeli. Girdi listesi bekler, gen1 gibi düz tensor değil.
- **Çözüm:** paketin kendi sınıfını kullanın: `gen2.script.predictor.EgoblurDetector`.
  Çağrıyı `with patch_instances(fields=PATCH_INSTANCES_FIELDS):` içinde yapın (resmi demo gibi).
- **Not:** `EgoblurDetector` görüntüyü 1200 piksele küçültür. gen1 ile kutu sayısı karşılaştırması yaparken bunu hesaba katın.

## Ollama / Open WebUI

### `ollama pull` yavaş internette takılıyor
- **Neden:** büyük blob'u 16 paralel bağlantıyla indirir. Bunu değiştiren belgelenmiş bir ayar bulunamadı.
- **Çözüm:** blob'u `registry.ollama.ai/v2/library/<model>/blobs/sha256:<digest>` adresinden tek bağlantıyla indirin,
  sha256 doğrulayın, `blobs` klasörüne koyun, sonra `ollama pull` çalıştırın ([docs/09](09-lokal-llm.md)).

### `curl --retry` ile `-C -` birlikte baştan başladı
- **Belirti:** tekrar denemede 6.4 MB'lık dosya 24 KB'a düştü.
- **Çözüm:** `--retry` kullanmayın; `until curl -C - ...; do sleep 30; done` döngüsü kurun.

### `pkill -f` kendi SSH komutunu öldürdü
- **Neden:** `ssh sunucu 'pkill -f "ollama pull"'` içindeki metin, uzak kabuğun kendi komut satırıyla da eşleşir.
- **Çözüm:** `pkill -f "[o]llama pull"`.

### Docker `-p` portları UFW'yi atlar
- **Çözüm:** yalnız yerel ağa açılacak servisi `--network=host` ile çalıştırıp UFW kuralı yazın.

### Open WebUI ilk açılışta dakikalarca `unhealthy`
- **Neden:** embedding modelinin tüm ONNX/OpenVINO kopyalarını HuggingFace'ten indirir; indirme bitmeden port açılmaz.
- **Çözüm:** `-e RAG_EMBEDDING_MODEL_AUTO_UPDATE=false`. Gerekli model imajın içinde gelir; açılış 21 sn'ye indi.

### `ollama pull`: `412 ... requires a newer version of Ollama`
- **Çözüm:** Ollama'yı yükseltin ([docs/09](09-lokal-llm.md)). Önce sürüm notlarını okuyun: model yalnız belirli donanımı destekliyor olabilir.

### `cp -n` ile alınan yedek eski dosyaydı
- **Belirti:** yedekle yeni dosyanın `diff`'i, değişen satırı "eklenmiş" gösterdi.
- **Neden:** aynı adda eski bir yedek vardı; `cp -n` üzerine yazmaz ve dosyayı atlar.
- **Çözüm:** yedek adına tarih ekleyin, değişiklikten önce yedeği `diff` ile doğrulayın.

## Kod asistanı (Pi) ve yerel modeller

Pi `1.6.0` ile `gemma4:e4b` ve `inkling-pi:32k` denemelerinde görülenler. Ayrıntı: [LOG.md](../LOG.md).

### Pi sessizce duruyor, dosya değişmemiş
- **Belirti:** model düzenleyeceğini söylüyor, sonra Pi hata göstermeden yeni girdi bekliyor.
- **Neden:** Gemma'nın `edit` çağrısı bozuk biçimdeydi; Ollama çağrıyı ayrıştıramadı, Pi'ye hiç araç çağrısı ulaşmadı.
- **Kontrol:** `sudo journalctl -u ollama | grep "tool call parsing failed"`
- **Çözüm:** çağrının bozuk olduğunu ve dosyanın değişmediğini yazıp devam etmesini istemek bir denemede, yalnız `continue.` yazmak iki denemede yetti. Gemma'da 5 çalıştırmanın 3'ünde görüldü, Inkling'de görülmedi.

### Model "bitti" diyor ama testler geçmemiş
- **Neden:** Gemma'nın testi hataları yakalayıp yalnız `FAIL` yazdırıyordu; betik yine de başarıyla bitiyordu.
- **Çözüm:** modelin sözüne değil `git diff`'e ve kendi çalıştırdığınız teste bakın. Her denemeden önce commit alın.
  Çıkış kodu tek başına yetmez; çıktıda `FAIL` satırı olmadığını da kontrol edin.

### Modelin kendi testleri yeterli değil
- **Belirti:** 8 kasıtlı hatanın hepsini yakalayan testler bile koddaki gerçek hataları (ASCII dışı rakam, `-5m`) kaçırdı.
  Bir denemede Gemma, kodu düzeltmek yerine başarısız olan doğru testi değiştirdi.
- **Çözüm:** çalışma klasörü dışında tutulan, modelin görmediği ayrı bir kontrol betiği kullanın. O betiğin de eksikleri olabilir:
  bizimki `PASS: ...` satırlarına aldanıp test gücünü yanlış ölçtü. Son satırın tam `PASS` olmasını ve `FAIL` geçmemesini arayın.

### Büyük model GPU'ya hiç katman koymuyor
- **Belirti:** Inkling varsayılan ayarda 6.5 token/sn, günlükte `offloaded 0/49 layers to GPU`.
- **Neden:** bağlam 64K ve batch 512 iken 13.8 GB'lık hesap tamponu VRAM'i dolduruyor.
- **Çözüm:** `num_ctx 32768` ve `num_batch 128` ile türetilmiş model: 49/49 katman, 30.4 token/sn.

### Pi'de komut onayı ve sandbox yok
- **Dikkat:** modelin komutları kullanıcının tüm yetkileriyle, sorulmadan çalışır.
- **Çözüm:** Pi'yi yalnız deneme klasöründe, gözetim altında ya da container içinde çalıştırın.

### Windows'ta satır sonları değişiyor
- **Belirti:** tek satırlık düzeltmede `git diff` bütün dosyayı değişmiş gösteriyor.
- **Neden:** model dosyayı Windows'ta Python'un metin kipiyle yazınca LF, CRLF'ye dönüyor.
- **Çözüm:** `git diff --ignore-space-at-eol` ile bakın.

## Kod asistanı (opencode) ve yerel modeller

opencode `2.4.2` ile aynı testlerde görülenler. Ayrıntı: [LOG.md](../LOG.md), [bench/](../bench/README.md).

### Küçük bağlamda model sürekli sıkıştırıp ilerlemiyor
- **Belirti:** 32K bağlamlı Inkling, ~16.7K token'da sıkıştırıyor, dosyaları unutup dakikalarca baştan düşünüyor, birkaç dakika sonra yine sıkıştırıyor.
- **Neden:** `compaction.buffer` varsayılanı en az 16K token boş alan bırakıyor; sıkıştırmadan sonra da ~15K token (`keep.tokens`) korunuyor.
  Çıktı sınırını düşürmek bunu değiştirmiyor.
- **Çözüm:** `"compaction": { "buffer": 6144, "keep": { "tokens": 4000 } }`, ardından `opencode reload`. Sonra iki çalıştırma hiç sıkıştırmadan bitti.

### opencode kendiliğinden güncellendi, komutlar değişti
- **Belirti:** `opencode -m ...` → `Unrecognized flag: -m`; `opencode models ollama` → `Unexpected positional argument`.
- **Neden:** ilk açılışta `1.19.6`'dan `2.4.2`'ye güncellendi; `2.x` arka planda bir servis kullanıyor ve model TUI içinde seçiliyor.
- **Çözüm:** karşılaştırmalı testlerde sürümü her oturumda kaydedin (`opencode --version`, veritabanında `session_v2.version`). Ayar değişince `opencode reload`.

### Model dosyaları sormadan siliyor
- **Dikkat:** varsayılan ayarda opencode da komutları sormadan çalıştırıyor; Inkling bir denemede `Remove-Item` ile dosya sildi.
- **Çözüm:** yalnız deneme klasöründe ve gözetim altında çalıştırın; her denemeden önce commit alın.
