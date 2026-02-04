import { serve } from '@hono/node-server'
import { config } from 'dotenv'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { Env } from './config/auth'
import { authMiddleware, User } from './middleware/auth'
import authRoutes from './routes/auth'

// Load environment variables from .dev.vars
config({ path: '.dev.vars' })

// Create env object from process.env
const env: Env = {
  AZURE_TENANT_ID: process.env.AZURE_TENANT_ID || '',
  AZURE_CLIENT_ID: process.env.AZURE_CLIENT_ID || '',
  AZURE_CLIENT_SECRET: process.env.AZURE_CLIENT_SECRET || '',
  REDIRECT_URI: process.env.REDIRECT_URI || 'http://localhost:8787/auth/callback'
}

// Create app with injected env for Node.js dev
const app = new Hono<{
  Bindings: Env
  Variables: { user: User }
}>()

// Inject env into every request context
app.use('*', async (c, next) => {
  // @ts-ignore - Inject env for local dev
  c.env = env
  await next()
})

// Enable CORS
app.use('/*', cors())

// Public routes
app.get('/', (c) => {
  return c.json({
    message: 'Hello World',
    api: 'WNDMNGR Backend API',
    version: '1.0.0'
  })
})

app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  })
})

// Auth routes
app.route('/auth', authRoutes)

// Protected routes
const protectedRoutes = new Hono<{
  Bindings: Env
  Variables: { user: User }
}>()

protectedRoutes.use('/*', authMiddleware())

protectedRoutes.get('/me', (c) => {
  const user = c.get('user')
  return c.json({
    id: user.id,
    email: user.email,
    name: user.name
  })
})

app.route('/', protectedRoutes)

// Start server
const port = 8787
console.log(`Server running at http://localhost:${port}`)
console.log(`Env loaded: AZURE_TENANT_ID=${env.AZURE_TENANT_ID ? '***' : 'NOT SET'}`)

serve({
  fetch: app.fetch,
  port
})
