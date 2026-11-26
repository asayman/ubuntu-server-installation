# Kod asistanı testleri: Pi ve opencode, üç yerel model

Sunucudaki Ollama'da çalışan üç modelin, Windows PC'deki iki kod asistanıyla (harness) aynı üç görevi nasıl yaptığının kaydı.
Testleri kullanıcı elle çalıştırdı; sonuçlar modelin sözüne göre değil, `git diff` ve aşağıdaki kontrol betikleriyle değerlendirildi.

- Tarihler: Pi 2026-11-25, opencode 2026-11-26. Komutlar ve ayrıntılar: [LOG.md](../LOG.md).
- Bu klasör: [istemler](prompts/), [başlangıç dosyaları](tests/), [kontrol betikleri](checks/).

## Modeller ve harness'lar

| Model (Ollama) | Bağlam | Çıktı sınırı | Not |
|---|---|---|---|
| `gemma4:e4b` | 64K | 8192 | Küçük, hızlı |
| `inkling-pi:32k` | 32K | 8192 (opencode test 3 çalıştırma 2-3: 4096) | `inkling-2-mini:26b-a5b-iq4_NL`'den türetildi, `num_ctx 32768`, `num_batch 128` |
| `bonsai-pi:64k` | 64K | 16384 | Ternary Bonsai 2.5 27B `Q2_0`, model kartının örnekleme ayarları |

| | Pi | opencode |
|---|---|---|
| Sürüm | `1.6.0` (`@earendil-works/pi-coding-agent`) | `2.4.2` (ilk açılışta `1.19.6`'dan kendiliğinden güncellendi) |
| Bağlantı | `openai-completions`, `http://<sunucu>:11434/v1` | `@ai-sdk/openai-compatible`, aynı adres |
| Düşünme | `--thinking medium` | model ayarında `reasoningEffort: "medium"` (istekte `reasoning_effort` gittiği doğrulandı) |
| Komut onayı / sandbox | Yok | Varsayılan ayarda sormuyor, sandbox yok |
| Sıkıştırma (compaction) | `reserveTokens 10000`, `keepRecentTokens 8000` | Varsayılan: en az 16K boş alan, sonrasında 15K token korunur. Inkling için `buffer 6144`, `keep.tokens 4000` yapıldı |

## Testler

Her çalıştırma ayrı bir git deposunda, `baseline` etiketli temiz başlangıçtan ve yeni bir oturumla yapıldı.

| # | Görev | Ölçtüğü şey | Dosyalar | İstem |
|---|---|---|---|---|
| 1 | Tek satırlık hata (`len(xs) + 1`) | Basit okuma, düzenleme, test çalıştırma | [tests/test1](tests/test1) | [prompts/test1.txt](prompts/test1.txt) |
| 2 | İki dosyaya yayılmış iki hata (kuruşlar kayboluyor, indirim yüzde değil tutar olarak düşülüyor) | Belirtiyle nedeni farklı dosyada bulmak, teste dokunmamak | [tests/test2](tests/test2) | [prompts/test2.txt](prompts/test2.txt) |
| 3 | Kurallardan yeni özellik: `parse_duration` / `format_duration` ve kendi testleri | Kurallara tam uyum, test yazma, yalan başarı bildirmemek | [tests/test3](tests/test3) | [prompts/test3.txt](prompts/test3.txt) |

Test 1 ve 2 her modelde birer kez, test 3 üçer kez çalıştırıldı.

**Kurallar:** kullanıcı yalnızca `Continue.` yazabilir (en çok 3 kez), 10 dakikada durdurulur. Kontroller modelin göremediği bir klasörde tutuldu.

### Kontroller

> **Uyarı:** kontrol betikleri modelin yazdığı kodu sizin makinenizde, sandbox olmadan çalıştırır. Önce kodu okuyun.

| Betik | Ne yapar |
|---|---|
| [checks/check.py](checks/check.py) `<klasör> <1\|2\|3>` | Değişen dosyalar izin verilenlerin dışına çıktı mı (`SCOPE`). Test 1-2: `baseline`'daki **orijinal** test dosyasını çalıştırır, böylece değiştirilmiş bir test geçemez. Test 3: aşağıdaki gizli kontrolü ve sıkı test kuralını çalıştırır. |
| [checks/hidden_check.py](checks/hidden_check.py) `<klasör>` | 243 davranış kontrolü (geçerli/geçersiz girdiler ve 205 gidiş-dönüş). Modelin testlerini doğru bir koda ve 8 kasıtlı hatalı koda (mutant) karşı çalıştırır. |
| [checks/strict_strength.py](checks/strict_strength.py) `<klasör>` | Mutant puanı, sıkı kuralla: çıkış kodu 0, hiçbir satırda `FAIL` yok, son satır tam `PASS`. (Gevşek kural `PASS: ...` yazan betiklere aldanıyor.) |
| [checks/ascii_check.py](checks/ascii_check.py) `<klasör>` | "ASCII rakam" kuralı: `"٥s"`, `"５m"` gibi girdiler `ValueError` vermeli. Gizli kontrolde yoktu, sonradan eklendi. |

243 kontrolün çoğu gidiş-dönüş denemesi olduğu için puan yüzdesi yanıltıcıdır; asıl bakılacak şey kaçırılan girdilerdir.

### Kendiniz çalıştırmak için

```powershell
# her çalıştırma için ayrı klasör
$ws = "C:\bench\gemma\test3"
New-Item -ItemType Directory -Force $ws | Out-Null
Copy-Item -Recurse bench\tests\test3\* $ws; Copy-Item bench\tests\test3\.gitignore $ws
cd $ws; git init -q; git add -A; git commit -qm baseline; git tag baseline
# harness'ı bu klasörde açın, prompts\test3.txt içeriğini yapıştırın; bitince:
git diff baseline; git status --short
python <repo>\bench\checks\check.py . 3
python <repo>\bench\checks\strict_strength.py .
python <repo>\bench\checks\ascii_check.py .
```

opencode ayarı (`~/.config/opencode/opencode.jsonc`, kısaltılmış):

```jsonc
{
  "compaction": { "buffer": 6144, "keep": { "tokens": 4000 } },
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://gpu-server:11434/v1", "apiKey": "ollama" },
      "models": {
        "inkling-pi:32k": {
          "reasoning": true, "tool_call": true,
          "limit": { "context": 32768, "output": 4096 },
          "options": { "reasoningEffort": "medium" }
        }
      }
    }
  }
}
```

opencode 2.x'te `-m` bayrağı yok; model TUI içinde (`ctrl+p`) seçilir. Ayar değişince `opencode reload` gerekir.

## Sonuçlar

Süreler: Pi'de bekleme hariç yaklaşık çalışma süresi, opencode'da ilk istekten son yanıta kadar (opencode veritabanından).
Düşünme: bin karakter. Test 3'te üç değer üç çalıştırmayı gösterir.

### Pi

| | gemma4:e4b | inkling-pi:32k | bonsai-pi:64k |
|---|---|---|---|
| Test 1 | Bir yardım mesajıyla düzeltti | Geçti, 32 sn | Geçti, 20 sn |
| Test 2 | Geçti, 11 sn | Geçti, 26 sn | Geçti, 63 sn |
| Test 3 gizli kontrol (/243) | 238, 238, 238 | 243, 243, 243 | 243, 243, 243 |
| Test 3 ASCII kuralı | ✗ ✗ ✗ | ✗ ✓ ✓ | ✗ ✗ ✗ |
| Test 3 kendi testleri (sıkı) | ✗ ✓ ✓ | ✓ ✓ ✓ | ✓ ✓ ✓ |
| Test 3 mutant (sıkı, /8) | ölçülemedi, 8, 8 | 8, 8, 8 | 8, 8, 8 |
| Test 3 `Continue.` | 0, 1, 1 | 0, 0, 0 | 0, 0, 0 |
| Test 3 süre (sn) | 80, 91, 113 | 268, 233, 160 | 131, 142, 240 |
| Test 3 düşünme | 18, 24, 31 | 6, 7, 2 | 3, 3, 8 |
| Kaybolan araç çağrısı (5 çalıştırma) | 3 | 0 | 0 |

### opencode

| | gemma4:e4b | inkling-pi:32k | bonsai-pi:64k |
|---|---|---|---|
| Test 1 | Geçti, 20 sn | Geçti, 124 sn (model yükleme dahil) | Geçti, 40 sn |
| Test 2 | Geçti, 18 sn | Geçti, 156 sn | Geçti, 94 sn |
| Test 3 gizli kontrol (/243) | 243, 241, 238 | 243 (zaman aşımı), 243, 243 | 243, 243, 243 |
| Test 3 ASCII kuralı | ✗ ✗ ✗ | ✓ ✓ ✓ | ✓ ✗ ✓ |
| Test 3 kendi testleri (sıkı) | ✗ ✓ ✗ | ✗ ✓ ✓ | ✓ ✓ ✓ |
| Test 3 mutant (sıkı, /8) | ölçülemedi, 7, ölçülemedi | ölçülemedi, 8, 8 | 8, 8, 8 |
| Test 3 `Continue.` | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| Test 3 süre (sn) | 148, 91, 65 | durduruldu (~15 dk), 506, 400 | 276, 524, 704 |
| Test 3 düşünme | 24, 15, 8 | 25, 9, 10 | 16, 33, 53 |
| Test 3 sıkıştırma | 0, 0, 0 | 2, 0, 0 | 0, 0, 0 |
| Kaybolan araç çağrısı (5 çalıştırma) | 0 (3 hatalı çağrı, kendisi düzeltti) | 0 (2 hatalı çağrı, kendisi düzeltti) | 0 |

opencode notları:
- **Gemma test 3:** 1. çalıştırmanın testi doğru bir girdiyi (`"1d 1m"`) hatalı sayıyor ve `pytest` içe aktarıyor; model testi suçlayıp işi bitmiş saydı.
  2. çalıştırma `"5 m"` ve `format_duration(True)` kabul ediyor. 3. çalıştırma Pi'deki aynı beş hatayı yapıyor (`-5m`, `1.5h`, `1h,5m`, `1h foo`, `1h5` kabul).
  Ayrıca `PASS`'tan sonra bir satır daha yazdırıyor.
- **Inkling test 3, 1. çalıştırma:** varsayılan sıkıştırma ayarıyla 32K pencerede ~16.7K token'da sıkıştırdı, iki kez. Her seferinde dosyaları unutup baştan düşündü, testini hiç çalıştıramadan 10 dakikayı geçti ve durduruldu.
  Bıraktığı `duration.py` doğruydu (243/243, ASCII geçti), test dosyası yanlış bir beklenen değer içeriyordu.
  Çıktı sınırını 4096'ya düşürmek tek başına işe yaramadı (yine ~16.6K'da sıkıştırdı, geçersiz sayıldı). `compaction.buffer 6144` ve `keep.tokens 4000` ile 2. ve 3. çalıştırma hiç sıkıştırmadan tam temiz bitti.
- **Bonsai test 3:** her çalıştırmada ilk adımda 4-5.5 dakika düşündü. 3. çalıştırma 10 dakika sınırını aştı (kullanıcı durdurmadı) ama sonuç en temiz olanlardan: `"1ſ"` girdisini de reddediyor.
- Gemma ve Bonsai (64K) en çok ~31K ve ~20K token kullandı; sıkıştırmaya hiç yaklaşmadılar, yeni sıkıştırma ayarı onların sonuçlarını etkilemez.

### Model karşılaştırması

| Model | Kısa sonuç |
|---|---|
| **inkling-pi:32k** | Kurallara en sıkı uyan model: iki harness'ta geçerli 5 test 3 çalıştırmasının hepsi 243/243, ASCII kuralı 5'te 4. Kod yazmak için önerilen. opencode'da sıkıştırma ayarı şart. |
| **bonsai-pi:64k** | Altı test 3 çalıştırmasının hepsi 243/243 ve 8/8; ASCII kuralında zayıf (Pi 0/3, opencode 2/3). Uzun bağlam gereken işler için. opencode'da çok yavaş. |
| **gemma4:e4b** | En hızlısı ama test 3'te hiçbir çalıştırması tam doğru değil; geçersiz girdileri kabul ediyor ve başarıyı kolay iddia ediyor. Gözetimli küçük düzeltmeler için. |

### Harness karşılaştırması

| | Pi | opencode |
|---|---|---|
| Doğruluk | Aynı seviyede | Aynı seviyede |
| Gemma'nın araç çağrıları | 5 çalıştırmada 3 çağrı kayboldu (Ollama ayrıştıramadı), Pi hata göstermeden durdu | Kayıp yok; hatalı çağrılar araç hatası olarak döndü ve model kendisi düzeltti |
| Hız (Inkling, Bonsai) | Daha hızlı, daha az düşünme | Test 3'te Inkling ~2, Bonsai 2-4 kat yavaş; Bonsai 5-11 kat fazla düşündü |
| Küçük bağlam (32K) | Sorunsuz | Varsayılan sıkıştırma ayarı işi engelliyor; ayar gerekiyor |
| Sistem istemi | Ölçülmedi | ~22-23K karakter, 10-12 araç (ilk istek ~10.7K token) |
| Güncelleme | Elle | Kendiliğinden güncelledi; komut satırı değişti (`-m` kalktı) |

**Sınırlar:** her hücre bir-üç çalıştırma; örnek sayısı az. Bağlam ve çıktı sınırları modeller arasında farklı. opencode'da Inkling'in test 3 ayarı (çıktı 4096, sıkıştırma) Pi'dekinden farklı. Süreler aynı yöntemle ölçülmedi.
