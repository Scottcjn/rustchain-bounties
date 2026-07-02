# GUÍA MAESTRA DE EJECUCIÓN: DESARROLLO DIRIGIDO POR ESPECIFICACIONES (SDD) + MCP

Esta guía define el flujo operativo estándar para abordar cualquier Issue o Recompensa (Bounty) utilizando ingeniería de prompts, automatización de contexto mediante MCP (Context7) y el entorno OpenCode.

---

## 🛠️ CONFIGURACIÓN INICIAL DEL ENTORNO (Una vez por proyecto)

1. **Clonación:** Clonar el repositorio objetivo localmente.
2. **Conexión MCP (Context7):** 
   - Abrir la configuración de herramientas/MCP en el entorno OpenCode.
   - Asegurar que el servidor MCP de `Context7` esté activo y apuntando al backend del proveedor para inyectar documentación en tiempo real.
3. **Despliegue de Estructura:** Crear en la raíz las carpetas `/spec/constitution/`, `/spec/features/` y `/docs/sessions/`, `/docs/changelogs/`.

---

## 🧠 HABILIDADES DEL AGENTE
Este agente opera bajo las habilidades definidas en `.opencode/skills/fullstack-dev/`. Estas habilidades garantizan el enfoque SDD (Arquitectura-First), el uso de MCP (Context7) y estándares de desarrollo Full-Stack.

---

## ⚠️ RECOMENDACIONES CRÍTICAS (Mantenimiento de Control)

1. **La `spec` es tu escudo:** Si el agente intenta saltarse pasos o implementar algo no definido en `spec/features/.../plan.md`, detén la ejecución. **Si no está en el plan, no debe estar en el código.**
2. **Atomicidad real:** En `tasks.md`, asegúrate de que cada tarea termine con un test de verificación (unitario o funcional). No des por terminada una tarea hasta que el agente muestre el resultado positivo del test.
3. **Higiene de Contexto:** Al cambiar de repositorio o iniciar un nuevo issue, ejecuta `/init` nuevamente para que el agente refresque su memoria y cree el contexto necesario en `AGENTS.md`.

---

## 🚀 FLUJO DE TRABAJO PASO A PASO

Para cada repositorio, sigue este ciclo obligatorio. **No intentes saltar fases**. La calidad de tu código depende de la fidelidad a este proceso.

### FASE 0: Inicialización (Solo al clonar el repo)
1. Entra a la carpeta del proyecto.
2. Ejecuta `/init`. Esto crea el contexto necesario (`AGENTS.md`).
3. Verifica que la estructura SDD (`/spec/`, `/docs/`) esté creada en la raíz.

### FASE 1: Constitución del Ecosistema (Solo al empezar el repo)
*Objetivo: Que el agente entienda el proyecto.*
Pega este prompt:
> "Actúa como un Ingeniero de Software Experto. Analiza el repositorio actual usando tus herramientas de exploración de archivos. Investiga el stack tecnológico y las dependencias principales usando el MCP de Context7 si es necesario. Completa los archivos `spec/constitution/tech-stack.md`, `mission.md` y `roadmap.md` mapeando la arquitectura del proyecto y los objetivos de desarrollo."
*Espera a que termine y revisa los 3 archivos.*

---

*(De aquí en adelante, repite este ciclo por cada ISSUE o TAREA)*

---

### FASE 2: Especificación y Anclaje
*Objetivo: Definir el "QUÉ" y el "CÓMO" para un issue concreto.*
1. Crea la carpeta: `/spec/features/nombre-de-la-tarea/`.
2. Crea `spec.md` y pega la descripción del Issue de GitHub.
3. Pega este prompt:
> "Lee atentamente la especificación del problema e implicaciones técnicas detalladas en `spec/features/[nombre-tarea]/spec.md`. Utiliza Context7 mediante MCP para contrastar los requerimientos con las mejores prácticas de la documentación oficial. Genera el archivo `plan.md` proponiendo la arquitectura de archivos afectados, la lógica de flujo de datos y los riesgos potenciales."
*Detente aquí y revisa el `plan.md` hasta que estés conforme.*

### FASE 3: Desglose de Tareas de Alta Precisión
*Objetivo: Convertir el plan en micro-pasos.*
Pega este prompt:
> "Basado en el `plan.md` que validamos, genera el archivo `tasks.md`. Crea un checklist exhaustivo y estrictamente secuencial de micro-tareas verificables. Cada tarea debe ser lo suficientemente pequeña para no romper el contexto."
*Revisa que las tareas sean atómicas.*

### FASE 4: Implementación Guiada y Atómica
*Objetivo: Ejecutar el desarrollo paso a paso.*
Para CADA tarea en el checklist, inicializa el bucle:
> "Ejecuta estrictamente la Tarea [Número] definida en `spec/features/[nombre-tarea]/tasks.md`. Utiliza el contexto almacenado en la Constitución y las consultas de sintaxis de Context7. Al finalizar la modificación de los archivos, marca la tarea con una [X], describe brevemente qué cambiaste y detén tu ejecución esperando mi feedback."
*No pases a la Tarea [Número+1] sin que yo te haya dado feedback positivo de la Tarea [Número].*

### FASE 5: Verificación, Cierre y Documentación de Sesión
*Objetivo: Documentar el entregable.*
Cuando el checklist esté completo y verificado:
> "La funcionalidad ha sido verificada con éxito. Compila los logs de cambios y genera de forma automática el reporte técnico final en inglés en `docs/changelogs/changelog-[nombre-tarea].md` estructurado como una plantilla de Pull Request de GitHub (Description, Changes, Verification Steps). Limpia los archivos temporales y actualiza el contexto general en `docs/sessions/`."
