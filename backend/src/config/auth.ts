// Azure Entra ID Configuration
// Environment variables are injected by Cloudflare Workers

export interface AuthConfig {
  tenantId: string
  clientId: string
  clientSecret: string
  redirectUri: string
  scopes: string[]
}

export interface Env {
  AZURE_TENANT_ID: string
  AZURE_CLIENT_ID: string
  AZURE_CLIENT_SECRET: string
  REDIRECT_URI?: string
}

export function getAuthConfig(env: Env): AuthConfig {
  return {
    tenantId: env.AZURE_TENANT_ID,
    clientId: env.AZURE_CLIENT_ID,
    clientSecret: env.AZURE_CLIENT_SECRET,
    redirectUri: env.REDIRECT_URI || 'http://localhost:8787/auth/callback',
    scopes: ['openid', 'profile', 'email']
  }
}

// Entra ID endpoints
export function getEntraEndpoints(tenantId: string) {
  const base = `https://login.microsoftonline.com/${tenantId}`
  return {
    authorize: `${base}/oauth2/v2.0/authorize`,
    token: `${base}/oauth2/v2.0/token`,
    jwks: `${base}/discovery/v2.0/keys`,
    issuer: `https://login.microsoftonline.com/${tenantId}/v2.0`
  }
}
