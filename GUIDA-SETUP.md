# EVENTOON! — Guida Completa alla Messa Online

## Cosa otterrai alla fine di questa guida

Un'app web funzionante su `eventoon.vercel.app` (o il dominio che preferisci) che:
- Si apre su iPhone e Android come un'app nativa
- Mostra eventi reali delle città dell'Emilia-Romagna
- Si aggiorna automaticamente ogni mattina alle 7:00
- Costa circa 5-10€ al mese (solo per l'API Claude che estrae gli eventi)

---

## Prerequisiti

Ti servono solo 3 account gratuiti. Tempo totale di setup: circa 30 minuti.

### 1. Account GitHub (gratuito)
Vai su https://github.com e registrati. GitHub è dove vivrà il codice dell'app.

### 2. Account Vercel (gratuito)  
Vai su https://vercel.com e registrati con il tuo account GitHub. Vercel è il server che renderà l'app accessibile online.

### 3. Chiave API Anthropic
Vai su https://console.anthropic.com, registrati, e crea una API key.
Servirà allo scraper per analizzare le pagine dei giornali.
Costo: paghi solo quello che usi, circa $0.15-0.30 al giorno = ~5-10€/mese.

---

## Passo 1: Crea il Repository su GitHub

1. Vai su https://github.com/new
2. Nome repository: `eventoon`
3. Seleziona "Public"
4. Spunta "Add a README file"
5. Clicca "Create repository"

Ora hai un repository vuoto. Devi caricarci i file del progetto.

---

## Passo 2: Carica i File del Progetto

Nella pagina del tuo repository su GitHub:

1. Clicca "Add file" → "Upload files"
2. Trascina tutti i file della cartella `eventoon-project` che hai scaricato
3. I file da caricare sono:
   - `scraper.py` — lo script che raccoglie gli eventi
   - `public/index.html` — l'app vera e propria
   - `public/events.json` — il database degli eventi
   - `.github/workflows/update-events.yml` — il timer automatico
4. Scrivi come messaggio di commit: "Prima versione EVENTOON"
5. Clicca "Commit changes"

**Attenzione alla struttura delle cartelle!** I file devono essere organizzati così:
```
eventoon/
├── scraper.py
├── public/
│   ├── index.html
│   └── events.json
└── .github/
    └── workflows/
        └── update-events.yml
```

Per creare le sottocartelle su GitHub, quando carichi un file puoi scrivere il percorso completo nel nome (es: `public/index.html`).

---

## Passo 3: Configura la Chiave API su GitHub

Lo scraper ha bisogno della tua chiave Anthropic per funzionare, ma non la mettiamo nel codice (per sicurezza). La mettiamo nei "Secrets" di GitHub:

1. Nel tuo repository, vai su **Settings** (in alto a destra)
2. Nel menu a sinistra, clicca **Secrets and variables** → **Actions**
3. Clicca **New repository secret**
4. Nome: `ANTHROPIC_API_KEY`
5. Valore: incolla la tua chiave API (inizia con `sk-ant-...`)
6. Clicca **Add secret**

---

## Passo 4: Collega Vercel

1. Vai su https://vercel.com/dashboard
2. Clicca **"Add New..."** → **"Project"**
3. Trova il tuo repository `eventoon` nella lista e clicca **"Import"**
4. Nelle impostazioni:
   - Framework Preset: **Other**
   - Root Directory: **public**  (IMPORTANTE!)
5. Clicca **"Deploy"**
6. Aspetta 30 secondi — Vercel ti darà un URL tipo `eventoon-xyz.vercel.app`

**L'app è online!** Apri quell'URL dal tuo iPhone.

---

## Passo 5: Aggiungi alla Schermata Home dell'iPhone

1. Apri Safari sul tuo iPhone
2. Vai all'URL che Vercel ti ha dato
3. Tocca l'icona di condivisione (il quadrato con la freccia in basso)
4. Scorri e tocca **"Aggiungi alla schermata Home"**
5. Dai il nome "EVENTOON!" e conferma

Ora hai un'icona sulla Home che apre l'app a schermo pieno, senza barre del browser.

---

## Passo 6: Lancia il Primo Aggiornamento Manuale

1. Su GitHub, vai al tuo repository
2. Clicca la tab **"Actions"**
3. A sinistra trovi **"Aggiorna Eventi EVENTOON"**
4. Clicca **"Run workflow"** → **"Run workflow"**
5. Aspetta 2-3 minuti — vedrai il pallino diventare verde
6. Vai su `public/events.json` nel repository: sarà pieno di eventi reali!
7. Vercel si aggiorna automaticamente — ricarica l'app sul telefono.

Da domani mattina, questo succederà automaticamente ogni giorno alle 7:00.

---

## Personalizzazione del Dominio (Opzionale)

Se vuoi un dominio personalizzato tipo `eventoon.it`:

1. Compra il dominio su un registrar (Namecheap, GoDaddy, Aruba — circa 10€/anno)
2. Su Vercel, vai nelle impostazioni del progetto → **Domains**
3. Aggiungi il tuo dominio
4. Vercel ti darà i record DNS da configurare nel registrar
5. Segui le istruzioni — in 24 ore sarà attivo

---

## Come Aggiungere Nuove Fonti

Se scopri un nuovo sito locale che pubblica eventi:

1. Apri il file `scraper.py` su GitHub
2. Clicca l'icona della matita (Edit)
3. Nella sezione `FONTI`, aggiungi una nuova voce:
```python
{
    "nome": "Nome della Testata",
    "url": "https://url-della-pagina-eventi",
    "tipo": "media"  # oppure "istituzionale" o "proloco"
},
```
4. Clicca "Commit changes"
5. Lo scraper userà la nuova fonte dal prossimo aggiornamento

---

## Come Aggiungere una Nuova Città

1. Apri `scraper.py`
2. Aggiungi una nuova sezione in `FONTI`:
```python
"ferrara": [
    {
        "nome": "FerraraToday",
        "url": "https://www.ferraratoday.it/eventi/",
        "tipo": "media"
    },
],
```
3. Aggiungi il nome in `FONTI_CITY_NAMES`:
```python
"ferrara": "Ferrara",
```
4. Commit e il prossimo aggiornamento includerà Ferrara

---

## Costi Mensili Reali

| Voce | Costo |
|------|-------|
| Hosting Vercel | Gratis (piano free) |
| GitHub | Gratis |
| Claude API (scraping giornaliero) | ~5-10€/mese |
| Dominio personalizzato (opzionale) | ~10€/anno |
| **TOTALE** | **~5-10€/mese** |

---

## Manutenzione

### Se un sito cambia indirizzo
Aggiorna l'URL nel file `scraper.py` su GitHub.

### Se lo scraper smette di funzionare
1. Vai su GitHub → Actions
2. Controlla l'ultimo run (sarà rosso se fallito)
3. Clicca per vedere l'errore
4. Di solito è un sito che ha cambiato struttura — aggiorna l'URL

### Per aggiungere eventi manualmente
Puoi anche editare direttamente il file `public/events.json` su GitHub.
L'app si aggiornerà automaticamente.

### Per lanciare un aggiornamento immediato
GitHub → Actions → "Aggiorna Eventi EVENTOON" → Run workflow

---

## Evoluzione Futura

Quando l'app avrà trazione, i prossimi passi possono essere:
- **Notifiche push** — servizio come OneSignal (gratis fino a 10K utenti)
- **Upload foto utenti** — servizio Cloudinary (gratis fino a 25K trasformazioni)
- **Database evoluto** — migrare da JSON a Supabase (gratis fino a 500MB)
- **App nativa** — se serve davvero, con Capacitor si converte in app iOS/Android
- **Effetto fumetto** — API come Replicate.com per style transfer (~$0.01/foto)

Ognuno di questi passi si può fare incrementalmente, senza ricostruire tutto.
