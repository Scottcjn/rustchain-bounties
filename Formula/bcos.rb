# typed: true
# frozen_string_literal: true

# Homebrew formula for BCOS engine standalone tool.
# Usage: brew install Scottcjn/tap/bcos
#
# This formula installs bcos_engine.py as the `bcos` command,
# pulling from PyPI (clawrtc 1.8.0+) or directly from GitHub.
# Dependencies: python3, semgrep (optional), pip-audit (optional)

class Bcos < Formula
  include Language::Python::Virtualenv

  desc "BCOS engine standalone tool"
  homepage "https://github.com/Scottcjn/RustChain"
  url "https://github.com/Scottcjn/rustchain-bounties/archive/refs/tags/v0.0.1.tar.gz"  # placeholder, replace with actual release
  version "1.0.0"

  depends_on "python@3.11"
  depends_on "semgrep" => :optional
  depends_on "pip-audit" => :optional

  resource "clawrtc" do
    url "https://files.pythonhosted.org/packages/source/c/clawrtc/clawrtc-1.8.0.tar.gz"
    # TODO: Replace with actual SHA256 from PyPI
    sha256 ""
  end

  def install
    venv = virtualenv_create(libexec, "python3")
    venv.pip_install resource("clawrtc")
    # Create wrapper script to expose bcos command
    (bin/"bcos").write <<~EOS
      #!/bin/bash
      exec "#{venv.root}/bin/python3" -m bcos_engine "$@"
    EOS
    chmod 0755, bin/"bcos"
  end

  test do
    system "#{bin}/bcos", "--help"
  end
end
