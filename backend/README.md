# WNDMNGR Backend API

Backend REST API pour WNDMNGR, construit avec Cloudflare Workers et le framework Hono.

## Prerequisites

- Node.js 20+ (recommandé) ou 22+
- npm
- Compte Cloudflare (pour le déploiement)

## Installation

```bash
cd backend
npm install --ignore-scripts
```

> **Note Windows**: Sur certains environnements Windows avec restrictions de sécurité, utilisez `--ignore-scripts` pour contourner les blocages de binaires.

## Développement local

```bash
# Option 1: Wrangler (utilise workerd - peut être bloqué sur Windows)
npm run dev

# Option 2: Node.js (recommandé sur Windows avec restrictions)
npm run dev:node
```

Le serveur sera accessible sur `http://localhost:8787`

## Scripts disponibles

| Script | Description |
|--------|-------------|
| `npm run dev` | Serveur Wrangler (workerd) |
| `npm run dev:node` | Serveur Node.js (contourne restrictions Windows) |
| `npm run build:node` | Compile TypeScript pour Node.js |
| `npm run deploy` | Déploie sur Cloudflare Workers |
| `npm run typecheck` | Vérifie les types TypeScript |

## Endpoints

### Public

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Hello World - Info API |
| GET | `/health` | Health check |
| GET | `/auth/login` | Initie le flow OAuth Entra ID |
| GET | `/auth/callback` | Callback OAuth (échange code → tokens) |
| GET | `/auth/logout` | Déconnexion |

### Protected (Bearer Token requis)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/me` | Retourne les infos de l'utilisateur authentifié |

## Authentication (Microsoft Entra ID)

### Configuration requise

1. **Créer une App Registration** dans Azure Entra ID :
   - Aller dans Azure Portal → Entra ID → App registrations
   - New registration
   - Redirect URI: `http://localhost:8787/auth/callback` (dev)
   - Copier: Application (client) ID et Directory (tenant) ID

2. **Créer un Client Secret** :
   - Certificates & secrets → New client secret
   - Copier la valeur immédiatement

3. **Configurer les variables d'environnement** :

   Pour le développement local, créer `.dev.vars` :
   ```
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
   ```

   Pour la production, utiliser Wrangler secrets :
   ```bash
   npx wrangler secret put AZURE_TENANT_ID
   npx wrangler secret put AZURE_CLIENT_ID
   npx wrangler secret put AZURE_CLIENT_SECRET
   ```

### Flow OAuth 2.0

```
1. GET /auth/login     → Retourne l'URL d'auth Azure
2. Redirect vers Azure → User se connecte
3. GET /auth/callback  → Échange code contre tokens
4. Requests avec Header: Authorization: Bearer <access_token>
```

## Structure du projet

```
backend/
├── src/
│   ├── index.ts           # Point d'entrée Hono
│   ├── dev-server.ts      # Serveur Node.js pour dev local
│   ├── config/
│   │   └── auth.ts        # Configuration Entra ID
│   ├── middleware/
│   │   └── auth.ts        # Middleware JWT validation
│   └── routes/
│       └── auth.ts        # Routes OAuth (/auth/*)
├── wrangler.toml          # Configuration Cloudflare Worker
├── package.json           # Dépendances et scripts
├── tsconfig.json          # Configuration TypeScript
└── README.md              # Ce fichier
```

## Stack technique

- **Runtime**: Cloudflare Workers (Edge)
- **Framework**: [Hono](https://hono.dev/) - Ultrafast web framework
- **Language**: TypeScript
- **Bundler**: esbuild (via wrangler)

## Troubleshooting

### Windows Group Policy bloque workerd/esbuild

Si vous voyez "Ce programme est bloqué par une stratégie de groupe":

```bash
# Solution recommandée: utiliser le serveur Node.js
npm run dev:node
```

Le serveur Node.js utilise `@hono/node-server` et fonctionne sans binaires bloqués.

### npm install échoue avec esbuild

Utilisez:

```bash
npm install --ignore-scripts
```
