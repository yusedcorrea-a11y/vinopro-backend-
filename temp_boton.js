// --- BOTÓN 404 REGISTRAR VINO ---
function mostrarBotonRegistrar() {
  const btn = document.createElement('button');
  btn.id = 'btnRegistrar404';
  btn.innerText = '¿No es tu vino? Regístralo';
  btn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;padding:12px 18px;background:#c0392b;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:bold;';
  btn.onclick = abrirFormularioRegistro;
  document.body.appendChild(btn);
}

function abrirFormularioRegistro() {
  const html = `
    <div id="modalRegistro" style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:10000;">
      <div style="background:#fff;padding:25px;border-radius:12px;width:90%;max-width:400px;">
        <h3>Registrar vino desconocido</h3>
        <input id="regNombre" placeholder="Nombre del vino" style="width:100%;padding:8px;margin:6px 0;">
        <input id="regBodega" placeholder="Bodega / Marca" style="width:100%;padding:8px;margin:6px 0;">
        <input id="regAnada" type="number" placeholder="Añada (ej. 2020)" style="width:100%;padding:8px;margin:6px 0;">
        <input id="regPrecio" type="number" placeholder="Precio € (opcional)" style="width:100%;padding:8px;margin:6px 0;">
        <label><input id="regVenta" type="checkbox"> ¿Poner en venta?</label>
        <div style="margin-top:12px;text-align:right;">
          <button onclick="cerrarFormularioRegistro()" style="margin-right:8px;padding:8px 14px;border:none;border-radius:6px;background:#ccc;">Cancelar</button>
          <button onclick="enviarRegistro()" style="padding:8px 14px;border:none;border-radius:6px;background:#27ae60;color:#fff;">Guardar</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', html);
}

function cerrarFormularioRegistro() {
  document.getElementById('modalRegistro').remove();
}

async function enviarRegistro() {
  const body = {
    name: document.getElementById('regNombre').value,
    producer: document.getElementById('regBodega').value,
    vintage: parseInt(document.getElementById('regAnada').value) || null,
    price: parseFloat(document.getElementById('regPrecio').value) || null,
    for_sale: document.getElementById('regVenta').checked
  };
  if (!body.name || !body.producer) { alert('Nombre y bodega obligatorios'); return; }
  const res = await fetch('/wines', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if (res.ok) {
    alert('Vino registrado con éxito');
    cerrarFormularioRegistro();
    location.reload();
  } else {
    alert('Error al registrar');
  }
}
