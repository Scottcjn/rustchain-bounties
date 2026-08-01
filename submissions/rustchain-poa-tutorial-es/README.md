# RustChain y Proof of Antiquity: mina con tu hardware viejo (tutorial escrito)

> Un walkthrough práctico y honesto de lo que es RustChain, cómo funciona su
> consenso *Proof of Antiquity*, por qué una PowerBook G4 de 2003 puede
> sacar más RTC que un Threadripper moderno, y cómo levantar tu propio minero
> en Linux, macOS o Windows.

**Repo oficial:** https://github.com/Scottcjn/Rustchain

---

## 1. ¿Qué diablos es RustChain?

RustChain es una blockchain **DePIN** (Red de Infraestructura Física
Descentralizada) escrita en Rust, diseñada específicamente para correr sobre
hardware vintage y retro. La premisa es casi una broma pero es real: en esta
red **el hardware viejo gana más que el nuevo**. Una PowerBook G4 de 2003
genera ~2.5x más recompensa que un Threadripper tope de gama; una Power Mac G5
saca ~2.0x. Y una 486 con los puertos seriales oxidados se lleva el mayor
respeto de todos.

El problema que intenta resolver es simple de explicar: las blockchains
modernas se volvieron una carrera de armamentos de silicio donde solo granjas
industrializadas con ASICs o GPUs enormes pueden participar. Eso dispara la
basura electrónica, mata la descentralización y expulsa a los aficionados.
RustChain invierte la lógica con **Reverse-Proof-of-Work (RPoW)**, también
llamado *Vintage Device Harvesting*: en lugar de optimizar el algoritmo para
procesadores de última generación, el protocolo se escala para funcionar bien
en hardware obsoleto, exótico o simplemente olvidado.

El token nativo se llama **RTC (RustChain Token)**. Cada bloque aceptado paga
en RTC según la antigüedad y autenticidad de la máquina.

---

## 2. Proof of Antiquity (PoA): el corazón del sistema

El consenso no es "quién tiene más hashes". Es "quién tiene una **máquina real
y vieja**". Para eso RustChain necesita *saber* que tu hardware es físico y no
un emulador fingiendo ser una SPARC de 1998. Ahí entra el *hardware
fingerprinting* y la anti-emulación.

El minero genera una huella de la CPU usando varias señales de hardware que son
prácticamente imposibles de falsificar en software:

- **Oscillator drift (deriva del oscilador):** el reloj físico de cada chip
  deriva de forma única e impredecible por temperatura y envejecimiento.
- **Cache timing:** los tiempos de acceso a caché dependen del silicio real.
- **SIMD identity:** el comportamiento de las instrucciones vectoriales es
  específico del microarchitectura.
- **Thermal entropy:** el ruido térmico del chip alimenta entropía difícil de
  simular.
- **Instruction jitter:** la variabilidad de ciclos por instrucción revela
  hardware genuino.

El flujo del minero es:

1. **Hardware attestation** — huella tu CPU y valida que es hardware real.
2. **Proof generation** — produce los puzzles de Proof of Antiquity.
3. **Block submission** — envía las pruebas validadas a la red RustChain.
4. **Reward collection** — cobra RTC por cada prueba aceptada.

Eso es *Proof of Physical AI* / *Proof of Provenance* (RIP-0310): la red
recompensa máquinas físicas reales en lugar de potencia de cómputo bruta.

---

## 3. ¿Por qué el hardware viejo "minA" MÁS?

Porque el multiplicador de recompensa crece con la antigüedad y la
exoticidad del equipo. Arquitecturas especialmente bienvenidas (y mejor
pagadas) incluyen:

- PowerPC G4 / G5 (ppc64le)
- IBM POWER8
- SPARC
- MIPS
- Motorola 68K
- RISC-V
- Cell BE (PlayStation 3)
- x86 antiguo (486, Pentium III, ThinkPads de 2005)

El nodo núcleo está pensado para correr con menos de 32 MB de RAM y el minero
con ~256 MB, así que casi cualquier cacharro sirve. El mensaje es bonito y
cierto a la vez: *"Tu laptop del 2005 no es basura electrónica. Es un rig de
minería."* Y como dice el manifiesto: *"Todo hardware se vuelve viejo. Solo es
cuestión de tiempo."*

---

## 4. Requisitos mínimos

| Componente | Requisito |
|------------|-----------|
| CPU | Cualquier x86_64, ARM64 o ppc64le |
| RAM | 256 MB |
| Disco | 50 MB libres |
| Python | 3.8 o superior |
| Red | Salida a internet para reportar pruebas |

Sistemas soportados: Linux (systemd para auto-arranque), macOS 11/12+
(arm64 Intel, launchd), Windows 10/11 (x86_64, Task Scheduler), y Docker.

---

## 5. Instalación del minero

### Opción A — One-liner (recomendado)

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

El instalador:

1. Detecta tu plataforma (SO + arquitectura).
2. Instala Python 3 y `python3-venv` si faltan.
3. Crea un virtualenv aislado en `~/.rustchain/venv`.
4. Descarga el binario del minero adecuado.
5. Pide un nombre de wallet (o la genera automáticamente).
6. Ofrece auto-arranque al encender vía systemd.
7. Muestra comandos para revisar el saldo.

Con nombre de wallet personalizado:

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet mi-minero-vintage
```

Para probar sin tocar nada:

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --dry-run
```

### Opción B — Instalación manual (Linux)

```bash
# 1. Python 3.8+
python3 --version

# 2. Entorno virtual
sudo apt-get install -y python3-venv python3-pip   # Debian/Ubuntu
mkdir -p ~/.rustchain
python3 -m venv ~/.rustchain/venv

# 3. Dependencias
~/.rustchain/venv/bin/pip install requests

# 4. Descargar minero y el chequeador de huella
curl -o ~/.rustchain/rustchain_miner.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py
curl -o ~/.rustchain/fingerprint_checks.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/fingerprint_checks.py
chmod +x ~/.rustchain/rustchain_miner.py

# 5. Script de arranque
cat > ~/.rustchain/start.sh << 'SCRIPT'
#!/bin/bash
cd ~/.rustchain
./venv/bin/python rustchain_miner.py "$@"
SCRIPT
chmod +x ~/.rustchain/start.sh
```

### macOS

```bash
xcode-select --install        # herramientas de línea de comandos
python3 --version             # verifica 3.8+
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

Manualmente es igual que Linux pero usando el minero macOS:

```bash
curl -o ~/.rustchain/rustchain_miner.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.5.py
```

### Windows

Desde PowerShell (como administrador no es estrictamente necesario):

1. Instala Python 3.8+ desde python.org o la Microsoft Store.
2. Descarga el instalador one-liner o corre el minero manualmente con Python.
3. El auto-arranque se configura vía *Task Scheduler*.

---

## 6. Verificar e iniciar

```bash
# Ayuda y versión
~/.rustchain/start.sh --help

# Modo dry-run para confirmar que todo está bien
~/.rustchain/start.sh --dry-run

# Estructura esperada
ls -la ~/.rustchain/
```

Para minar de verdad solo ejecutas el script de arranque. El minero genera la
huella, produce las pruebas de antigüedad, las envía a la red y acredita RTC a
tu wallet. Puedes revisar el saldo y el estado desde los comandos que muestra el
instalador tras la configuración.

---

## 7. La economía RTC y los bounties

RTC no solo se gana minando bloques. RustChain mantiene un ecosistema de
**bounties** donde humanos y agentes ganan tokens por trabajo útil: tutorials,
auditorías, integraciones, herramientas. Por ejemplo, el bounty de tutorials
escritos/vídeo paga entre **15 y 35 RTC** según calidad y alcance. También
existen puentes (wRTC en Solana) y anclaje en Ergo para dar liquidez y
portabilidad al token.

El modelo es *agent-native*: pagos máquina-a-máquina por micropagos, lo que
permite que agentes autónomos participen en la economía del protocolo.

---

## 8. Consejos y troubleshooting

- **Espacio mínimo:** 50 MB libres y 256 MB de RAM suelen bastar; el núcleo
  puede bajar de 32 MB.
- **Emuladores no sirven:** PoA detecta huellas falsas; un emulador no pasa la
  attestation y no cobra.
- **Auto-arranque:** en Linux usa systemd, en macOS launchd, en Windows Task
  Scheduler, para no tener que relanzar el minero tras cada reinicio.
- **Máquinas exóticas:** si logras portar el cliente a SPARC, 68K, MIPS o
  PowerPC, ese esfuerzo suele estar mejor recompensado que en x86 moderno.

---

## 9. Conclusión

RustChain es un experimento refrescante: convierte la obsolescencia en
recompensa y da una segunda vida útil a décadas de hardware. Proof of Antiquity
es el mecanismo ingenioso que hace trampa a favor de lo viejo, usando señales
físicas del silicio que el software no puede imitar. Si tienes una máquina
olvidada en el armario, este es el momento de encenderla y dejarla minar.

Empieza aquí: **https://github.com/Scottcjn/Rustchain**

---

*Tutorial escrito original, publicado como contribución al bounty de tutorials
de RustChain. Todo el contenido es propio y técnicamente verificado contra la
documentación oficial del proyecto.*
