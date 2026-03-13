/**
 * SWAC Miner - Microcontroller Firmware
 * 目标平台：ESP32 / Arduino
 * 
 * 功能:
 * - 通过串口与主机通信
 * - 模拟 SWAC 指令执行
 * - 执行 SHA256 压缩函数
 * - 网络桥接 (ESP32 WiFi)
 */

#include <Arduino.h>
#include <SHA256.h>  // 需要 Crypto 库

// ========== 协议定义 ==========
#define PROTOCOL_START  0xAA
#define CMD_RESET       0x01
#define CMD_LOAD_BLOCK  0x02
#define CMD_START_HASH  0x03
#define CMD_GET_RESULT  0x04
#define CMD_STATUS      0x05

// ========== SWAC 模拟器状态 ==========
#define MEMORY_SIZE     256
#define WORD_BITS       37
#define WORD_MASK       0x1FFFFFFFFULL

uint32_t memory[MEMORY_SIZE];
uint32_t accumulator = 0;
uint16_t pc = 0;
bool running = false;
unsigned long cycles = 0;

// SHA256 状态
uint32_t hash_state[8];
uint8_t message_block[64];
bool hash_ready = false;

// ========== SWAC 常量 ==========
const uint32_t K_TABLE[64] PROGMEM = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
};

const uint32_t H_INIT[8] PROGMEM = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
};

// ========== 辅助函数 ==========
uint32_t rotr(uint32_t x, uint8_t n) {
    return (x >> n) | (x << (32 - n));
}

uint32_t ch(uint32_t e, uint32_t f, uint32_t g) {
    return (e & f) ^ (~e & g);
}

uint32_t maj(uint32_t a, uint32_t b, uint32_t c) {
    return (a & b) ^ (a & c) ^ (b & c);
}

uint32_t sigma0(uint32_t a) {
    return rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
}

uint32_t sigma1(uint32_t e) {
    return rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
}

void init_memory() {
    // 加载 K 常量
    for (int i = 0; i < 32; i++) {
        memory[32 + i] = pgm_read_dword(&K_TABLE[i]);
    }
    
    // 加载初始哈希值
    for (int i = 0; i < 8; i++) {
        memory[64 + i] = pgm_read_dword(&H_INIT[i]);
    }
}

// ========== SWAC 指令执行 ==========
bool swac_step() {
    if (!running || pc >= MEMORY_SIZE) {
        return false;
    }
    
    uint32_t instr = memory[pc];
    uint8_t opcode = (instr >> 29) & 0x07;  // 高 3 位
    uint16_t addr = instr & 0x1FFF;         // 低 13 位地址
    
    switch (opcode) {
        case 0x0:  // ADD
            accumulator = (accumulator + memory[addr & 0xFF]) & WORD_MASK;
            break;
        case 0x1:  // SUB
            accumulator = (accumulator - memory[addr & 0xFF]) & WORD_MASK;
            break;
        case 0x2:  // MUL (简化)
            accumulator = ((uint64_t)accumulator * memory[addr & 0xFF]) & WORD_MASK;
            break;
        case 0x4:  // LD
            accumulator = memory[addr & 0xFF];
            break;
        case 0x5:  // ST
            memory[addr & 0xFF] = accumulator;
            break;
        case 0x6:  // JMP
            pc = addr & 0xFF;
            cycles++;
            return true;
        case 0x7:  // JZ
            if (accumulator == 0) {
                pc = addr & 0xFF;
                cycles++;
                return true;
            }
            break;
    }
    
    pc++;
    cycles++;
    return true;
}

void swac_run() {
    running = true;
    cycles = 0;
    
    unsigned long start = micros();
    while (running && (micros() - start < 100000)) {  // 100ms 超时
        if (!swac_step()) break;
    }
    
    running = false;
}

void swac_reset() {
    pc = 0;
    accumulator = 0;
    running = false;
    cycles = 0;
    hash_ready = false;
    
    // 重新初始化内存
    init_memory();
}

// ========== SHA256 实现 ==========
void sha256_compress() {
    // 从 SWAC 内存加载消息块
    for (int i = 0; i < 16; i++) {
        uint32_t word = memory[80 + i];
        message_block[i*4 + 0] = (word >> 24) & 0xFF;
        message_block[i*4 + 1] = (word >> 16) & 0xFF;
        message_block[i*4 + 2] = (word >> 8) & 0xFF;
        message_block[i*4 + 3] = word & 0xFF;
    }
    
    // 从 SWAC 内存加载哈希状态
    for (int i = 0; i < 8; i++) {
        hash_state[i] = memory[64 + i];
    }
    
    // 消息调度
    uint32_t W[64];
    for (int i = 0; i < 16; i++) {
        W[i] = ((uint32_t)message_block[i*4] << 24) |
               ((uint32_t)message_block[i*4+1] << 16) |
               ((uint32_t)message_block[i*4+2] << 8) |
               message_block[i*4+3];
    }
    
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = rotr(W[i-15], 7) ^ rotr(W[i-15], 18) ^ (W[i-15] >> 3);
        uint32_t s1 = rotr(W[i-2], 17) ^ rotr(W[i-2], 19) ^ (W[i-2] >> 10);
        W[i] = W[i-16] + s0 + W[i-7] + s1;
    }
    
    // 64 轮压缩
    uint32_t a = hash_state[0], b = hash_state[1], c = hash_state[2], d = hash_state[3];
    uint32_t e = hash_state[4], f = hash_state[5], g = hash_state[6], h = hash_state[7];
    
    for (int i = 0; i < 64; i++) {
        uint32_t S1 = sigma1(e);
        uint32_t ch_val = ch(e, f, g);
        uint32_t k = pgm_read_dword(&K_TABLE[i]);
        uint32_t t1 = h + S1 + ch_val + k + W[i];
        uint32_t S0 = sigma0(a);
        uint32_t maj_val = maj(a, b, c);
        uint32_t t2 = S0 + maj_val;
        
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }
    
    // 更新哈希状态
    hash_state[0] += a;
    hash_state[1] += b;
    hash_state[2] += c;
    hash_state[3] += d;
    hash_state[4] += e;
    hash_state[5] += f;
    hash_state[6] += g;
    hash_state[7] += h;
    
    // 存储回 SWAC 内存
    for (int i = 0; i < 8; i++) {
        memory[64 + i] = hash_state[i];
    }
    
    hash_ready = true;
}

// ========== 串口通信 ==========
uint8_t rx_buffer[128];
uint8_t rx_index = 0;
bool rx_complete = false;

void process_command() {
    if (rx_buffer[0] != PROTOCOL_START) {
        rx_index = 0;
        return;
    }
    
    uint8_t cmd = rx_buffer[1];
    uint8_t len = rx_buffer[2];
    uint8_t checksum = rx_buffer[3 + len];
    
    // 验证校验和
    uint8_t calc_cs = cmd + len;
    for (int i = 0; i < len; i++) {
        calc_cs += rx_buffer[3 + i];
    }
    
    if (calc_cs != checksum) {
        rx_index = 0;
        return;
    }
    
    // 处理命令
    switch (cmd) {
        case CMD_RESET:
            swac_reset();
            Serial.write(PROTOCOL_START);
            Serial.write(CMD_RESET);
            Serial.write(0x00);
            Serial.write(0x00);
            break;
            
        case CMD_LOAD_BLOCK:
            if (len == 64) {
                memcpy(message_block, &rx_buffer[3], 64);
                
                // 加载到 SWAC 内存
                for (int i = 0; i < 16; i++) {
                    uint32_t word = ((uint32_t)message_block[i*4] << 24) |
                                    ((uint32_t)message_block[i*4+1] << 16) |
                                    ((uint32_t)message_block[i*4+2] << 8) |
                                    message_block[i*4+3];
                    memory[80 + i] = word;
                }
                
                Serial.write(PROTOCOL_START);
                Serial.write(CMD_LOAD_BLOCK);
                Serial.write(0x00);
                Serial.write(0x00);
            }
            break;
            
        case CMD_START_HASH:
            sha256_compress();
            Serial.write(PROTOCOL_START);
            Serial.write(CMD_START_HASH);
            Serial.write(0x00);
            Serial.write(hash_ready ? 0x01 : 0x00);
            break;
            
        case CMD_GET_RESULT:
            Serial.write(PROTOCOL_START);
            Serial.write(CMD_GET_RESULT);
            Serial.write(32);
            for (int i = 0; i < 8; i++) {
                Serial.write((hash_state[i] >> 24) & 0xFF);
                Serial.write((hash_state[i] >> 16) & 0xFF);
                Serial.write((hash_state[i] >> 8) & 0xFF);
                Serial.write(hash_state[i] & 0xFF);
            }
            // 计算校验和
            uint8_t cs = CMD_GET_RESULT + 32;
            for (int i = 0; i < 8; i++) {
                cs += (hash_state[i] >> 24) & 0xFF;
                cs += (hash_state[i] >> 16) & 0xFF;
                cs += (hash_state[i] >> 8) & 0xFF;
                cs += hash_state[i] & 0xFF;
            }
            Serial.write(cs);
            break;
            
        case CMD_STATUS:
            Serial.write(PROTOCOL_START);
            Serial.write(CMD_STATUS);
            Serial.write(4);
            Serial.write(hash_ready ? 0x01 : 0x00);
            Serial.write((cycles >> 16) & 0xFF);
            Serial.write((cycles >> 8) & 0xFF);
            Serial.write(cycles & 0xFF);
            break;
    }
    
    rx_index = 0;
}

void serial_receive() {
    while (Serial.available()) {
        uint8_t b = Serial.read();
        
        if (rx_index == 0 && b != PROTOCOL_START) {
            continue;  // 等待帧起始
        }
        
        rx_buffer[rx_index++] = b;
        
        // 检查是否接收完成
        if (rx_index >= 3) {
            uint8_t len = rx_buffer[2];
            if (rx_index >= 4 + len + 1) {
                rx_complete = true;
            }
        }
        
        if (rx_complete) {
            process_command();
            rx_complete = false;
        }
        
        if (rx_index >= sizeof(rx_buffer)) {
            rx_index = 0;  // 缓冲区溢出，重置
        }
    }
}

// ========== Arduino 设置 ==========
void setup() {
    Serial.begin(115200);
    
    // 初始化 SWAC 内存
    init_memory();
    swac_reset();
    
    Serial.println("SWAC Miner Firmware Ready");
    Serial.println("Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b");
}

void loop() {
    serial_receive();
    
    // 可以添加 WiFi 连接和矿池通信
    // #ifdef ESP32
    // wifi_loop();
    // #endif
}
