# WPD Wind Manager Dashboard

Dashboard de visualisation des données éoliennes pour WPD Windmanager France, construit avec [Evidence.dev](https://evidence.dev/).

## Stack Technique

- **Frontend**: Evidence.dev (framework de BI basé sur Markdown + SQL)
- **Base de données**: Supabase (PostgreSQL)
- **Hébergement**: Cloudflare Pages

## Structure du Projet

```
├── dashboard/           # Application Evidence.dev
│   ├── pages/          # Pages Markdown avec requêtes SQL
│   ├── sources/        # Configuration des sources de données
│   └── package.json
├── docs/               # Documentation du projet
└── bmad-agent/         # Configuration BMAD
```

## Déploiement

### Cloudflare Pages

1. Connecter le repo GitHub
2. Configuration :
   - **Root Directory**: `dashboard`
   - **Build Command**: `npm run sources && npm run build`
   - **Build Output Directory**: `build`
3. Variables d'environnement :
   - `DATABASE_URL`: URL de connexion PostgreSQL Supabase

## Développement Local

```bash
cd dashboard
npm install
npm run dev
```

Le dashboard sera accessible sur `http://localhost:3000`.

## Documentation

- [Epic 1 - MVP Setup](docs/epic-1-mvp-setup.md)
- [Sprint Change Proposal](Sprint_Change_Proposal.md)
