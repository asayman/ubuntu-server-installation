# Ubuntu Server 24.04 + NVIDIA GPU: Local AI / YOLO / EgoBlur Server Setup

**English** | [Türkçe](README.tr.md)

A step-by-step record of turning an old 3D design workstation into a server that runs local models
(LLM, YOLO, EgoBlur and more) on its GPU, starting from a clean **Ubuntu Server 24.04.2 LTS** install.
Every command, every error, its fix and the result are written down, so anyone doing something similar can follow along.

> The step-by-step guides in [docs/](docs/) and the full command log in [LOG.md](LOG.md) are in Turkish.

## Hardware

| Component | Value |
|---|---|
| CPU | Intel Xeon W-2235 @ 3.80 GHz (6 cores / 12 threads) |
| RAM | 32 GB |
| Disk | 480 GB SSD |
| GPU | NVIDIA RTX A4000 16 GB (Ampere, GA104) |
| OS | Ubuntu Server 24.04.2 LTS (amd64) |

## Roadmap

| # | Step | Done by | Status |
|---|---|---|---|
| 1 | [Downloading the ISO and making a USB stick with Rufus](docs/01-usb-hazirlama.md) | User (Windows) | ✅ Done |
| 2 | [BIOS settings and Ubuntu Server install](docs/02-ubuntu-kurulum.md) | User (on site) | ✅ Done |
| 3 | [Static IP (netplan)](docs/03-sabit-ip.md) | Over SSH | ✅ Done |
| 4 | [SSH service and key-based remote login](docs/04-ssh.md) | User | ✅ Done |
| 5 | [System update, base packages, disk expansion](docs/05-temel-sistem.md) | Over SSH | ✅ Done |
| 6 | [NVIDIA driver](docs/06-nvidia-surucu.md) | Over SSH | ✅ Done |
| 7 | [Docker + NVIDIA Container Toolkit](docs/07-docker-nvidia.md) | Over SSH | ✅ Done |
| 8 | [Python environment, PyTorch, YOLO, EgoBlur](docs/08-pytorch-yolo-egoblur.md) | Over SSH | ✅ |
| 9 | [Local LLM: Ollama + Open WebUI](docs/09-lokal-llm.md) | Over SSH | ✅ Done |
| 10 | [(Optional) Access from outside the LAN: Tailscale](docs/10-uzaktan-erisim-tailscale.md) | Over SSH + user (account approval) | ✅ Done |

- Every command run and its output: [LOG.md](LOG.md)
- Problems hit, what worked and what didn't: [docs/sorunlar-ve-dersler.md](docs/sorunlar-ve-dersler.md)

## Coding assistant tests: Pi and opencode

Three local models on the server (`gemma4:e4b`, `inkling-pi:32k`, `bonsai-pi:64k`) were tried with two coding assistants
(harnesses) on a Windows PC, [Pi](https://pi.dev) `1.6.0` and [opencode](https://opencode.ai) `2.4.2`, on the same three tasks:
a one-line bug, two bugs spread over two files, and a new feature built from a written spec (3 runs).
Results were judged by `git diff` and by check scripts the model never saw, not by what the model claimed.

| Test 3: feature from a spec (3 runs) | Pi | opencode |
|---|---|---|
| **inkling-pi:32k** | 243/243 ×3, ASCII rule 2/3 | Run 1 timed out (compaction setting), then 243/243 ×2, fully clean |
| **bonsai-pi:64k** | 243/243 ×3, ASCII rule 0/3 | 243/243 ×3, ASCII rule 2/3, 2-4× slower |
| **gemma4:e4b** | 238/243 ×3, lost tool calls | 243, 241, 238; weak own tests |

Every model passed tests 1 and 2 in both harnesses (in Pi, Gemma needed one help message on test 1).
In short: **Inkling** for writing code, **Bonsai** for long context, **Gemma** for quick, supervised small fixes.

- Prompts, starting files, check scripts, all tables and harness settings: [bench/](bench/README.md)
- Commands and details (Turkish): [LOG.md](LOG.md)

## Using this repo for your own setup

- Values such as `192.168.1.50`, `gpu-server` and `kullanici` (user) in the docs are **examples**.
  Replace them with your own network and username.
- The network interface name (`eno1`, `enp0s31f6` and so on) depends on the hardware; find yours with `ip a`.

## License

[MIT](LICENSE)
