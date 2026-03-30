# Deployment Guide — JS Windshields Auto Claim Form Filler

**Hosting:** Netlify (free)
**Domain:** jswindshields.com (registered on GoDaddy)
**Target URL:** `https://jswindshields.com/auto-claim-form-filler`

---

## What You're Deploying

Two files inside the `deploy/auto-claim-form-filler/` folder:
- `index.html` — the application
- `united_india_claim_form.pdf` — the blank United India claim form

---

## Step 1 — Create a Free Netlify Account

1. Go to **netlify.com**
2. Click **Sign up** → use any email or GitHub
3. Complete email verification

---

## Step 2 — Deploy the Files

1. In Netlify dashboard, click **"Add new site"** → **"Deploy manually"**
2. Drag and drop the entire `deploy/auto-claim-form-filler/` **folder** onto the upload area
3. Wait ~10 seconds — Netlify gives you a temporary URL like `https://random-name.netlify.app`
4. Test it: open the URL, verify the form loads

---

## Step 3 — Connect jswindshields.com

### 3a. Add domain in Netlify
1. In your Netlify site dashboard → **Domain management** → **Add a domain**
2. Enter: `jswindshields.com`
3. Netlify will show you nameserver values like:
   ```
   dns1.p01.nsone.net
   dns2.p01.nsone.net
   dns3.p01.nsone.net
   dns4.p01.nsone.net
   ```
   (exact values shown in your Netlify dashboard — copy them)

### 3b. Update nameservers in GoDaddy
1. Log in to GoDaddy → **My Products** → **Domains** → `jswindshields.com` → **Manage**
2. Click **DNS** tab → **Nameservers** → **Change Nameservers**
3. Select **"I'll use my own nameservers"**
4. Replace the current values (`athena.dns-parking.com`, `apollo.dns-parking.com`) with Netlify's nameservers
5. Save

### 3c. Wait for DNS propagation
- Takes **a few minutes to a few hours** (rarely up to 24 hours)
- You'll get an email from Netlify when the domain is live
- Netlify automatically provisions a free SSL certificate (HTTPS)

---

## Step 4 — Set the Subdirectory Path

After the domain connects, the site will be at `jswindshields.com` (root).
To serve at `/auto-claim-form-filler`, do one of the following:

**Option A (simplest):** In Netlify → **Site configuration** → rename the deploy path, or simply share the URL as:
`https://jswindshields.com/auto-claim-form-filler/`

This works automatically because Netlify serves `index.html` from the uploaded folder name.

> **Note:** When you drag-and-drop the `auto-claim-form-filler` folder in Step 2, Netlify preserves the folder structure. The URL `jswindshields.com/auto-claim-form-filler/` will automatically serve `index.html` from inside that folder.

---

## Step 5 — First-Time Setup for Rupak (on phone)

1. Open `https://jswindshields.com/auto-claim-form-filler/` on mobile browser
2. Enter the **Anthropic API key** (`sk-ant-...`) in the Claude API Key field
3. Tap **Save** — the key is stored in the browser (only needs to be done once per device)
4. Done — the tool is ready to use

---

## Usage (Every Claim)

1. Open the URL on phone
2. Upload the combined govt ID PDF (RC + Insurance + DL + Aadhaar + PAN)
3. Select claim type, accident date/time, place, and type
4. Tap **Generate Filled Form**
5. Wait ~15 seconds
6. Tap **Download** → print

---

## Updating the App in Future

To update the HTML (bug fix, new feature):
1. Make changes to `deploy/auto-claim-form-filler/index.html`
2. In Netlify dashboard → **Deploys** → drag and drop the updated folder again
3. Live within seconds

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not load blank claim form PDF" | Ensure `united_india_claim_form.pdf` is in the same folder as `index.html` |
| API error 401 | API key is wrong or expired — re-enter in the app |
| API error 529 | Anthropic servers overloaded — wait and retry |
| Form fields blank after generation | Scan quality of uploaded PDF is poor — use a clearer scan |
| URL not working after domain change | DNS still propagating — wait up to 24 hours |
