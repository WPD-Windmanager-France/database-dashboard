import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { Env } from './config/auth'
import { authMiddleware, User } from './middleware/auth'
import authRoutes from './routes/auth'

// Define app with environment bindings and variables
const app = new Hono<{
  Bindings: Env
  Variables: { user: User }
}>()

// Enable CORS for frontend
app.use('/*', cors())

// Hello World endpoint (public)
app.get('/', (c) => {
  return c.json({
    message: 'Hello World',
    api: 'WNDMNGR Backend API',
    version: '1.0.0'
  })
})

// Health check endpoint (public)
app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  })
})

// Auth routes (public)
app.route('/auth', authRoutes)

// Protected routes - require authentication
const protectedRoutes = new Hono<{
  Bindings: Env
  Variables: { user: User }
}>()

protectedRoutes.use('/*', authMiddleware())

// GET /me - Return authenticated user info
protectedRoutes.get('/me', (c) => {
  const user = c.get('user')
  return c.json({
    id: user.id,
    email: user.email,
    name: user.name
  })
})

// Mount protected routes
app.route('/', protectedRoutes)

export default app
