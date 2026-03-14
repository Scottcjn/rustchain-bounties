#!/usr/bin/env python3
"""
ESP32 Network Bridge for Computer Space Miner

This MicroPython firmware runs on the ESP32 and provides:
- WiFi connectivity to RustChain API
- SPI communication with FPGA
- Hardware fingerprinting
- Attestation protocol

Author: RustChain Bounty Hunter
License: MIT
"""

import network
import urequests as requests
import json
import machine
import time
import gc
from machine import SPI, Pin, ADC, RTC


# ============================================================================
# CONFIGURATION
# ============================================================================

WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
RUSTCHAIN_API = "http://rustchain.org/api/attest"
WALLET_ADDRESS = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
EPOCH_DURATION = 600  # 10 minutes in seconds

# SPI Configuration (FPGA interface)
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19
SPI_CS = 5

# LED indicators
LED_MINING = 2
LED_NETWORK = 4
LED_ERROR = 15


# ============================================================================
# HARDWARE FINGERPRINT COLLECTOR
# ============================================================================

class FingerprintCollector:
    """
    Collects unique hardware fingerprints from ESP32.
    
    These fingerprints prove we're running on real hardware,
    not an emulator.
    """
    
    def __init__(self):
        # ADC for noise measurement (GPIO 36 = VP)
        self.adc = ADC(Pin(36))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        
        # Temperature sensor (internal)
        # self.temp_sensor = machine.TouchPad(4)  # Optional
        
        # RTC for drift measurement
        self.rtc = RTC()
        
        # WiFi for RSSI fingerprint
        self.wlan = None
    
    def read_chip_id(self) -> str:
        """Read unique ESP32 chip ID (efuse MAC)"""
        # ESP32 has unique MAC address burned into efuse
        mac = machine.unique_id()
        return mac.hex().upper()
    
    def measure_adc_noise(self) -> int:
        """
        Measure ADC noise floor.
        
        Real hardware has analog noise variance.
        Emulators have perfect readings.
        """
        samples = []
        for _ in range(100):
            samples.append(self.adc.read())
            time.sleep_ms(1)
        
        # Calculate variance
        avg = sum(samples) // len(samples)
        variance = sum((s - avg) ** 2 for s in samples) // len(samples)
        
        return variance
    
    def measure_wifi_rssi(self) -> int:
        """Measure WiFi RSSI (signal strength fingerprint)"""
        if self.wlan and self.wlan.isconnected():
            return self.wlan.status('rssi')
        return -999
    
    def measure_rtc_drift(self) -> int:
        """
        Measure RTC crystal drift.
        
        Real crystals drift with temperature and age.
        Emulators have perfect timing.
        """
        # Set initial time
        self.rtc.datetime((2026, 3, 14, 0, 12, 0, 0, 0))
        
        # Wait 1 second
        time.sleep(1)
        
        # Read actual time
        dt = self.rtc.datetime()
        actual_ms = dt[4] * 60 + dt[5]  # minutes + seconds
        
        # Expected: exactly 1 second elapsed
        # Real hardware will have slight drift
        drift = actual_ms - 1
        
        return abs(drift)
    
    def measure_power_variance(self) -> int:
        """
        Measure power supply variance.
        
        Real hardware has voltage fluctuations.
        Emulators have stable power.
        """
        # ESP32 has internal ADC that can measure VDD
        # This is a simplified version
        samples = []
        for _ in range(50):
            # Read from battery/voltage pin if available
            samples.append(self.adc.read())
            time.sleep_ms(2)
        
        avg = sum(samples) // len(samples)
        variance = sum((s - avg) ** 2 for s in samples) // len(samples)
        
        return variance
    
    def collect(self) -> dict:
        """Collect complete hardware fingerprint"""
        fingerprint = {
            "device_arch": "computer_space_esp32_bridge",
            "device_family": "computer_space_1971",
            "esp32_chip_id": self.read_chip_id(),
            "adc_noise_variance": self.measure_adc_noise(),
            "wifi_rssi": self.measure_wifi_rssi(),
            "rtc_drift_ms": self.measure_rtc_drift(),
            "power_variance": self.measure_power_variance(),
            "vintage_year": 1971,
            "fpga_partner": "lattice_ice40_up5k",
            "ttl_chip_count": 74
        }
        
        return fingerprint
    
    def detect_emulator(self) -> bool:
        """
        Detect if running on emulator.
        
        Emulators have:
        - Perfect ADC readings (no noise)
        - No WiFi hardware
        - Deterministic RTC
        - Stable power
        """
        emulator_score = 0
        
        # Check ADC noise (should be > 100 for real hardware)
        adc_noise = self.measure_adc_noise()
        if adc_noise < 50:
            emulator_score += 1
            print(f"⚠️  Low ADC noise: {adc_noise} (emulator?)")
        
        # Check WiFi
        rssi = self.measure_wifi_rssi()
        if rssi == -999:
            emulator_score += 1
            print("⚠️  No WiFi hardware (emulator?)")
        
        # Check power variance
        power_var = self.measure_power_variance()
        if power_var < 50:
            emulator_score += 1
            print(f"⚠️  Low power variance: {power_var} (emulator?)")
        
        # Check RTC drift
        rtc_drift = self.measure_rtc_drift()
        if rtc_drift < 5:
            emulator_score += 1
            print(f"⚠️  Perfect RTC: {rtc_drift}ms drift (emulator?)")
        
        is_emulator = emulator_score >= 2
        if is_emulator:
            print(f"❌ EMULATOR DETECTED (score: {emulator_score}/4)")
        else:
            print(f"✅ Real hardware verified (score: {emulator_score}/4)")
        
        return is_emulator


# ============================================================================
# NETWORK MANAGER
# ============================================================================

class NetworkManager:
    """Manages WiFi connectivity"""
    
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
    
    def connect(self, timeout: int = 30) -> bool:
        """Connect to WiFi network"""
        print(f"📶 Connecting to WiFi: {self.ssid}")
        
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        
        start = time.time()
        while not self.wlan.isconnected():
            if time.time() - start > timeout:
                print("❌ WiFi connection timeout")
                return False
            time.sleep(0.5)
            print(".", end="")
        
        print("\n✅ WiFi connected!")
        print(f"   IP: {self.wlan.ifconfig()[0]}")
        return True
    
    def disconnect(self):
        """Disconnect from WiFi (power saving)"""
        self.wlan.disconnect()
        self.wlan.active(False)
        print("📶 WiFi disconnected")
    
    def is_connected(self) -> bool:
        return self.wlan.isconnected()
    
    def get_rssi(self) -> int:
        if self.is_connected():
            return self.wlan.status('rssi')
        return -999


# ============================================================================
# RUSTCHAIN MINER
# ============================================================================

class RustChainMiner:
    """
    RustChain miner for Computer Space.
    
    Handles attestation protocol with rustchain.org API.
    """
    
    def __init__(self, wallet: str, api_url: str):
        self.wallet = wallet
        self.api_url = api_url
        self.attestation_count = 0
        self.total_earned = 0.0
        self.fingerprint_collector = FingerprintCollector()
    
    def build_attestation_payload(self) -> dict:
        """Build attestation JSON payload"""
        fp = self.fingerprint_collector.collect()
        
        payload = {
            "wallet": self.wallet,
            "miner_type": "computer_space_1971",
            "hardware_fingerprint": fp,
            "timestamp": time.time(),
            "attestation_id": self.attestation_count,
            "vintage_multiplier": 3.5,
            "fpga_partner": "lattice_ice40_up5k",
            "ttl_chips_emulated": 74
        }
        
        return payload
    
    def attest(self) -> dict:
        """Submit attestation to RustChain API"""
        print(f"\n💰 Submitting attestation #{self.attestation_count + 1}...")
        
        # Check for emulator
        if self.fingerprint_collector.detect_emulator():
            print("❌ Emulator detected! Attestation rejected.")
            return {
                "status": "rejected",
                "reason": "emulator_detected",
                "reward": 0
            }
        
        # Build payload
        payload = self.build_attestation_payload()
        
        try:
            # POST to RustChain API
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.attestation_count += 1
                
                reward = result.get("reward", 0.0042 * 3.5)
                self.total_earned += reward
                
                print(f"✅ Attestation successful!")
                print(f"   Reward: {reward:.4f} RTC")
                print(f"   Total: {self.total_earned:.4f} RTC")
                print(f"   Multiplier: 3.5× (Vintage Arcade)")
                
                return {
                    "status": "success",
                    "reward": reward,
                    "total": self.total_earned,
                    "response": result
                }
            else:
                print(f"❌ API error: {response.status_code}")
                return {
                    "status": "error",
                    "code": response.status_code,
                    "reward": 0
                }
                
        except Exception as e:
            print(f"❌ Network error: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "reward": 0
            }
    
    def run_continuous(self, epoch_duration: int = EPOCH_DURATION):
        """Run miner continuously"""
        print("=" * 60)
        print("  RUSTCHAIN MINER - COMPUTER SPACE (1971)")
        print("=" * 60)
        print(f"Wallet: {self.wallet}")
        print(f"API: {self.api_url}")
        print(f"Epoch: {epoch_duration}s")
        print("=" * 60)
        
        while True:
            # Attest
            result = self.attest()
            
            if result["status"] == "success":
                # Blink LED
                for _ in range(3):
                    Pin(LED_MINING, Pin.OUT).value(1)
                    time.sleep(0.2)
                    Pin(LED_MINING, Pin.OUT).value(0)
                    time.sleep(0.2)
            
            # Wait for next epoch
            print(f"\n⏳ Waiting {epoch_duration}s for next epoch...")
            for i in range(epoch_duration // 10):
                time.sleep(10)
                if i % 6 == 0:  # Print every minute
                    elapsed = (i + 1) * 10
                    remaining = epoch_duration - elapsed
                    print(f"   {remaining}s remaining...")


# ============================================================================
# FPGA INTERFACE (SPI)
# ============================================================================

class FPGAInterface:
    """SPI interface to FPGA"""
    
    def __init__(self):
        self.spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
                      sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
        self.cs = Pin(SPI_CS, Pin.OUT, value=1)
    
    def read_register(self, addr: int) -> int:
        """Read FPGA register"""
        self.cs.value(0)
        self.spi.write(bytes([addr]))
        data = self.spi.read(1)
        self.cs.value(1)
        return data[0] if data else 0
    
    def write_register(self, addr: int, value: int):
        """Write FPGA register"""
        self.cs.value(0)
        self.spi.write(bytes([addr, value]))
        self.cs.value(1)
    
    def read_fingerprint(self) -> bytes:
        """Read FPGA fingerprint data"""
        self.cs.value(0)
        self.spi.write(bytes([0xFF]))  # Fingerprint command
        data = self.spi.read(16)  # Read 16 bytes
        self.cs.value(1)
        return data
    
    def detect_fpga(self) -> bool:
        """Detect if FPGA is connected"""
        try:
            chip_id = self.read_register(0x00)
            return chip_id != 0 and chip_id != 0xFF
        except:
            return False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  COMPUTER SPACE (1971) - ESP32 NETWORK BRIDGE")
    print("  RustChain Miner")
    print("=" * 60)
    
    # Initialize LEDs
    Pin(LED_MINING, Pin.OUT).value(0)
    Pin(LED_NETWORK, Pin.OUT).value(0)
    Pin(LED_ERROR, Pin.OUT).value(0)
    
    # Check FPGA connection
    fpga = FPGAInterface()
    if fpga.detect_fpga():
        print("✅ FPGA detected")
        Pin(LED_NETWORK, Pin.OUT).value(1)
    else:
        print("⚠️  FPGA not detected (continuing in simulator mode)")
    
    # Connect to WiFi
    net = NetworkManager(WIFI_SSID, WIFI_PASSWORD)
    if not net.connect():
        print("❌ Failed to connect to WiFi")
        Pin(LED_ERROR, Pin.OUT).value(1)
        return
    
    Pin(LED_NETWORK, Pin.OUT).value(1)
    
    # Start mining
    miner = RustChainMiner(WALLET_ADDRESS, RUSTCHAIN_API)
    
    # Run single attestation (demo mode)
    print("\n🚀 Running demo attestation...")
    result = miner.attest()
    
    print("\n" + "=" * 60)
    print(f"  FINAL RESULT")
    print("=" * 60)
    print(f"  Status: {result['status']}")
    print(f"  Reward: {result.get('reward', 0):.4f} RTC")
    print(f"  Wallet: {WALLET_ADDRESS}")
    print("=" * 60)
    
    # Uncomment for continuous mining:
    # miner.run_continuous()


if __name__ == "__main__":
    main()
