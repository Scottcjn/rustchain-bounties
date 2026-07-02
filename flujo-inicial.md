# Flujo Inicial: Nuestra Brújula de Git y Estructura de Proyectos

Este protocolo es de obligatorio cumplimiento antes de escribir cualquier línea de código o activar agentes de IA. Su objetivo es blindar el entorno local, asegurar el historial de Git y prevenir la pérdida de archivos o bloqueos en los Pull Requests. *(Nota de aprendizaje: Evitar a toda costa los errores de historias desconectadas sufridos en Stellar Creator y Engram).*

---

## Fase Previa: Almacenamiento Seguro
Antes de tocar la terminal, ve al repositorio original del proyecto en la web y descarga el código en un archivo **ZIP**. Guárdalo en tu disco local como un respaldo estático e histórico del estado inicial del proyecto. Esto es puramente para tu almacenamiento personal; **nunca** trabajes ni compiles sobre esta carpeta descomprimida.

---

## Paso 1: El Fork (Primero en la Web)
Antes de interactuar con la consola, ve al GitHub del proyecto original (`Autor/Proyecto`) y haz clic en el botón **`Fork`** (arriba a la derecha). Esto genera una copia idéntica y legítima del repositorio bajo tu propio usuario de GitHub (`gramseostudio-dev/Proyecto`).

---

## Paso 2: Auditoría y Seteo de Estructura de Carpetas (Local)
Una vez que el proyecto está creado en tu entorno local (tras el clonado del Paso 3), se debe realizar una revisión manual y rigurosa de la arquitectura del proyecto, archivo por archivo y carpeta por carpeta, para delimitar el alcance del trabajo:

1. **Revisión de Contenido Existente:** Abrir el proyecto en el editor y mapear qué archivos base tienen código funcional que debe dejarse quieto para no alterar la lógica central del repositorio original.
2. **Definición de Archivos Vacíos:** Identificar y crear los archivos o specs que se inicializarán en blanco (por ejemplo, `docs/openapi.yaml` o carpetas de configuración locales) listos para que el desarrollador o el agente los rellene.
3. **Fijación de Archivos Protegidos:** Marcar claramente los archivos sensibles del sistema (como configuraciones de CI/CD, dependencias globales o llaves de entorno) que **no se deben tocar** bajo ninguna circunstancia para evitar scope creep o fallas de compilación en el servidor de destino.

---

## Paso 3: Clonar TU Fork en la Terminal
Abre tu **Git Bash** en tu ruta de desarrollo local *(alejada de carpetas con sincronización activa de OneDrive para evitar bloqueos de permisos o desaparición de archivos en segundo plano)* y ejecuta el clonado de tu copia modificable:

```bash
# Clonar tu repositorio fork
git clone [https://github.com/gramseostudio-dev/Proyecto.git](https://github.com/gramseostudio-dev/Proyecto.git)

# Entrar a la carpeta del proyecto
cd Proyecto


Paso 4: Vincular el Repositorio Original (upstream)
Establece de inmediato el puente con el repositorio del dueño original para mantener tu código actualizado y evitar que los historiales se desalineen en el futuro:

# Vincular el repositorio del dueño original
git remote add upstream [https://github.com/Autor/Proyecto.git](https://github.com/Autor/Proyecto.git)

# Verificar que tengas 'origin' (tu repo) y 'upstream' (el de ellos)
git remote -v


Paso 5: Crear una Rama de Trabajo (Feature Branch)
El trabajo nunca se realiza de manera directa sobre la rama main. Aísla tus cambios creando una rama específica para la tarea o el bounty correspondiente:

# Crear y cambiarte a la nueva rama
git checkout -b feature/nombre-de-la-tarea



Paso 6: Guardar los Cambios Localmente (Commit)
Cuando la estructura definida en el Paso 2 haya sido completada, auditada y los archivos cuenten con el código correcto, prepara tu paquete de entrega en la consola:

# Ver qué archivos cambiaste o agregaste
git status

# Agregar todos los cambios al escenario
git add .

# Confirmar los cambios con un mensaje bajo el estándar convencional
git commit -m "docs: add complete OpenAPI 3.0 spec for miner HTTP endpoints (closes #23)"


Paso 7: Subir la Rama a TU GitHub
Empuja la rama de trabajo que creaste localmente directo hacia tu repositorio remoto controlado:

git push origin feature/nombre-de-la-tarea


Paso 8: Iniciar el Pull Request desde la Terminal
Para evitar interfaces web congeladas, botones bloqueados o problemas de renderizado en el navegador, ejecuta la apertura del Pull Request directamente utilizando la herramienta oficial de GitHub para consolas:

# Crear el PR directo apuntando al repositorio original de forma automática
gh pr create --title "docs: add complete OpenAPI 3.0 spec for miner HTTP endpoints (closes #23)" --body-file docs/changelogs/changelog-engram-openapi.md

(Si no utilizas gh, el comando git push del Paso 7 te entregará un enlace azul automático en la consola. Al presionar Ctrl + Clic sobre él, te llevará a la web con el formulario limpio, el botón verde desbloqueado y libre de conflictos de historial).


---

Con este documento guardado en tu espacio de trabajo, garantizamos que cada nuevo proyecto comience con las carpetas protegidas y la terminal perfectamente alineada. ¿Guardamos el archivo y lo dejas listo junto a la guía maestra?











