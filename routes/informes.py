"""
Exportar informes en PDF: informe de cata profesional e informe de bodega personal.
"""
import io
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Informes"])


class InformeCataBody(BaseModel):
    vino: dict = {}
    notas_adicionales: str = ""

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def _session_id(x_session_id: str | None = Header(None, alias="X-Session-ID")) -> str:
    if not x_session_id or not x_session_id.strip():
        raise HTTPException(status_code=400, detail="X-Session-ID requerido para informe de bodega.")
    return x_session_id.strip()


def _pdf_cata(vino: dict, notas_adicionales: str = "") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="CustomTitle", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#6b2d3c"))
    flow = [
        Paragraph("Informe de cata profesional", title_style),
        Spacer(1, 0.5*cm),
        Paragraph(f"<b>Vino:</b> {vino.get('nombre', 'N/A')}", styles["Normal"]),
        Paragraph(f"<b>Bodega:</b> {vino.get('bodega', 'N/A')}", styles["Normal"]),
        Paragraph(f"<b>Región / País:</b> {vino.get('region', '')} ({vino.get('pais', 'N/A')})", styles["Normal"]),
        Paragraph(f"<b>Tipo:</b> {vino.get('tipo', 'N/A')}", styles["Normal"]),
        Paragraph(f"<b>Puntuación:</b> {vino.get('puntuacion', 'N/A')}", styles["Normal"]),
        Paragraph(f"<b>Precio estimado:</b> {vino.get('precio_estimado', 'N/A')}", styles["Normal"]),
        Spacer(1, 0.5*cm),
        Paragraph("<b>Descripción</b>", styles["Heading2"]),
        Paragraph(vino.get("descripcion", ""), styles["Normal"]),
        Spacer(1, 0.3*cm),
        Paragraph("<b>Notas de cata</b>", styles["Heading2"]),
        Paragraph(vino.get("notas_cata", ""), styles["Normal"]),
        Spacer(1, 0.3*cm),
        Paragraph("<b>Maridaje</b>", styles["Heading2"]),
        Paragraph(vino.get("maridaje", ""), styles["Normal"]),
    ]
    if notas_adicionales:
        flow.append(Spacer(1, 0.3*cm))
        flow.append(Paragraph("<b>Notas adicionales</b>", styles["Heading2"]))
        flow.append(Paragraph(notas_adicionales, styles["Normal"]))
    flow.append(Spacer(1, 1*cm))
    flow.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} — VINO PRO IA", styles["Normal"]))
    doc.build(flow)
    return buffer.getvalue()


def _pdf_bodega(botellas: list, valoracion: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="CustomTitle", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#6b2d3c"))
    flow = [
        Paragraph("Informe de Mi Bodega Virtual", title_style),
        Spacer(1, 0.3*cm),
        Paragraph(f"Total botellas: {valoracion.get('total_botellas', 0)} | Valoración estimada: {valoracion.get('valoracion_estimada', 0):.2f} €", styles["Normal"]),
        Spacer(1, 0.5*cm),
    ]
    if botellas:
        data = [["Vino", "Cant.", "Añada", "Ubicación", "Valor unit."]]
        for b in botellas:
            data.append([
                (b.get("vino_nombre") or "")[:30],
                str(b.get("cantidad", 1)),
                str(b.get("anada") or "-"),
                (b.get("ubicacion") or "-")[:15],
                str(b.get("valor_unitario_estimado") or "-"),
            ])
        t = Table(data, colWidths=[5*cm, 1.2*cm, 1.5*cm, 3*cm, 2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6b2d3c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
        ]))
        flow.append(t)
    flow.append(Spacer(1, 0.5*cm))
    flow.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} — VINO PRO IA", styles["Normal"]))
    doc.build(flow)
    return buffer.getvalue()


@router.get("/informes/bodega")
def informe_bodega_pdf(session_id: str = Depends(_session_id)):
    """Genera PDF con el inventario de Mi Bodega Virtual."""
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Generación de PDF no disponible (instalar reportlab).")
    from services import bodega_service
    botellas = bodega_service.get_bodega(session_id)
    valoracion = bodega_service.get_valoracion(session_id)
    pdf_bytes = _pdf_bodega(botellas, valoracion)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=informe_bodega.pdf"})


@router.post("/informes/cata")
def informe_cata_pdf(body: InformeCataBody):
    """Genera PDF de informe de cata profesional. Body: JSON con vino (nombre, bodega, etc.) y opcional notas_adicionales."""
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Generación de PDF no disponible (instalar reportlab).")
    pdf_bytes = _pdf_cata(body.vino, body.notas_adicionales)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=informe_cata.pdf"})
