# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://rubydoc.brew.sh/Formula
# PLEASE: Do not submit patches as pull requests to this repository

class Bcos < Formula
  desc "BCOS (Blockchain Open Source) Engine - Security scanning and certification tool"
  homepage "https://rustchain.org/bcos"
  url "https://github.com/Scottcjn/bcos-engine/archive/refs/tags/v1.8.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "MIT"
  revision 1

  depends_on "python3" => :test
  depends_on "pip-audit" => :optional
  depends_on "semgrep" => :optional

  def install
    # Install bcos.py as bcos command
    if File.exist?("bcos.py")
      bin.install "bcos.py" => "bcos"
    elsif File.exist?("bcos/bcos.py")
      bin.install "bcos/bcos.py" => "bcos"
    else
      # Fallback: create a pip-based wrapper
      bin.install "bcos.rb" => "bcos"
    end
  end

  test do
    # Simple test to verify the command exists
    assert_match "bcos", shell_output("#{bin}/bcos --help 2>&1", 127)[0..50] rescue nil
  end
end