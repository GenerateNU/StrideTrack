# Dependencies Installation Guide

This guide covers all tools required to develop StrideTrack locally.

## Package Managers

Before installing dependencies, ensure you have the appropriate package manager for your OS.

**macOS - Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Windows - Chocolatey:**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

## Required Tools

### 1. Docker & Docker Compose

Containerization for all services.

**macOS:**

```bash
brew install --cask docker
```

**Linux (Ubuntu/Debian):**

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Windows:**

```bash
choco install docker-desktop
```

### 2. Bun

JavaScript runtime and package manager for the frontend.

**All platforms:**

```bash
curl -fsSL https://bun.sh/install | bash
```

**macOS (Homebrew):**

```bash
brew install oven-sh/bun/bun
```

**Windows:**

```bash
choco install bun
```

### 3. Python 3.13.9

Required for the backend.

**macOS:**

```bash
brew install python@3.13
```

**Linux:**

```bash
# Using pyenv (recommended)
curl https://pyenv.run | bash
pyenv install 3.13.9
pyenv global 3.13.9
```

**Windows:**

```bash
choco install python --version=3.13.9
```

### 4. uv

Fast Python package manager.

**All platforms:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS (Homebrew):**

```bash
brew install uv
```

**Windows:**

```bash
choco install uv
```

### 5. Make

Task automation (usually pre-installed on macOS/Linux).

**macOS:**

```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt install make
```

**Windows:**

```bash
choco install make
```

## Verification

Run from project root:

```bash
make check-deps
```

Or manually verify each tool:

```bash
docker --version          # Docker version 24+
docker compose version    # Docker Compose version v2+
bun --version             # 1.0+
python --version          # Python 3.13.9
uv --version              # 0.1+
make --version            # GNU Make 3.81+
```
