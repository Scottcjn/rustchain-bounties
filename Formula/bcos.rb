# SPDX-License-Identifier: MIT
class Bcos < Formula
  desc "BCOS v2 - Beacon Certified Open Source code certification engine"
  homepage "https://rustchain.org/bcos/"
  url "https://files.pythonhosted.org/packages/source/c/clawrtc/clawrtc-1.8.0.tar.gz"
  sha256 "TODO: Calculate SHA256 after upload"
  license "MIT"

  head "https://github.com/Scottcjn/Rustchain.git", branch: "main"

  depends_on "python@3.9"
  depends_on "pip"
  depends_on "semgrep" => :optional
  depends_on "pip-audit" => :optional

  def install
    # Install Python package
    system "pip3", "install", "-v", "--no-deps", "--ignore-installed", "--no-binary", ":all:", "--prefix", prefix, "."
    
    # Install bcos command
    bin.install "tools/bcos_engine.py" => "bcos"
    chmod 0755, bin/"bcos"
  end

  def post_install
    # Ensure pip installs are accessible
    (HOMEBREW_PREFIX/"lib/python3.9/site-packages").mkpath
  end

  def caveats
    <<~EOS
      BCOS v2 is now installed!

      Usage:
        bcos scan .              # Scan current directory
        bcos verify BCOS-xxx     # Verify a certification
        bcos certify .           # Certify a repository

      For more information, visit: https://rustchain.org/bcos/
    EOS
  end

  test do
    # Test basic command execution
    assert_match "BCOS", shell_output("#{bin}/bcos --help")
  end
end
