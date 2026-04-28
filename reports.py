# reports.py — PETROCI PRO
# Génération de rapports PDF professionnels

import io
from datetime import date

def generer_rapport_pdf(rapport, titre, date_debut,
                         date_fin, nb_jours, kpis=None):
    """Génère un rapport PDF professionnel"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle,
            Paragraph, Spacer, HRFlowable
        )
        from reportlab.lib.styles import (
            getSampleStyleSheet, ParagraphStyle
        )
        from reportlab.lib.units import cm

        buffer = io.BytesIO()
        doc    = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        styles = getSampleStyleSheet()
        elems  = []

        OR  = colors.HexColor("#E07B00")
        BLU = colors.HexColor("#1A1A2E")
        GRY = colors.HexColor("#F4F6F9")
        LGY = colors.HexColor("#DDDDDD")

        # Styles
        s_titre = ParagraphStyle("titre", parent=styles["Title"],
                                  textColor=OR, fontSize=18,
                                  spaceAfter=4)
        s_sous  = ParagraphStyle("sous", parent=styles["Normal"],
                                  textColor=colors.HexColor("#666"),
                                  fontSize=9, spaceAfter=16)
        s_h2    = ParagraphStyle("h2", parent=styles["Heading2"],
                                  textColor=BLU, fontSize=11,
                                  spaceBefore=12, spaceAfter=6)
        s_body  = ParagraphStyle("body", parent=styles["Normal"],
                                  fontSize=9, textColor=BLU)
        s_foot  = ParagraphStyle("foot", parent=styles["Normal"],
                                  fontSize=7, textColor=LGY,
                                  alignment=1)

        # En-tête
        elems.append(Paragraph("PETROCI PRO", s_titre))
        elems.append(Paragraph(
            f"{titre}  |  "
            f"Periode : {date_debut} au {date_fin}  |  "
            f"Genere le : {date.today().strftime('%d/%m/%Y')}",
            s_sous
        ))
        elems.append(HRFlowable(width="100%", thickness=2, color=OR))
        elems.append(Spacer(1, 0.4*cm))

        # KPIs résumé
        if kpis:
            elems.append(Paragraph("Indicateurs Cles", s_h2))
            kpi_data = [
                ["Indicateur", "Valeur", "Unite"],
                ["Production totale",
                 f"{kpis.get('production_totale_bbl',0):,.0f}", "bbl"],
                ["Revenu journalier",
                 f"${kpis.get('revenu_journalier_usd',0):,.0f}", "USD"],
                ["Revenu journalier",
                 f"{kpis.get('revenu_journalier_xof',0)/1e6:.1f}M", "FCFA"],
                ["Puits actifs",
                 str(kpis.get('nb_puits_actifs',0)), "puits"],
                ["Uptime moyen",
                 f"{kpis.get('uptime_moyen',0):.1f}%", ""],
                ["Marge journaliere",
                 f"${kpis.get('marge_usd',0):,.0f}", "USD"],
            ]
            tbl = Table(kpi_data, colWidths=[7*cm, 5*cm, 4*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,0), OR),
                ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
                ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0),(-1,-1), 9),
                ("ALIGN",      (0,0),(-1,-1), "CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),
                 [colors.white, GRY]),
                ("GRID",       (0,0),(-1,-1), 0.4, LGY),
                ("TOPPADDING", (0,0),(-1,-1), 6),
                ("BOTTOMPADDING",(0,0),(-1,-1), 6),
                ("FONTNAME",   (0,1),(0,-1), "Helvetica-Bold"),
            ]))
            elems.append(tbl)
            elems.append(Spacer(1, 0.4*cm))

        # Rapport par champ
        if rapport is not None and not rapport.empty:
            elems.append(Paragraph("Detail par Champ", s_h2))
            headers = [
                "Champ", "Production (bbl)",
                "Water Cut", "Uptime",
                "Revenu USD", "Revenu FCFA"
            ]
            data = [headers]
            for _, row in rapport.iterrows():
                data.append([
                    str(row.get("champ", "")),
                    f"{row.get('Production_Totale',0):,.0f}",
                    f"{row.get('WaterCut_Moyen',0):.1%}",
                    f"{row.get('Uptime_Moyen',0):.1f}%",
                    f"${row.get('Revenu_USD',0):,.0f}",
                    f"{row.get('Revenu_FCFA',0)/1e6:.1f}M",
                ])
            # Total
            data.append([
                "TOTAL",
                f"{rapport['Production_Totale'].sum():,.0f}",
                f"{rapport['WaterCut_Moyen'].mean():.1%}",
                f"{rapport['Uptime_Moyen'].mean():.1f}%",
                f"${rapport['Revenu_USD'].sum():,.0f}",
                f"{rapport['Revenu_FCFA'].sum()/1e6:.1f}M",
            ])
            col_w = [3*cm, 3.5*cm, 2.5*cm, 2*cm, 3*cm, 2.5*cm]
            tbl2  = Table(data, colWidths=col_w)
            tbl2.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0), BLU),
                ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
                ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,-1), 8),
                ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-2),
                 [colors.white, GRY]),
                ("BACKGROUND",    (0,-1),(-1,-1),
                 colors.HexColor("#FFF0DC")),
                ("FONTNAME",      (0,-1),(-1,-1), "Helvetica-Bold"),
                ("GRID",          (0,0),(-1,-1), 0.4, LGY),
                ("TOPPADDING",    (0,0),(-1,-1), 5),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ]))
            elems.append(tbl2)

        # Pied de page
        elems.append(Spacer(1, 1*cm))
        elems.append(HRFlowable(width="100%", thickness=0.5, color=LGY))
        elems.append(Spacer(1, 0.2*cm))
        elems.append(Paragraph(
            "Document confidentiel — PETROCI PRO — "
            "Systeme de Gestion de Production — "
            "Cote d'Ivoire",
            s_foot
        ))

        doc.build(elems)
        buffer.seek(0)
        return buffer.read()

    except ImportError:
        return None
    except Exception:
        return None
