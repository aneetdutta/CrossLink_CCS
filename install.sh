#!/usr/bin/env bash
# ==============================================================================
# CrossLink: Automated Installation & Environment Setup Script
# ==============================================================================
set -euo pipefail

# Color formatting helpers
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RED="\033[31m"
RESET="\033[0m"

log_info() { echo -e "${CYAN}[INFO]${RESET} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${RESET} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${RESET} $1"; }
log_error() { echo -e "${RED}[ERROR]${RESET} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info "Starting CrossLink installation..."

# ------------------------------------------------------------------------------
# 1. System Packages (APT)
# ------------------------------------------------------------------------------
if command -v apt-get &> /dev/null; then
    log_info "Updating package lists and installing system dependencies..."
    SUDO=""
    if [ "$EUID" -ne 0 ] && command -v sudo &> /dev/null; then
        SUDO="sudo"
    fi
    $SUDO apt-get update -y || true
    $SUDO apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        curl \
        git \
        pkg-config \
        libssl-dev \
        libxrender1 \
        libxext6 \
        libsm6 \
        libx11-6 \
        libgl1 \
        libfontconfig1 \
        sumo \
        sumo-tools || log_warn "Some apt packages could not be installed automatically. Continuing..."
    $SUDO ldconfig || true
else
    log_warn "apt-get not found. Skipping system package installation. Ensure required tools (Python, Rust, SUMO) are installed."
fi

# ------------------------------------------------------------------------------
# 2. Rust Toolchain Installation & Engine Compilation
# ------------------------------------------------------------------------------
if ! command -v cargo &> /dev/null; then
    log_info "Rust toolchain not found. Installing Rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
else
    log_info "Rust toolchain detected: $(rustc --version)"
fi

if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

log_info "Building optimized Rust backend release binaries..."
cd rust_code
cargo build --release
cd ..
log_success "Rust backend compiled successfully."

# ------------------------------------------------------------------------------
# 3. Python Environment Setup using `uv`
# ------------------------------------------------------------------------------
if ! command -v uv &> /dev/null; then
    log_info "Installing 'uv' package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    elif [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv &> /dev/null; then
    log_warn "'uv' command not found in PATH after installation attempt. Falling back to standard python3 venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    log_info "'uv' version detected: $(uv --version)"
    log_info "Creating Python virtual environment (.venv) via uv..."
    uv venv --clear .venv
    log_info "Installing Python dependencies from pyproject.toml via uv..."
    uv pip install -r pyproject.toml
fi

log_success "Python virtual environment created and dependencies installed."

# ------------------------------------------------------------------------------
# 4. Rust Backend Configuration Update
# ------------------------------------------------------------------------------
CONFIG_YAML="$SCRIPT_DIR/rust_code/config.yaml"
if [ -f "$CONFIG_YAML" ]; then
    log_info "Updating root_dir path in rust_code/config.yaml..."
    ROOT_PATH="$SCRIPT_DIR/"
    sed -i "s|^root_dir:.*|root_dir: \"$ROOT_PATH\" #path to main repository|" "$CONFIG_YAML"
    log_success "Updated rust_code/config.yaml root_dir to: $ROOT_PATH"
fi

# ------------------------------------------------------------------------------
# 4. Verification & Smoke Test
# ------------------------------------------------------------------------------
log_info "Verifying installed software versions..."

VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON="python3"
fi

log_info "Python version: $($VENV_PYTHON --version)"
log_info "Rust version: $(rustc --version 2>/dev/null || echo 'Not found')"

if command -v sumo &> /dev/null; then
    log_info "SUMO version: $(sumo --version 2>&1 | head -n 1)"
else
    log_warn "SUMO binary ('sumo') is not currently in PATH. If SUMO was installed via apt or custom path, ensure SUMO_HOME and PATH are configured."
fi

# Run a quick python import test
$VENV_PYTHON -c "
import shapely, libsumo, polars, pandas, scipy, pymongo, loguru, matplotlib, yaml, pyshark, seaborn, networkx, tqdm, pyarrow, sklearn, alphashape
print('All core Python imports verified successfully!')
"

log_success "=========================================================="
log_success " CrossLink Environment Setup Completed Successfully! "
log_success "=========================================================="
echo -e "${CYAN}To activate the Python virtual environment, run:${RESET}"
echo -e "    ${BOLD}source .venv/bin/activate${RESET}"