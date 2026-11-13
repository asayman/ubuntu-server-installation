# 4. SSH Servisi ve Uzaktan Bağlantı

## 4.1 Sunucuda SSH durumunu kontrol etme

Kurulumda "Install OpenSSH server" seçildiyse paket kuruludur. Ubuntu 24.04'te SSH
**socket activation** ile çalışır: `ssh.socket` 22. portu dinler, bağlantı gelince `ssh.service` başlar.
Bu yüzden `ssh.service` "inactive" görünebilir; bu normaldir.

```bash
systemctl status ssh.socket ssh.service --no-pager
ss -tlnp | grep ':22'      # 22. port dinleniyor mu?
```

Kurulu değilse:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

## 4.2 Güvenlik duvarı (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
```

> Önce `allow OpenSSH`, sonra `enable`. Ters sırada uzaktaki oturum kilitlenebilir.

## 4.3 İstemciden (Mac/Linux/Windows) ilk bağlantı

```bash
ssh kullanici@192.168.1.50
```

İlk bağlantıda host fingerprint onayı sorulur → `yes`. Şifre ile giriş yapılmalı.

## 4.4 SSH anahtarı ile şifresiz giriş

İstemcide anahtar yoksa oluşturun:

```bash
ssh-keygen -t ed25519 -C "gpu-server erisimi"
```

Public key'i sunucuya kopyalayın:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub kullanici@192.168.1.50
```

Windows'ta `ssh-copy-id` yoktur; PowerShell:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh kullanici@192.168.1.50 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Test (şifre sormamalı):

```bash
ssh kullanici@192.168.1.50 'hostname && whoami'
```

## 4.5 Kısa ad: `~/.ssh/config`

İstemcide:

```
Host gpu-server
    HostName 192.168.1.50
    User kullanici
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 30
```

Artık `ssh gpu-server` yeterli.

## 4.6 Otomasyon için şifresiz sudo (geçici)

Kurulumun geri kalanı (sürücü, CUDA, Docker) SSH üzerinden betik/otomasyon ile yapılacağı için,
etkileşimsiz `sudo` gerekir. **Geçici olarak** kullanıcıya şifresiz sudo verin:

```bash
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/90-setup-nopasswd
sudo chmod 440 /etc/sudoers.d/90-setup-nopasswd
sudo visudo -c       # "parsed OK" görmelisiniz
```

> **Güvenlik:** Bu, SSH anahtarına erişen herkese root yetkisi verir. Kurulum bitince kaldırın:
> `sudo rm /etc/sudoers.d/90-setup-nopasswd`

## 4.7 SSH sertleştirme (anahtar girişi çalıştıktan sonra)

Anahtarla girişin çalıştığından **emin olduktan sonra** şifreyle girişi kapatın:

```bash
sudo tee /etc/ssh/sshd_config.d/99-hardening.conf >/dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
sudo sshd -t && sudo systemctl restart ssh
```

Mevcut oturumu kapatmadan yeni bir terminalden `ssh gpu-server` ile test edin.

## Sonuç kontrol listesi

- [ ] `ssh gpu-server` şifre sormadan bağlanıyor
- [ ] `ssh gpu-server 'sudo -n true && echo OK'` → `OK`
- [ ] UFW aktif, OpenSSH izinli

Sonraki adım: [05 - Temel sistem](05-temel-sistem.md)
