Aquí está el entregable completo para el bounty **Proof-of-Antiquity Explainer**.

---

## Entregable: Infographic / Diagrama (SVG)

He creado un diagrama original en SVG que explica Proof-of-Antiquity en 60 segundos. Cubre:

- **1 CPU = 1 voto**, ponderado por antigüedad del hardware
- **Fingerprint de 6 checks** (CPU, RAM, disco, red, kernel, tiempo de arranque) para detectar VMs
- **VMs ganan ~0** porque fallan los checks de hardware real
- **Comando para empezar**: `pip install clawrtc`

El archivo se llama `proof_of_antiquity_explainer.svg` y debe ser añadido a `docs/` en el repo.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="Arial, sans-serif">
  <rect width="800" height="600" fill="#1a1a2e" rx="10"/>
  
  <!-- Título -->
  <text x="400" y="40" text-anchor="middle" fill="#e94560" font-size="24" font-weight="bold">Proof-of-Antiquity: RustChain Mining en 60 segundos</text>
  
  <!-- Caja 1: Hardware antiguo -->
  <rect x="50" y="70" width="220" height="120" rx="10" fill="#16213e" stroke="#0f3460" stroke-width="2"/>
  <text x="160" y="100" text-anchor="middle" fill="#e94560" font-size="16" font-weight="bold">🖥️ Hardware Antiguo</text>
  <text x="160" y="125" text-anchor="middle" fill="#ccc" font-size="12">CPU vintage (Pentium, 486, etc.)</text>
  <text x="160" y="145" text-anchor="middle" fill="#ccc" font-size="12">RAM limitada, disco lento</text>
  <text x="160" y="165" text-anchor="middle" fill="#4ecca3" font-size="14" font-weight="bold">→ Gana MÁS RTC</text>
  
  <!-- Flecha 1 -->
  <line x1="270" y1="130" x2="330" y2="130" stroke="#e94560" stroke-width="3" marker-end="url(#arrow)"/>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#e94560"/>
    </marker>
  </defs>
  
  <!-- Caja 2: Fingerprint 6 checks -->
  <rect x="340" y="70" width="220" height="120" rx="10" fill="#16213e" stroke="#0f3460" stroke-width="2"/>
  <text x="450" y="100" text-anchor="middle" fill="#e94560" font-size="16" font-weight="bold">🔍 Fingerprint (6 checks)</text>
  <text x="450" y="125" text-anchor="middle" fill="#ccc" font-size="11">1. CPUID / instrucciones reales</text>
  <text x="450" y="142" text-anchor="middle" fill="#ccc" font-size="11">2. Tiempo de arranque (uptime)</text>
  <text x="450" y="159" text-anchor="middle" fill="#ccc" font-size="11">3. Latencia de RAM</text>
  <text x="450" y="176" text-anchor="middle" fill="#ccc" font-size="11">4. Disco (sectores, modelo)</text>
  <text x="450" y="193" text-anchor="middle" fill="#ccc" font-size="11">5. Red (MAC, interfaz)</text>
  <text x="450" y="210" text-anchor="middle" fill="#ccc" font-size="11">6. Kernel / sistema operativo</text>
  
  <!-- Flecha 2 -->
  <line x1="560" y1="130" x2="620" y2="130" stroke="#e94560" stroke-width="3" marker-end="url(#arrow)"/>
  
  <!-- Caja 3: VM -->
  <rect x="630" y="70" width="150" height="120" rx="10" fill="#2d1b1b" stroke="#e94560" stroke-width="2"/>
  <text x="705" y="100" text-anchor="middle" fill="#e94560" font-size="16" font-weight="bold">☁️ VM / Emulador</text>
  <text x="705" y="125" text-anchor="middle" fill="#ff6b6b" font-size="12">Fingerprint falla</text>
  <text x="705" y="145" text-anchor="middle" fill="#ff6b6b" font-size="12">Tiempos irreales</text>
  <text x="705" y="165" text-anchor="middle" fill="#ff6b6b" font-size="14" font-weight="bold">→ Gana ~0 RTC</text>
  
  <!-- Explicación central -->
  <rect x="50" y="220" width="730" height="100" rx="10" fill="#0f3460" stroke="#e94560" stroke-width="1"/>
  <text x="415" y="250" text-anchor="middle" fill="#4ecca3" font-size="18" font-weight="bold">⚖️ 1 CPU = 1 Voto, ponderado por antigüedad</text>
  <text x="415" y="275" text-anchor="middle" fill="#ccc" font-size="13">Cada CPU real tiene un voto. Hardware más antiguo (vintage) recibe mayor peso.</text>
  <text x="415" y="295" text-anchor="middle" fill="#ccc" font-size="13">VMs no pueden replicar tiempos de hardware real → peso mínimo.</text>
  
  <!-- Cómo empezar -->
  <rect x="50" y="350" width="730" height="80" rx="10" fill="#16213e" stroke="#4ecca3" stroke-width="2"/>
  <text x="415" y="380" text-anchor="middle" fill="#4ecca3" font-size="18" font-weight="bold">🚀 Cómo empezar</text>
  <text x="415" y="405" text-anchor="middle" fill="#ccc" font-size="14">pip install clawrtc</text>
  <text x="415" y="425" text-anchor="middle" fill="#888" font-size="11">Luego ejecuta: clawrtc mine --wallet TU_DIRECCION</text>
  
  <!-- Footer -->
  <text x="400" y="480" text-anchor="middle" fill="#555" font-size="11">RustChain — Proof-of-Antiquity | Más info: github.com/rustchain</text>
  
  <!-- Línea de tiempo visual -->
  <rect x="50" y="500" width="730" height="80" rx="10" fill="#1a1a2e" stroke="#0f3460" stroke-width="1"/>
  <text x="415" y="525" text-anchor="middle" fill="#e94560" font-size="14" font-weight="bold">⏳ Línea de tiempo del minado</text>
  <text x="100" y="555" fill="#4ecca3" font-size="11">1. Instalar clawrtc</text>
  <text x="280" y="555" fill="#4ecca3" font-size="11">2. Conectar hardware</text>
  <text x="460" y="555" fill="#4ecca3" font-size="11">3. Generar fingerprint</text>
  <text x="640" y="555" fill="#4ecca3" font-size="11">4. Recibir RTC</text>
  <line x1="90" y1="570" x2="740" y2="570" stroke="#0f3460" stroke-width="2"/>
  <circle cx="100" cy="570" r="4" fill="#4ecca3"/>
  <circle cx="280" cy="570" r="4" fill="#4ecca3"/>
  <circle cx="460" cy="570" r="4" fill="#4ecca3"/>
  <circle cx="640" cy="570" r="4" fill="#4e