// Supabase Database Configuration
// Environment variables are injected by Cloudflare Workers

export interface DatabaseEnv {
  SUPABASE_URL: string
  SUPABASE_ANON_KEY: string
  SUPABASE_SERVICE_ROLE_KEY?: string
}

export interface DatabaseConfig {
  url: string
  anonKey: string
  serviceRoleKey?: string
}

export function getDatabaseConfig(env: DatabaseEnv): DatabaseConfig {
  if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) {
    throw new Error('Missing required database environment variables: SUPABASE_URL, SUPABASE_ANON_KEY')
  }

  return {
    url: env.SUPABASE_URL,
    anonKey: env.SUPABASE_ANON_KEY,
    serviceRoleKey: env.SUPABASE_SERVICE_ROLE_KEY
  }
}
