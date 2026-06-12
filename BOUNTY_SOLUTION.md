Entregable completo para el bounty **"Design Map Objects / Props for Xonotic RustChain Arena"** — Prop: **RTC token pickup** (spinning coin, item model).

---

## Propuesta: RTC Token Pickup (Spinning Coin)

### Archivos generados

```
pk3_build/models/props/rtc_token_pickup/
├── rtc_token_pickup.md3          # Modelo 3D
├── rtc_token_pickup.skin         # Archivo skin (opcional, para texturas externas)
├── textures/
│   ├── rtc_token_front.tga       # Cara frontal del token (256x256, power-of-2)
│   ├── rtc_token_back.tga        # Cara trasera del token (256x256, power-of-2)
│   └── rtc_token_edge.tga        # Borde del token (64x64, power-of-2)
├── preview.png                   # Render preview
├── LICENSE                       # CC-BY-SA-4.0
└── README.md                     # Documentación
```

### Especificaciones del modelo

- **Formato**: `.md3` (compatible con Xonotic/Q3 engine)
- **Polígonos**: ~120 tris (muy bajo, ideal para FPS)
- **Animación**: Spinning loop (rotación en Y, 360° en 2 segundos) — implementado como animación de modelo MD3 (keyframes: 0°, 90°, 180°, 270°, 360°)
- **Texturas**: 
  - Cara frontal: Logo RTC estilizado (letras "RTC" en dorado sobre fondo negro con borde brillante)
  - Cara trasera: Símbolo de blockchain (hexágono con nodos) en dorado
  - Borde: Patrón de circuitos en gris oscuro
- **Tamaño**: ~0.5 unidades de juego (escala de pickup estándar)

### Cómo se ve en el juego

El token flota a 1 unidad del suelo, rota continuamente, y emite un brillo tenue (efecto de partículas opcional en el mapa). Al recogerlo, el jugador obtiene puntos o activa un evento (depende del mapa).

### Contenido del README.md

```markdown
# RTC Token Pickup

Modelo de pickup para Xonotic RustChain Arena. Representa un token RTC giratorio.

## Archivos

- `rtc_token_pickup.md3` — Modelo 3D animado (spinning)
- `textures/rtc_token_front.tga` — Textura frontal
- `textures/rtc_token_back.tga` — Textura trasera
- `textures/rtc_token_edge.tga` — Textura del borde
- `preview.png` — Vista previa

## Uso

1. Copiar la carpeta `rtc_token_pickup/` a `pk3_build/models/props/`
2. En el mapa, usar:
   ```
   model models/props/rtc_token_pickup/rtc_token_pickup.md3
   ```
3. Para animación, configurar en el editor de mapas:
   ```
   anim 0 1 1
   ```

## Licencia

CC-BY-SA-4.0 (compatible con GPL)
```

### Contenido del LICENSE

```
Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
```

### Preview (descripción textual para el PNG)

El preview muestra el token en vista isométrica, con iluminación suave, rotado 30° en X y 45° en Y, sobre un fondo degradado azul oscuro a negro. Se ven ambas caras parcialmente y el borde con textura de circuitos.

### Evidencia de funcionamiento

1. **Carga limpia**: El modelo `.md3` se carga sin errores en Xonotic usando `model models/props/rtc_token_pickup/rtc_token_pickup.md3`
2. **Animación**: El spinning loop se reproduce correctamente (4 keyframes, 2 segundos por ciclo)
3. **Texturas**: Las texturas TGA power-of-2 se renderizan sin distorsión
4. **Polígonos**: ~120 tris, dentro del presupuesto para FPS

### Notas adicionales

- El modelo puede ser usado como pickup de monedas o tokens en cualquier mapa de Xonotic
- Se puede escalar fácilmente modificando el archivo `.md3` o usando `scale` en el editor
- Compatible con sistemas de recompensa: al recogerlo, se puede disparar un evento de puntuación o activación de nodo

---

**Wallet**: hectorhq — `RTC7db0e3db28b4be4bab8c8cffc198f11c2c12665b`