"""Mattoni grafici nello stile video della testata (vedi il documento di stile).

Tutte le funzioni restituiscono immagini RGBA 1080x1920 da sovrapporre al video:
le parti trasparenti lasciano vedere il video sotto.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
TOP = 1300                      # le schede coprono 0..TOP: i sottotitoli del video restano visibili sotto
BLU = (0, 135, 240)             # #0087F0, accento dei video
GRIGIO = (150, 150, 150)
CAP_Y = 1414                    # centro della riga dei sottotitoli
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "font")


def font(peso="bold", size=64):
    nome = {"bold": "Poppins-Bold.ttf", "extrabold": "Poppins-ExtraBold.ttf"}[peso]
    return ImageFont.truetype(os.path.join(FONT_DIR, nome), size)


def tela():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def testo_ombra(img, xy, txt, f, fill=(255, 255, 255), anchor="mm", ombra=6):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 3, xy[1] + 4), txt, font=f, fill=(0, 0, 0, 200), anchor=anchor)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(ombra)))
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=fill, anchor=anchor)


def riga_evidenziata(img, cy, parole, evidenziate, f, pad=(14, 8), spazio=None):
    """Riga centrata; le parole agli indici 'evidenziate' stanno su un riquadro blu."""
    d = ImageDraw.Draw(img)
    ev = evidenziate if isinstance(evidenziate, (list, tuple)) else [evidenziate]
    sp = spazio if spazio is not None else int(f.size * 0.28)
    larg = [d.textlength(p, font=f) for p in parole]
    x0 = (W - (sum(larg) + sp * (len(parole) - 1))) / 2
    x = x0
    for i, (p, l) in enumerate(zip(parole, larg)):
        if i in ev:
            bb = d.textbbox((x, cy), p, font=f, anchor="lm")
            d.rounded_rectangle((bb[0] - pad[0], bb[1] - pad[1], bb[2] + pad[0], bb[3] + pad[1]),
                                radius=int(f.size * 0.18), fill=BLU + (255,))
        x += l + sp
    x = x0
    for p, l in zip(parole, larg):
        testo_ombra(img, (x, cy), p, f, anchor="lm", ombra=4)
        x += l + sp


def sottotitolo(parole, evidenziata, cy=CAP_Y, size=64):
    """Sottotitolo come quelli dei talking head: maiuscolo bianco, parola pronunciata su blu."""
    img = tela()
    riga_evidenziata(img, cy, [p.upper() for p in parole], evidenziata, font("bold", size))
    return img


def sottotitoli_da_parole(parole_json, gruppi):
    """gruppi: liste di parole del copione come appaiono a schermo, es. [["HA", "GUADAGNATO"], ["PAZZESCA"]].
    Usa i tempi di parole.json (stesso ordine) per creare un'immagine per ogni parola pronunciata.
    Restituisce [(inizio, fine, immagine)]."""
    out, k = [], 0
    for g in gruppi:
        for i in range(len(g)):
            a, b = parole_json[k][0], parole_json[k][1]
            out.append((a, b, sottotitolo(g, i)))
            k += 1
    # ogni sottotitolo resta fino all'inizio del successivo
    return [(a, out[n + 1][0] if n + 1 < len(out) else b, im) for n, (a, b, im) in enumerate(out)]


def scheda_vuota():
    img = tela()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, TOP), fill=(0, 0, 0, 255))
    for i in range(70):  # bordo sfumato verso il video
        d.line((0, TOP + i, W, TOP + i), fill=(0, 0, 0, int(255 * (1 - i / 70))))
    return img


def fonte(img, txt):
    ImageDraw.Draw(img).text((W / 2, TOP - 70), txt, font=font("bold", 30), fill=GRIGIO + (255,), anchor="mm")


def scheda_numero(numero, righe, testo_fonte, size_numero=250):
    """righe: [(["PAROLE", "SBAGLIATE"], [1]), (["COMPRATE SU GOOGLE"], [])]  (indici evidenziati in blu)."""
    img = scheda_vuota()
    testo_ombra(img, (W / 2, 520), numero, font("extrabold", size_numero))
    y = 790
    for parole, ev in righe:
        if ev:
            riga_evidenziata(img, y, parole, ev, font("extrabold", 78), spazio=24)
        else:
            testo_ombra(img, (W / 2, y), " ".join(parole), font("extrabold", 66))
        y += 110
    fonte(img, testo_fonte)
    return img


def cartello_finale(riga1, riga2, evidenziate2, sotto="Diccelo nei commenti", logo_brand=None):
    img = scheda_vuota()
    if logo_brand:
        lg = Image.open(logo_brand).convert("RGBA")
        lg = lg.resize((520, int(lg.height * 520 / lg.width)), Image.LANCZOS)
        img.alpha_composite(lg, (int((W - 520) / 2), 330))
    testo_ombra(img, (W / 2, 690), riga1, font("extrabold", 86))
    riga_evidenziata(img, 810, riga2, evidenziate2, font("extrabold", 78), spazio=22)
    testo_ombra(img, (W / 2, 960), sotto, font("bold", 48))
    return img


def logo_testata(logo_png, larghezza=294, y=80):
    """Logo della testata in alto al centro, con ombra leggera."""
    mi = Image.open(logo_png).convert("RGBA")
    mi = mi.resize((larghezza, int(mi.height * larghezza / mi.width)), Image.LANCZOS)
    img = tela()
    sh = tela()
    sh.paste(Image.new("RGBA", mi.size, (0, 0, 0, 150)), (int((W - mi.width) / 2) + 2, y + 4), mi)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    img.alpha_composite(mi, (int((W - mi.width) / 2), y))
    return img
