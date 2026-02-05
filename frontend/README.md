# WNDMNGR Frontend

WPD Windmanager France - Asset Management Platform (Frontend)

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   │   ├── layout.tsx # Root layout
│   │   ├── page.tsx   # Home page
│   │   └── globals.css
│   ├── components/    # React components
│   │   └── ui/        # shadcn/ui components
│   └── lib/           # Utilities
│       └── utils.ts   # cn() helper for Tailwind
├── public/            # Static assets
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Backend API

The frontend communicates with the Cloudflare Workers backend API:
- Development: `http://localhost:8787`
- Production: TBD

## Authentication

Authentication is handled via Microsoft Entra ID through the backend API.
