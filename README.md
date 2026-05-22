# PriceCompare — Amazon vs Flipkart

Compare live product prices by pasting an Amazon India URL and a Flipkart URL for the same item.

## Local development

### 1. API (Python)

```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python local_server.py
```

API runs at `http://127.0.0.1:5000`.

### 2. Frontend

Open `index.html` in a browser, or serve the project root:

```bash
cd ..
python -m http.server 8080
```

Then open `http://localhost:8080`. The frontend calls `http://127.0.0.1:5000/api/compare` when hosted on localhost.

## Deploy to Vercel (free)

1. Push this folder to a new GitHub repository.
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → import the repo.
3. Framework preset: **Other** (static files at root, Python in `/api`).
4. Deploy. Your site will be at `https://your-project.vercel.app`.

Vercel runs `api/compare.py` at `/api/compare` and `api/health.py` at `/api/health`. After changing API files, redeploy from the Vercel dashboard or push to GitHub.

## API

**POST** `/api/compare`

```json
{
  "amazon_url": "https://www.amazon.in/dp/...",
  "flipkart_url": "https://www.flipkart.com/.../p/..."
}
```

**GET** `/api/health` — health check

## Notes

- Prices are scraped from public product pages; they may differ at checkout.
- Amazon may occasionally block automated requests from cloud IPs. Retry or open the product link manually if that happens.
- For personal / educational use.
