#!/usr/bin/env python3
"""
EVENTOON — Script di aggiornamento automatico eventi
=====================================================
Questo script:
1. Visita i siti dei giornali locali dell'Emilia-Romagna
2. Estrae il contenuto delle pagine eventi
3. Usa Claude API per analizzare il testo e estrarre eventi strutturati
4. Salva tutto in un file events.json che l'app legge

Può girare:
- Manualmente: python scraper.py
- Automaticamente: via GitHub Actions (ogni giorno alle 7:00)

Costo stimato: ~$0.15-0.30 al giorno con Claude Sonnet
"""

import json
import os
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

# ═══════════════════════════════════════════════
# CONFIGURAZIONE
# ═══════════════════════════════════════════════

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Fonti da scrapare per ogni città
# Ogni fonte ha un URL della pagina eventi e il nome della testata
FONTI = {
    "reggio-emilia": [
        {
            "nome": "Turismo Reggiano",
            "url": "https://www.reggioemiliawelcome.it/it/eventi/manifestazioni-e-iniziative/eventi-multipli/marzo-2026-calendario-eventi-reggio-emilia-e-provincia",
            "tipo": "istituzionale"
        },
        {
            "nome": "Comune di RE",
            "url": "https://www.comune.reggioemilia.it/vivere-reggio-emilia/eventi",
            "tipo": "istituzionale"
        },
        {
            "nome": "I Teatri RE",
            "url": "https://www.iteatri.re.it/",
            "tipo": "istituzionale"
        },
        {
            "nome": "Musei Civici RE",
            "url": "https://www.musei.re.it/appuntamenti/",
            "tipo": "istituzionale"
        },
        {
            "nome": "Musei Civici RE - Mostre",
            "url": "https://www.musei.re.it/mostre/",
            "tipo": "istituzionale"
        },
        {
            "nome": "Mostre provincia RE",
            "url": "https://www.reggioemiliawelcome.it/it/reggio-emilia/eventi/manifestazioni-e-iniziative/Eventi-culturali/mostre-darte-in-provincia-di-reggio-emilia",
            "tipo": "istituzionale"
        },
    ],
    "bologna": [
        {
            "nome": "BolognaToday Eventi",
            "url": "https://www.bolognatoday.it/eventi/",
            "tipo": "media"
        },
        {
            "nome": "Bologna Welcome",
            "url": "https://www.bolognawelcome.com/it/eventi/homepage",
            "tipo": "istituzionale"
        },
        {
            "nome": "Cultura Bologna",
            "url": "https://www.culturabologna.it/objects/calendario-bologna-cultura",
            "tipo": "istituzionale"
        },
    ],
    "parma": [
        {
            "nome": "ParmaToday Eventi",
            "url": "https://www.parmatoday.it/eventi/",
            "tipo": "media"
        },
        {
            "nome": "Parma Welcome",
            "url": "https://parmawelcome.it/evento/",
            "tipo": "istituzionale"
        },
    ],
    "modena": [
        {
            "nome": "ModenaToday Eventi",
            "url": "https://www.modenatoday.it/eventi/",
            "tipo": "media"
        },
    ],
}

# ═══════════════════════════════════════════════
# FUNZIONI
# ═══════════════════════════════════════════════

def fetch_page(url):
    """Scarica il contenuto di una pagina web"""
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) EventoonBot/1.0"
        })
        with urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")
            # Rimuovi tag HTML per ottenere solo il testo
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            # Limita a ~4000 caratteri per non superare i limiti del contesto
            return text[:6000]
    except Exception as e:
        print(f"  ⚠️  Errore scaricando {url}: {e}")
        return None


def ask_claude(prompt, system=""):
    """Chiama l'API di Claude per analizzare il testo"""
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY non configurata!")
        sys.exit(1)
    
    import json
    from urllib.request import Request, urlopen
    
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    
    req = Request("https://api.anthropic.com/v1/messages", data=data, headers={
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    })
    
    try:
        with urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["content"][0]["text"]
    except Exception as e:
        print(f"  ⚠️  Errore Claude API: {e}")
        return None


def extract_events(text, fonte_nome, fonte_tipo, city):
    """Usa Claude per estrarre eventi strutturati dal testo di una pagina"""
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system = """Sei un assistente che estrae eventi e mostre da testi di siti web italiani.
Restituisci SOLO un array JSON valido, senza markdown, senza spiegazioni.
Ogni elemento deve avere esattamente questi campi:
- title: titolo dell'evento (stringa)
- type: "evento" per eventi puntuali, "mostra" per esposizioni in corso
- category: una tra "sport", "musica", "mercati", "arte", "food", "famiglia"
- date: per eventi puntuali, formato YYYY-MM-DD
- dateFrom: per mostre, data inizio YYYY-MM-DD
- dateTo: per mostre, data fine YYYY-MM-DD  
- time: orario (es. "21:00" o "10:00-18:00" o "tutto il giorno")
- orari: per mostre, gli orari di apertura settimanali
- location: luogo specifico (nome venue + indirizzo se disponibile)
- city: nome della città
- description: descrizione breve (max 150 caratteri)
- age: "tutti", "16+", "18+", o fascia specifica come "5-10"
- free: true se gratuito, false se a pagamento
- subcat: per mostre, sottocategoria (fotografia, pittura, contemporanea, etc.)

Estrai SOLO eventi futuri (da oggi in poi) o mostre attualmente in corso.
Ignora eventi passati. Oggi è """ + today

    prompt = f"""Analizza questo testo dalla fonte "{fonte_nome}" ({fonte_tipo}) per la città di {city}.
Estrai tutti gli eventi e le mostre che trovi. Restituisci SOLO l'array JSON.

TESTO:
{text}"""

    response = ask_claude(prompt, system)
    
    if not response:
        return []
    
    try:
        # Prova a parsare il JSON
        # Rimuovi eventuale markdown
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
            clean = clean.rsplit("```", 1)[0]
        
        events = json.loads(clean)
        
        # Aggiungi metadati della fonte
        for e in events:
            e["source"] = fonte_nome
            e["sourceType"] = fonte_tipo
            e["cityKey"] = city
            e["lastUpdated"] = today
        
        return events
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON non valido da Claude: {e}")
        return []


def assign_visual_properties(events):
    """Assegna colori, emoji e distanze agli eventi"""
    
    CATEGORY_COLORS = {
        "sport": "#2D6A4F",
        "musica": "#7B2D8E",
        "mercati": "#C77B30",
        "arte": "#264653",
        "food": "#E63946",
        "famiglia": "#00B4D8",
    }
    
    CATEGORY_EMOJI = {
        "sport": "🏃",
        "musica": "🎵",
        "mercati": "🏺",
        "arte": "🖼️",
        "food": "🍕",
        "famiglia": "👶",
    }
    
    for e in events:
        cat = e.get("category", "arte")
        e["color"] = CATEGORY_COLORS.get(cat, "#264653")
        e["image"] = CATEGORY_EMOJI.get(cat, "📌")
        # La distanza verrà calcolata lato client con la posizione dell'utente
        e["distance"] = 0
        # Genera un ID unico
        e["id"] = f"{e.get('cityKey','x')}-{hash(e.get('title',''))}"
    
    return events


def run_scraper():
    """Esegue lo scraping completo"""
    
    print("=" * 60)
    print(f"🚀 EVENTOON SCRAPER — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    all_events = []
    
    for city, fonti in FONTI.items():
        print(f"\n📍 {city.upper()}")
        print("-" * 40)
        
        for fonte in fonti:
            print(f"  📰 {fonte['nome']}...")
            
            # 1. Scarica la pagina
            text = fetch_page(fonte["url"])
            if not text:
                continue
            
            print(f"     ✓ Scaricati {len(text)} caratteri")
            
            # 2. Estrai eventi con Claude
            events = extract_events(
                text, 
                fonte["nome"], 
                fonte["tipo"],
                FONTI_CITY_NAMES.get(city, city)
            )
            
            print(f"     ✓ Estratti {len(events)} eventi/mostre")
            all_events.extend(events)
    
    # 3. Assegna proprietà visive
    all_events = assign_visual_properties(all_events)
    
    # 4. Rimuovi duplicati (stesso titolo + stessa città)
    seen = set()
    unique_events = []
    for e in all_events:
        key = (e.get("title", "").lower().strip(), e.get("cityKey", ""))
        if key not in seen:
            seen.add(key)
            unique_events.append(e)
    
    # 5. Salva il file JSON
    output = {
        "lastUpdated": datetime.now().isoformat(),
        "totalEvents": len(unique_events),
        "events": unique_events
    }
    
    output_path = os.path.join(os.path.dirname(__file__), "public", "events.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"✅ COMPLETATO: {len(unique_events)} eventi salvati in events.json")
    print(f"   Ultimo aggiornamento: {output['lastUpdated']}")
    print(f"{'=' * 60}")


# Nomi città per il prompt
FONTI_CITY_NAMES = {
    "reggio-emilia": "Reggio Emilia",
    "bologna": "Bologna",
    "parma": "Parma",
    "modena": "Modena",
}


if __name__ == "__main__":
    run_scraper()
