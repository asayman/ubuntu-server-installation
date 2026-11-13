# 7. Docker + NVIDIA Container Toolkit

> Durum: ✅ Tamamlandı (2026-11-13). Docker `29.9.3`, Compose `v5.7.1`, NVIDIA Container Toolkit `1.20.2`.
> Komutlar ve çıktılar [LOG.md](../LOG.md)'de.

## 7.1 Docker resmi apt deposu

Ubuntu'nun `docker.io` paketi eski kalır, snap sürümü NVIDIA runtime ve izinlerle sorun çıkarır.
Resmi depoyu kullanın:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
gpg --show-keys --with-fingerprint /etc/apt/keyrings/docker.asc
# beklenen: 9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88

. /etc/os-release
printf "Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n" \
  "$VERSION_CODENAME" "$(dpkg --print-architecture)" | sudo tee /etc/apt/sources.list.d/docker.sources
sudo apt-get update
```

## 7.2 Docker Engine

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl is-enabled docker containerd     # enabled
sudo docker run --rm hello-world           # "Hello from Docker!"
```

## 7.3 docker grubu

```bash
sudo usermod -aG docker "$USER"     # -a şart: yoksa sudo grubundan çıkarsınız
# yeni SSH oturumu açın, sonra:
id -nG; docker ps
```

> ⚠️ `docker` grubu fiilen şifresiz root yetkisidir (`docker run -v /:/host ...`).
> Tek kullanıcılı ev sunucusunda bilinçli bir uzlaşma olarak seçildi.
> Alternatifler: her komutta `sudo docker` veya rootless Docker (GPU kurulumu daha karmaşık).

## 7.4 NVIDIA Container Toolkit

Container'lar normalde GPU'yu görmez. Toolkit, `--gpus all` ile sürücü kütüphanelerini ve
`/dev/nvidia*` cihazlarını container'a bağlar.

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
gpg --show-keys --with-fingerprint /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
# beklenen: C95B 321B 61E8 8C18 09C4  F759 DDCA E044 F796 ECB0 (NVIDIA CORPORATION)

curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

## 7.5 Docker'a nvidia runtime'ı tanıtma

```bash
sudo nvidia-ctk runtime configure --runtime=docker   # /etc/docker/daemon.json yazar
sudo systemctl restart docker
docker info | grep -i runtimes                       # nvidia görünmeli
```

## 7.6 GPU testi

İmajın CUDA sürümü, `nvidia-smi`'deki `CUDA Version` değerini aşmamalı (bu kurulumda 13.2).

```bash
docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 nvidia-smi
```

## 7.7 Yeniden başlatma sonrası

```bash
systemctl is-active docker nvidia-persistenced
nvidia-smi -q | grep -i "Persistence Mode"
docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 nvidia-smi -L
```
