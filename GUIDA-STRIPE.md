# EVENTOON! — Setup Sistema Pubblicitario con Stripe

## Panoramica

Il sistema pubblicitario funziona così:
1. Un'attività apre l'app e tocca "📢 Promuovi"
2. Sceglie la categoria (corso, ristorante, locale, concerto, workshop)
3. Compila il form con foto, titolo, descrizione, date
4. Sceglie il piano (1 settimana €19, 2 settimane €29, 1 mese €49)
5. Paga con carta di credito o Apple Pay tramite Stripe
6. L'inserzione appare nel feed come card "SPONSORIZZATO"

## Setup Stripe (una volta sola, 15 minuti)

### 1. Crea Account Stripe
- Vai su https://stripe.com e registrati
- Compila i dati della tua attività (serve P.IVA o codice fiscale)
- Attiva l'account per ricevere pagamenti reali

### 2. Crea i Payment Link
Stripe ti permette di creare link di pagamento senza scrivere codice.

Vai su https://dashboard.stripe.com/payment-links e crea 3 link:

**Link 1 — Piano Settimanale**
- Nome prodotto: "EVENTOON Inserzione 1 Settimana"
- Prezzo: €19.00 (pagamento singolo)
- Spunta "Consenti codici promozionali"
- In "Dopo il pagamento" → Redirect a: `https://TUO-SITO.vercel.app/?payment=success`
- Salva e copia il link (tipo `https://buy.stripe.com/xxx`)

**Link 2 — Piano Bisettimanale**
- Nome prodotto: "EVENTOON Inserzione 2 Settimane"  
- Prezzo: €29.00
- Stesse impostazioni del Link 1

**Link 3 — Piano Mensile**
- Nome prodotto: "EVENTOON Inserzione 1 Mese"
- Prezzo: €49.00
- Stesse impostazioni del Link 1

### 3. Inserisci i Link nell'App
Apri il file `public/index.html` su GitHub e cerca questa sezione:

```javascript
const STRIPE_LINKS = {
  "1-settimana": "https://buy.stripe.com/TUO_LINK_SETTIMANALE",
  "2-settimane": "https://buy.stripe.com/TUO_LINK_BISETTIMANALE",
  "1-mese": "https://buy.stripe.com/TUO_LINK_MENSILE",
};
```

Sostituisci i 3 URL con quelli che hai copiato da Stripe.

### 4. Apple Pay
Apple Pay si attiva automaticamente in Stripe se:
- Hai verificato il tuo dominio in Stripe Dashboard → Settings → Payment Methods
- L'utente usa Safari su iPhone con Apple Pay configurato
- Il sito è servito via HTTPS (Vercel lo fa automaticamente)

Per verificare il dominio:
1. Vai su https://dashboard.stripe.com/settings/payment_methods
2. Nella sezione Apple Pay, clicca "Add new domain"
3. Inserisci il tuo dominio (es. `eventoon.vercel.app`)
4. Scarica il file di verifica e caricalo nella cartella `public/.well-known/`

## Come Funziona il Flusso

```
Utente tocca "Promuovi"
    ↓
Compila form (titolo, desc, foto, date, categoria)
    ↓
Sceglie piano (€19 / €29 / €49)
    ↓
Tocca "Paga e Pubblica"
    ↓
Redirect a Stripe Checkout (carta o Apple Pay)
    ↓
Pagamento completato → redirect al sito
    ↓
Ti arriva email da Stripe + notifica nell'app Stripe
    ↓
Tu aggiungi l'inserzione in ads.json (2 minuti)
```

## Come Pubblicare un'Inserzione Pagata

Quando ricevi il pagamento (email da Stripe):

1. Apri `public/ads.json` su GitHub
2. Clicca la matita (Edit)
3. Aggiungi un nuovo oggetto nell'array:

```json
{
  "id": "ad-004",
  "type": "corso",
  "title": "Titolo dell'inserzione",
  "business": "Nome attività",
  "location": "Indirizzo",
  "cityKey": "reggio-emilia",
  "description": "Descrizione breve",
  "image": "📷",
  "color": "#264653",
  "url": "https://sito-attività.it",
  "dateFrom": "2026-03-15",
  "dateTo": "2026-03-29",
  "plan": "2-settimane",
  "status": "active"
}
```

4. Commit — l'inserzione appare immediatamente nell'app

## Prezzi Consigliati

| Piano | Prezzo | Ideale per |
|-------|--------|------------|
| 1 settimana | €19 | Evento singolo, serata speciale |
| 2 settimane | €29 | Workshop, corso breve |
| 1 mese | €49 | Ristorante, locale, corso lungo |

Puoi modificare i prezzi in qualsiasi momento da Stripe Dashboard.

## Automazione Futura

Quando il volume cresce, puoi automatizzare la pubblicazione:
- Stripe Webhook → GitHub Action → aggiorna ads.json automaticamente
- Serve un piccolo servizio serverless (Vercel Serverless Function)
- Possiamo configurarlo quando sarà necessario

## Ricavi Attesi

Con 10 inserzioni/mese a prezzo medio €33:
- Ricavo mensile: ~€330
- Commissione Stripe (1.4% + €0.25): ~€5
- Netto: ~€325/mese

Con 30 inserzioni/mese: ~€975/mese netti.
