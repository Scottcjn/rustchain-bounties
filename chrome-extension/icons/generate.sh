#!/bin/bash
# Generate placeholder icons
convert -size 16x16 xc:#3498db icons/icon16.png
convert -size 48x48 xc:#3498db icons/icon48.png
convert -size 128x128 xc:#3498db icons/icon128.png
echo "Icons generated!"
