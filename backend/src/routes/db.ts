import { Hono } from 'hono'
import { Env } from '../config/auth'
import { getSupabaseClient, dbOperation } from '../lib/supabase'

const db = new Hono<{ Bindings: Env }>()

// GET /db/status - Check database connection
db.get('/status', async (c) => {
  try {
    const supabase = getSupabaseClient(c.env)

    // Test connection by attempting a simple query
    // We'll try to query any existing table or use a simple health check
    const startTime = Date.now()

    // Try to get the Supabase service status
    const { data, error } = await supabase
      .from('farms')
      .select('uuid, code, project')
      .limit(1)

    const responseTime = Date.now() - startTime

    if (error) {
      // Check if it's a "table not found" error (which means connection works)
      if (error.message.includes('does not exist') || error.code === '42P01') {
        return c.json({
          status: 'healthy',
          message: 'Database connection successful (farms table not yet created)',
          responseTimeMs: responseTime,
          timestamp: new Date().toISOString()
        })
      }

      return c.json({
        status: 'degraded',
        message: 'Database accessible but query failed',
        error: error.message,
        responseTimeMs: responseTime,
        timestamp: new Date().toISOString()
      }, 200)
    }

    return c.json({
      status: 'healthy',
      message: 'Database connection successful',
      responseTimeMs: responseTime,
      timestamp: new Date().toISOString()
    })

  } catch (err) {
    return c.json({
      status: 'error',
      message: 'Failed to connect to database',
      error: err instanceof Error ? err.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, 503)
  }
})

// GET /db/tables - List available tables in public schema
db.get('/tables', async (c) => {
  try {
    const supabase = getSupabaseClient(c.env)

    // Try to call get_tables RPC function if it exists
    const { data, error } = await supabase.rpc('get_tables')

    if (error) {
      // Return helpful message about setting up the function
      return c.json({
        message: 'To list tables, create this SQL function in Supabase:',
        sql: `
CREATE OR REPLACE FUNCTION get_tables()
RETURNS TABLE (table_name text, table_type text) AS $$
  SELECT table_name::text, table_type::text
  FROM information_schema.tables
  WHERE table_schema = 'public'
  ORDER BY table_name;
$$ LANGUAGE sql SECURITY DEFINER;`,
        error: error.message
      }, 200)
    }

    return c.json({
      tables: data,
      count: Array.isArray(data) ? (data as unknown[]).length : 0
    })

  } catch (err) {
    return c.json({
      error: err instanceof Error ? err.message : 'Unknown error'
    }, 500)
  }
})

// GET /db/query-test - Execute a simple test query
db.get('/query-test', async (c) => {
  const result = await dbOperation(async () => {
    const supabase = getSupabaseClient(c.env)

    // Query farms table using correct schema columns
    const { data, error } = await supabase
      .from('farms')
      .select('uuid, code, spv, project')
      .limit(5)

    return { data, error }
  })

  if (!result.success) {
    return c.json({
      success: false,
      message: 'Query test failed',
      error: result.error,
      hint: 'Ensure the "farms" table exists in your Supabase database'
    }, result.error?.includes('does not exist') ? 404 : 500)
  }

  return c.json({
    success: true,
    message: 'Query executed successfully',
    data: result.data,
    rowCount: Array.isArray(result.data) ? result.data.length : 0
  })
})

export default db
