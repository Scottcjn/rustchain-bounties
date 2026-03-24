class Bcos < Formula
  desc "BCOS v2 - Beacon Certified Open Source engine for trust scoring"
  homepage "https://rustchain.org/bcos/"
  url "https://github.com/Scottcjn/Rustchain/archive/refs/heads/main.tar.gz"
  sha256 :no_check
  license "MIT"
  version "2.0.0"
  revision 1

  depends_on "python@3.11"
  depends_on "semgrep" => :optional
  depends_on "pip-audit" => :optional

  def install
    # Install the BCOS engine script
    bin.install "tools/bcos_engine.py" => "bcos"
    
    # Make it executable
    chmod 0755, bin/"bcos"
    
    # Install supporting tools
    bin.install "tools/bcos_spdx_check.py" => "bcos-spdx-check" if File.exist?("tools/bcos_spdx_check.py")
    bin.install "tools/bcos_sbom_gen.py" => "bcos-sbom-gen" if File.exist?("tools/bcos_sbom_gen.py")
    
    # Create a wrapper that uses system Python
    (bin/"bcos").atomic_write <<~EOS
      #!/bin/bash
      exec "#{Formula["python@3.11"].opt_bin}/python3.11" "#{opt_bin}/bcos" "$@"
    EOS
    chmod 0755, bin/"bcos"
  end

  def caveats
    <<~EOS
      BCOS v2 Engine installed!
      
      Usage:
        bcos scan [path]           # Scan directory for BCOS certification
        bcos verify BCOS-xxx       # Verify a BCOS certification ID
        bcos certify [path]        # Certify a directory
        bcos --help                # Show help
        bcos --version             # Show version
      
      Optional dependencies:
        brew install semgrep       # For static analysis
        pip install pip-audit      # For vulnerability scanning
      
      Documentation: https://rustchain.org/bcos/
    EOS
  end

  test do
    # Test basic commands
    system "#{bin}/bcos", "--help"
    system "#{bin}/bcos", "--version"
    
    # Test scan on current directory
    system "#{bin}/bcos", "scan", ".", "--json" if File.exist?("#{bin}/bcos")
  end
end
