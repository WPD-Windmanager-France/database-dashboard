import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { DatabaseEnv, getDatabaseConfig } from '../config/database'

// Database types - will be extended as we add more tables
export interface Database {
  public: {
    Tables: {
      [key: string]: {
        Row: Record<string, unknown>
        Insert: Record<string, unknown>
        Update: Record<string, unknown>
      }
    }
  }
}

/**
 * Create a Supabase client for the current request
 * In serverless environments, clients should be created per-request
 */
export function getSupabaseClient(env: DatabaseEnv): SupabaseClient<Database> {
  const config = getDatabaseConfig(env)

  return createClient<Database>(config.url, config.anonKey, {
    auth: {
      persistSession: false,  // No session persistence in serverless
      autoRefreshToken: false
    }
  })
}

/**
 * Create a Supabase admin client with service role key
 * Use for operations that bypass RLS (Row Level Security)
 */
export function getSupabaseAdminClient(env: DatabaseEnv): SupabaseClient<Database> {
  const config = getDatabaseConfig(env)

  if (!config.serviceRoleKey) {
    throw new Error('SUPABASE_SERVICE_ROLE_KEY is required for admin operations')
  }

  return createClient<Database>(config.url, config.serviceRoleKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false
    }
  })
}

/**
 * Database operation result wrapper
 */
export interface DbResult<T> {
  data: T | null
  error: string | null
  success: boolean
}

/**
 * Execute a database operation with error handling
 */
export async function dbOperation<T>(
  operation: () => Promise<{ data: T | null; error: { message: string } | null }>
): Promise<DbResult<T>> {
  try {
    const { data, error } = await operation()

    if (error) {
      return {
        data: null,
        error: error.message,
        success: false
      }
    }

    return {
      data,
      error: null,
      success: true
    }
  } catch (err) {
    return {
      data: null,
      error: err instanceof Error ? err.message : 'Unknown database error',
      success: false
    }
  }
}
