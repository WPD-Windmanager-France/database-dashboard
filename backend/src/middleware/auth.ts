import { Context, MiddlewareHandler } from 'hono'
import { createRemoteJWKSet, jwtVerify } from 'jose'
import { Env, getAuthConfig, getEntraEndpoints } from '../config/auth'

// User info extracted from JWT
export interface User {
  id: string       // oid claim
  email: string    // email or preferred_username
  name: string     // name claim
}

// Allowed email domains (empty = all domains allowed)
const ALLOWED_DOMAINS = ['wpd.fr']

// Cache JWKS to avoid fetching on every request
let jwksCache: ReturnType<typeof createRemoteJWKSet> | null = null

function getJWKS(jwksUri: string) {
  if (!jwksCache) {
    jwksCache = createRemoteJWKSet(new URL(jwksUri))
  }
  return jwksCache
}

// Auth middleware for Hono
export function authMiddleware(): MiddlewareHandler<{
  Bindings: Env
  Variables: { user: User }
}> {
  return async (c, next) => {
    const authHeader = c.req.header('Authorization')

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return c.json({ error: 'Unauthorized', message: 'Missing or invalid Authorization header' }, 401)
    }

    const token = authHeader.substring(7)
    const config = getAuthConfig(c.env)
    const endpoints = getEntraEndpoints(config.tenantId)

    try {
      const jwks = getJWKS(endpoints.jwks)

      const { payload } = await jwtVerify(token, jwks, {
        issuer: endpoints.issuer,
        audience: config.clientId
      })

      // Extract user info from claims
      const user: User = {
        id: (payload.oid as string) || (payload.sub as string) || '',
        email: (payload.email as string) || (payload.preferred_username as string) || '',
        name: (payload.name as string) || ''
      }

      // Validate email domain if restrictions are configured
      if (ALLOWED_DOMAINS.length > 0 && user.email) {
        const emailDomain = user.email.split('@')[1]?.toLowerCase()
        const isAllowed = ALLOWED_DOMAINS.some(domain => emailDomain === domain.toLowerCase())

        if (!isAllowed) {
          return c.json({
            error: 'Forbidden',
            message: `Access restricted to ${ALLOWED_DOMAINS.join(', ')} domain(s)`
          }, 403)
        }
      }

      // Attach user to context for use in routes
      c.set('user', user)

      await next()
    } catch (error) {
      console.error('JWT validation error:', error)
      return c.json({
        error: 'Unauthorized',
        message: 'Invalid or expired token'
      }, 401)
    }
  }
}
