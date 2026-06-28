#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_lavoro — strato dati condiviso (nessuna GUI)
Riusato da app desktop, generatore web/PWA e app mobile Kivy.
Dipendenze: requests, beautifulsoup4
"""
import re
import json
import datetime as dt
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

def gnews(query):
    return ("https://news.google.com/rss/search?q=" + quote_plus(query) + "&hl=it&gl=IT&ceid=IT:it")

SOURCES = [
    {"id": "inps-circolari", "ente": "INPS", "code": "INPS", "categoria": "Circolari",
     "tipo": "rss", "url": "https://www.inps.it/it/it.rss.circolari.xml", "color": "#0a7d4d"},
    {"id": "inps-messaggi", "ente": "INPS", "code": "INPS", "categoria": "Messaggi",
     "tipo": "rss", "url": "https://www.inps.it/it/it.rss.messaggi.xml", "color": "#0a7d4d"}
]

def ripulisci(testo, max_len=200):
    if not testo:
        return ""
    testo = re.sub(r'\s+', ' ', testo).strip()
    if len(testo) > max_len:
        testo = testo[:max_len-3] + "..."
    return testo

def fetch_rss(src):
    items = []
    try:
        r = requests.get(src["url"], timeout=15)
        root = ET.fromstring(r.content)
        for channel in root.findall('channel'):
            for item in channel.findall('item'):
                title = item.find('title')
                link = item.find('link')
                pubDate = item.find('pubDate')
                
                t_str = title.text if title is not None else ""
                l_str = link.text if link is not None else ""
                
                dt_obj = None
                if pubDate is not None and pubDate.text:
                    try:
                        dt_obj = parsedate_to_datetime(pubDate.text)
                    except Exception:
                        pass
                
                items.append(crea_item(src, t_str, l_str, dt_obj, ""))
    except Exception as e:
        print(f"Errore RSS {src['id']}: {e}")
    return items

def crea_item(src, titolo, url, data, summary):
    titolo = ripulisci(titolo, 220) or "(senza titolo)"
    return {
        "uid": url or titolo,
        "ente": src["ente"], "code": src["code"], "categoria": src["categoria"],
        "color": src["color"], "titolo": titolo, "url": url or "",
        "data_label": data.strftime("%d/%m/%Y") if data else "—",
        "data_sort": data.strftime("%Y%m%d") if data else "00000000",
        "summary": summary or "",
    }

def raccogli(giorni=None):
    tutti = []
    soglia = dt.datetime.now() - dt.timedelta(days=giorni) if giorni else None
    for src in SOURCES:
        try:
            items = fetch_rss(src)
            if soglia:
                items = [it for it in items if it["data_sort"] == "00000000"
                         or dt.datetime.strptime(it["data_sort"], "%Y%m%d") >= soglia]
            tutti.extend(items)
        except Exception:
            pass
    return tutti
