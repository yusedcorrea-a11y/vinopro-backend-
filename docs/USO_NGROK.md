# Uso de ngrok para compartir Vino Pro IA

Con ngrok puedes dar acceso a tu app (por ejemplo a tu familia en Medellín) sin dominio ni hosting. Ellos abren un enlace en el navegador y usan Vino Pro IA como si estuviera en internet.

---

## Requisitos

1. **Backend en marcha**  
   El backend debe estar corriendo en `http://127.0.0.1:8001` **antes** de ejecutar ngrok.  
   En una terminal: `python main.py`

2. **ngrok instalado y configurado**  
   - Si no lo tienes: ejecuta `.\scripts\instalar_ngrok.ps1` (una sola vez).  
   - Cuenta gratuita y authtoken en [ngrok.com/signup](https://ngrok.com/signup).  
   - Luego: `ngrok config add-authtoken TU_TOKEN` (desde la carpeta donde está `ngrok.exe` o con ngrok en el PATH).

---

## Cómo iniciar ngrok cada vez que quieras compartir

1. Asegúrate de que el backend está corriendo: `python main.py`.
2. En **otra** ventana de PowerShell, desde la carpeta `backend_optimized`:
   ```powershell
   .\scripts\iniciar_ngrok.ps1
   ```
3. El script:
   - Comprueba que el backend responde en el puerto 8001.
   - Inicia ngrok y obtiene la URL pública (ej: `https://abc123.ngrok-free.app`).
   - Guarda la URL en `URL_ACCESO.txt`.
   - Actualiza `ENLACE_PARA_MEDELLIN.txt` con la URL e instrucciones.
   - **Copia la URL al portapapeles**.
4. Envía por WhatsApp (o como quieras) el enlace. La otra persona solo tiene que abrirlo en el navegador (móvil o PC).

---

## Importante

- **La URL cambia cada vez** que inicias ngrok (en la cuenta gratuita). Cada vez que ejecutes `iniciar_ngrok.ps1` tendrás una URL nueva; vuelve a compartirla.
- **Mientras ngrok esté abierto**, tu familia puede usar la app. Si cierras la ventana donde se ejecutó el script o matas el proceso `ngrok`, el enlace dejará de funcionar.
- **El backend debe seguir corriendo** en tu PC. ngrok solo hace de “túnel” hacia tu máquina.

---

## Dónde se guarda todo

| Archivo | Contenido |
|--------|-----------|
| `URL_ACCESO.txt` | Solo la URL pública (se actualiza al ejecutar `iniciar_ngrok.ps1`). |
| `ENLACE_PARA_MEDELLIN.txt` | URL + instrucciones para quien recibe el enlace. |

---

## Resumen rápido

```
1. python main.py                    # Terminal 1: backend
2. .\scripts\iniciar_ngrok.ps1       # Terminal 2: túnel
3. Copiar enlace (ya está en el portapapeles) y enviar por WhatsApp
4. ¡Tu familia en Medellín ya puede usar Vino Pro IA!
```

Para detener ngrok cuando ya no quieras compartir:

```powershell
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process
```
