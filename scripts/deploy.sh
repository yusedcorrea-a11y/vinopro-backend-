#!/bin/bash
# deploy.sh - Despliegue de Vino Pro IA (Linux / VPS)
# Uso: ./deploy.sh [ruta_destino]   o   DEPLOY_TARGET=/var/www/vino-pro ./deploy.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TARGET="${1:-$DEPLOY_TARGET}"

if [ -z "$TARGET" ]; then
  echo "Uso: ./deploy.sh /var/www/vino-pro"
  echo "  o: DEPLOY_TARGET=/var/www/vino-pro ./deploy.sh"
  exit 1
fi

echo "Proyecto: $PROJECT_ROOT -> Destino: $TARGET"

# Crear destino si no existe
mkdir -p "$TARGET"

# Copiar archivos (excluir venv, __pycache__, .git)
rsync -av --delete \
  --exclude 'venv' \
  --exclude 'venv_*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'pytest.ini' \
  --exclude 'tests' \
  "$PROJECT_ROOT/" "$TARGET/" \
  || {
    # Si no hay rsync, copiar manualmente
    cp -r "$PROJECT_ROOT/app.py" "$PROJECT_ROOT/templates" "$PROJECT_ROOT/static" \
          "$PROJECT_ROOT/data" "$PROJECT_ROOT/services" "$PROJECT_ROOT/routes" \
          "$PROJECT_ROOT/requirements_produccion.txt" "$PROJECT_ROOT/.env.example" "$TARGET/" 2>/dev/null || true
    [ -f "$PROJECT_ROOT/.env" ] && cp "$PROJECT_ROOT/.env" "$TARGET/.env"
  }

# Instalar dependencias
echo "Instalando dependencias..."
cd "$TARGET"
if command -v pip3 &>/dev/null; then
  pip3 install -r requirements_produccion.txt
elif command -v pip &>/dev/null; then
  pip install -r requirements_produccion.txt
else
  echo "Aviso: pip no encontrado. Instala dependencias manualmente."
fi

echo ""
echo "Variables de entorno: crear/editar .env en $TARGET con:"
echo "  HOST=0.0.0.0"
echo "  PORT=8000"
echo "  CORS_ORIGINS=https://tudominio.com"
echo "  STRIPE_SECRET_KEY=sk_live_xxx"
echo "  STRIPE_PUBLISHABLE_KEY=pk_live_xxx"
echo "  STRIPE_WEBHOOK_SECRET=whsec_xxx"
echo ""
echo "Iniciar servicio (ejemplo con systemd):"
echo "  sudo systemctl start vino-pro   # si tienes unidad configurada"
echo "  o: cd $TARGET && HOST=0.0.0.0 PORT=8000 nohup python3 app.py &"
echo "OK."
