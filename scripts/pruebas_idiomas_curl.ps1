# Pruebas de idiomas desde terminal (ejecutar con el backend corriendo: python main.py)
# Uso: .\scripts\pruebas_idiomas_curl.ps1
# La cookie de idioma es: vino_pro_lang (no pref_idioma)

$Base = "http://127.0.0.1:8001"
$ErrorActionPreference = "Continue"

Write-Host "=== Prueba 1: GET / sin cookie (debe incluir HTML del modal) ===" -ForegroundColor Cyan
$r1 = Invoke-WebRequest -Uri "$Base/" -UseBasicParsing -SessionVariable s
if ($r1.Content -match "modal-bienvenida-idioma") { Write-Host "OK - Modal de bienvenida presente en el HTML." -ForegroundColor Green }
else { Write-Host "FALLO - No se encontro modal-bienvenida-idioma en la respuesta." -ForegroundColor Red }
if ($r1.Content -match "set-lang\?lang=es" -and $r1.Content -match "set-lang\?lang=ar") { Write-Host "OK - Enlaces de idiomas (es, ar) presentes." -ForegroundColor Green }
else { Write-Host "Revisar: enlaces set-lang en el modal." -ForegroundColor Yellow }

Write-Host "`n=== Prueba 2: set-lang para cada idioma (302 + cookie vino_pro_lang) ===" -ForegroundColor Cyan
$langs = @("es","en","pt","fr","de","it","ar","ru","tr","zh","ja","ko")
foreach ($lang in $langs) {
  try {
    $r = Invoke-WebRequest -Uri "$Base/set-lang?lang=$lang" -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
  } catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 302) {
      $cookie = $_.Exception.Response.Headers["Set-Cookie"]
      if ($cookie -match "vino_pro_lang=$lang") { Write-Host "  $lang : OK (302 + cookie)" -ForegroundColor Green }
      else { Write-Host "  $lang : 302 pero cookie no coincide: $cookie" -ForegroundColor Yellow }
    } else { Write-Host "  $lang : No 302" -ForegroundColor Red }
  }
}

Write-Host "`n=== Prueba 3: Pagina principal CON cookie vino_pro_lang=ar (texto en arabe) ===" -ForegroundColor Cyan
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$cookie = New-Object System.Net.Cookie("vino_pro_lang", "ar", "/", "127.0.0.1")
$session.Cookies.Add($Base, $cookie)
$r3 = Invoke-WebRequest -Uri "$Base/" -UseBasicParsing -WebSession $session
if ($r3.Content -match "الرئيسية") { Write-Host "OK - Texto en arabe (الرئيسية) encontrado." -ForegroundColor Green }
else { Write-Host "Revisar: respuesta con cookie ar deberia contener arabe." -ForegroundColor Yellow }

Write-Host "`n=== Prueba 4: Muestra de texto traducido por idioma (nav.inicio) ===" -ForegroundColor Cyan
$esperado = @{
  es = "Inicio";     en = "Home";    pt = "Início";   fr = "Accueil";  de = "Startseite"; it = "Home"
  ar = "الرئيسية";   ru = "Главная"; tr = "Ana Sayfa"; zh = "首页";    ja = "ホーム";    ko = "홈"
}
foreach ($lang in $langs) {
  $s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
  $c = New-Object System.Net.Cookie("vino_pro_lang", $lang, "/", "127.0.0.1")
  $s.Cookies.Add($Base, $c)
  try {
    $resp = Invoke-WebRequest -Uri "$Base/" -UseBasicParsing -WebSession $s
    $txt = $esperado[$lang]
    if ($txt -and $resp.Content -match [regex]::Escape($txt)) { Write-Host "  $lang : OK ($txt)" -ForegroundColor Green }
    else { Write-Host "  $lang : No se encontro '$txt' en respuesta" -ForegroundColor Yellow }
  } catch { Write-Host "  $lang : Error $($_.Exception.Message)" -ForegroundColor Red }
}

Write-Host "`n=== Fin de pruebas ===" -ForegroundColor Cyan
Write-Host "Nota: La cookie de idioma es vino_pro_lang (no pref_idioma)." -ForegroundColor Gray
