import { ethers } from "hardhat";
import { expect } from "chai";
import "@nomicfoundation/hardhat-chai-matchers";

const DECIMALS = 6n;
const CAP = 20_000n * 10n ** DECIMALS;

describe("wRTC", () => {
  async function deployFixture() {
    const [admin, minter, pauser, alice, bob] = await ethers.getSigners();
    const WRTC = await ethers.getContractFactory("wRTC");
    const wrtc = await WRTC.deploy(admin.address);
    await wrtc.waitForDeployment();

    // Set up roles: minter gets MINTER_ROLE, pauser gets PAUSER_ROLE
    await wrtc.connect(admin).grantRole(await wrtc.MINTER_ROLE(), minter.address);
    await wrtc.connect(admin).revokeRole(await wrtc.MINTER_ROLE(), admin.address);
    await wrtc.connect(admin).grantRole(await wrtc.PAUSER_ROLE(), pauser.address);

    return { wrtc, admin, minter, pauser, alice, bob };
  }

  // ── Basic ERC-20 ────────────────────────────────────────────────────
  it("has 6 decimals, zero initial supply, and correct cap", async () => {
    const { wrtc } = await deployFixture();
    expect(await wrtc.decimals()).to.equal(6n);
    expect(await wrtc.totalSupply()).to.equal(0n);
    expect(await wrtc.MINT_CAP()).to.equal(CAP);
    expect(await wrtc.name()).to.equal("Wrapped RTC");
    expect(await wrtc.symbol()).to.equal("wRTC");
  });

  // ── Minting ─────────────────────────────────────────────────────────
  it("mints under cap and tracks totalMinted", async () => {
    const { wrtc, minter, alice } = await deployFixture();
    const amount = ethers.parseUnits("100", 6);
    await expect(wrtc.connect(minter).mint(alice.address, amount))
      .to.emit(wrtc, "TokensMinted")
      .withArgs(alice.address, amount);
    expect(await wrtc.balanceOf(alice.address)).to.equal(amount);
    expect(await wrtc.totalMinted()).to.equal(amount);
  });

  it("reverts mint when cap exceeded", async () => {
    const { wrtc, minter, alice } = await deployFixture();
    const almost = CAP - 1n;
    await wrtc.connect(minter).mint(alice.address, almost);
    await expect(
      wrtc.connect(minter).mint(alice.address, 2n)
    ).to.be.revertedWith("wRTC: cap exceeded");
  });

  it("non-minter cannot mint", async () => {
    const { wrtc, alice, bob } = await deployFixture();
    await expect(
      wrtc.connect(alice).mint(bob.address, 1n)
    ).to.be.revertedWithCustomError(wrtc, "AccessControlUnauthorizedAccount");
  });

  // ── Burning ─────────────────────────────────────────────────────────
  it("burn and burnFrom with allowance", async () => {
    const { wrtc, minter, alice, bob } = await deployFixture();
    const amount = ethers.parseUnits("50", 6);
    await wrtc.connect(minter).mint(alice.address, amount);

    await expect(wrtc.connect(alice).burn(ethers.parseUnits("10", 6)))
      .to.emit(wrtc, "TokensBurned")
      .withArgs(alice.address, ethers.parseUnits("10", 6));

    await wrtc.connect(alice).approve(bob.address, ethers.parseUnits("20", 6));
    await wrtc.connect(bob).burnFrom(alice.address, ethers.parseUnits("20", 6));
    expect(await wrtc.balanceOf(alice.address)).to.equal(ethers.parseUnits("20", 6));
  });

  it("totalMinted does not decrease after burn", async () => {
    const { wrtc, minter, alice } = await deployFixture();
    const amount = ethers.parseUnits("100", 6);
    await wrtc.connect(minter).mint(alice.address, amount);
    await wrtc.connect(alice).burn(ethers.parseUnits("50", 6));
    expect(await wrtc.totalMinted()).to.equal(amount); // unchanged
    expect(await wrtc.totalSupply()).to.equal(ethers.parseUnits("50", 6));
  });

  // ── Pausable ────────────────────────────────────────────────────────
  it("pauser can pause and unpause transfers", async () => {
    const { wrtc, minter, pauser, alice, bob } = await deployFixture();
    const amount = ethers.parseUnits("100", 6);
    await wrtc.connect(minter).mint(alice.address, amount);

    // Pause
    await wrtc.connect(pauser).pause();

    // Transfers blocked
    await expect(
      wrtc.connect(alice).transfer(bob.address, 1n)
    ).to.be.revertedWithCustomError(wrtc, "EnforcedPause");

    // Minting blocked
    await expect(
      wrtc.connect(minter).mint(bob.address, 1n)
    ).to.be.revertedWithCustomError(wrtc, "EnforcedPause");

    // Burning blocked
    await expect(
      wrtc.connect(alice).burn(1n)
    ).to.be.revertedWithCustomError(wrtc, "EnforcedPause");

    // Unpause
    await wrtc.connect(pauser).unpause();

    // Transfers resume
    await expect(wrtc.connect(alice).transfer(bob.address, 1n)).to.not.be.reverted;
  });

  it("non-pauser cannot pause", async () => {
    const { wrtc, alice } = await deployFixture();
    await expect(
      wrtc.connect(alice).pause()
    ).to.be.revertedWithCustomError(wrtc, "AccessControlUnauthorizedAccount");
  });

  // ── ERC-2612 Permit ─────────────────────────────────────────────────
  it("supports EIP-2612 permit (gasless approval)", async () => {
    const { wrtc, minter, alice, bob } = await deployFixture();
    const amount = ethers.parseUnits("50", 6);
    await wrtc.connect(minter).mint(alice.address, amount);

    const wrtcAddress = await wrtc.getAddress();
    const nonce = await wrtc.nonces(alice.address);
    const deadline = BigInt(Math.floor(Date.now() / 1000)) + 3600n;

    const domain = {
      name: "Wrapped RTC",
      version: "1",
      chainId: (await ethers.provider.getNetwork()).chainId,
      verifyingContract: wrtcAddress,
    };

    const types = {
      Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" },
      ],
    };

    const value = {
      owner: alice.address,
      spender: bob.address,
      value: amount,
      nonce: nonce,
      deadline: deadline,
    };

    const sig = await alice.signTypedData(domain, types, value);
    const { v, r, s } = ethers.Signature.from(sig);

    await wrtc.connect(bob).permit(alice.address, bob.address, amount, deadline, v, r, s);
    expect(await wrtc.allowance(alice.address, bob.address)).to.equal(amount);
  });

  // ── Constructor guard ───────────────────────────────────────────────
  it("reverts deploy with zero address admin", async () => {
    const WRTC = await ethers.getContractFactory("wRTC");
    await expect(WRTC.deploy(ethers.ZeroAddress)).to.be.revertedWith("wRTC: zero admin");
  });

  // ── AccessControl ───────────────────────────────────────────────────
  it("admin can grant and revoke roles", async () => {
    const { wrtc, admin, alice } = await deployFixture();
    const MINTER = await wrtc.MINTER_ROLE();

    await wrtc.connect(admin).grantRole(MINTER, alice.address);
    expect(await wrtc.hasRole(MINTER, alice.address)).to.be.true;

    await wrtc.connect(admin).revokeRole(MINTER, alice.address);
    expect(await wrtc.hasRole(MINTER, alice.address)).to.be.false;
  });
});
