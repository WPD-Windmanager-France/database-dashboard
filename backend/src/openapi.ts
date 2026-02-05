// OpenAPI 3.0 Specification for WPD Windmanager API
export const openAPISpec = {
  openapi: '3.0.3',
  info: {
    title: 'WPD Windmanager France - Asset Management API',
    description: `
## Overview

RESTful API for managing renewable energy assets operated by WPD Windmanager France.

This API provides comprehensive access to wind farm portfolio data, including:
- **Farm Management**: CRUD operations on wind and solar farm entities
- **Asset Information**: Technical specifications, turbine details, substations
- **Performance Data**: Historical and target performance metrics
- **Administrative Data**: Contracts, tariffs, compliance information

## Authentication

All protected endpoints require a valid **Microsoft Entra ID** (Azure AD) Bearer token.
Access is restricted to authorized WPD personnel with @wpd.fr email addresses.

## B2 API REST Certification

This API satisfies the B2 certification requirements:
- **C8**: Automated data extraction from database
- **C9**: SQL-based data queries with joins and aggregations
- **C10**: Data aggregation and transformation rules
- **C12**: OpenAPI documentation (this document)
    `.trim(),
    version: '1.0.0',
    contact: {
      name: 'WPD Windmanager France',
      url: 'https://www.wpd.fr'
    },
    license: {
      name: 'Proprietary',
      url: 'https://www.wpd.fr'
    }
  },
  servers: [
    {
      url: 'http://localhost:8787',
      description: 'Local Development'
    },
    {
      url: 'https://wndmngr-api.wpd.workers.dev',
      description: 'Production (Cloudflare Workers)'
    }
  ],
  tags: [
    { name: 'Health', description: 'Service health and status endpoints' },
    { name: 'Authentication', description: 'Microsoft Entra ID OAuth 2.0 authentication' },
    { name: 'Database', description: 'Database connectivity and diagnostics' },
    { name: 'Farms', description: 'Wind and solar farm asset management' },
    { name: 'Analytics', description: 'Aggregated statistics and performance metrics' }
  ],
  paths: {
    '/': {
      get: {
        tags: ['Health'],
        summary: 'API Information',
        description: 'Returns basic API metadata and version information',
        operationId: 'getApiInfo',
        responses: {
          '200': {
            description: 'Successful response with API information',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    message: { type: 'string', example: 'Hello World' },
                    api: { type: 'string', example: 'WPD Windmanager API' },
                    version: { type: 'string', example: '1.0.0' }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/health': {
      get: {
        tags: ['Health'],
        summary: 'Health Check',
        description: 'Returns the current health status of the API service',
        operationId: 'healthCheck',
        responses: {
          '200': {
            description: 'Service is healthy',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    status: { type: 'string', example: 'healthy' },
                    timestamp: { type: 'string', format: 'date-time' }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/auth/login': {
      get: {
        tags: ['Authentication'],
        summary: 'Initiate OAuth 2.0 Login',
        description: 'Redirects the user directly to the Microsoft Entra ID authorization page.',
        operationId: 'initiateLogin',
        responses: {
          '302': {
            description: 'Redirect to Azure Login'
          }
        }
      }
    },
    '/auth/callback': {
      get: {
        tags: ['Authentication'],
        summary: 'OAuth 2.0 Callback',
        description: 'Handles the OAuth callback from Microsoft Entra ID. Exchanges the authorization code for tokens and redirects back to the frontend.',
        operationId: 'handleOAuthCallback',
        parameters: [
          { name: 'code', in: 'query', required: true, description: 'Authorization code from Entra ID', schema: { type: 'string' } }
        ],
        responses: {
          '302': {
            description: 'Redirect to Frontend with tokens'
          },
          '400': { description: 'Authentication failed' }
        }
      }
    },
    '/db/status': {
      get: {
        tags: ['Database'],
        summary: 'Database Connection Status',
        description: 'Verifies connectivity to the Supabase PostgreSQL database and returns response time metrics',
        operationId: 'getDatabaseStatus',
        responses: {
          '200': {
            description: 'Database status information',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    status: { type: 'string', enum: ['healthy', 'degraded', 'error'], description: 'Current database health status' },
                    message: { type: 'string' },
                    responseTimeMs: { type: 'integer', description: 'Database query response time in milliseconds' },
                    timestamp: { type: 'string', format: 'date-time' }
                  }
                }
              }
            }
          },
          '503': { description: 'Database connection failed' }
        }
      }
    },
    '/db/tables': {
      get: {
        tags: ['Database'],
        summary: 'List Database Tables',
        description: 'Returns a list of all tables in the public schema of the database.',
        operationId: 'listTables',
        responses: {
          '200': {
            description: 'List of tables',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    tables: { type: 'array', items: { type: 'object' } },
                    count: { type: 'integer' }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/db/schema': {
      get: {
        tags: ['Database'],
        summary: 'Get Detailed Database Schema',
        description: 'Returns a comprehensive JSON representation of all tables and their columns (types, nullability) in the public schema.',
        operationId: 'getDatabaseSchema',
        responses: {
          '200': {
            description: 'Detailed schema information',
            content: {
              'application/json': {
                schema: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      table_name: { type: 'string' },
                      columns: {
                        type: 'array',
                        items: {
                          type: 'object',
                          properties: {
                            column_name: { type: 'string' },
                            data_type: { type: 'string' },
                            is_nullable: { type: 'string' }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    '/me': {
      get: {
        tags: ['Authentication'],
        summary: 'Get Current User',
        description: 'Returns profile information for the currently authenticated user based on their JWT token claims',
        operationId: 'getCurrentUser',
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'User profile information',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/User' }
              }
            }
          },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '403': { description: 'Forbidden - email domain not authorized' }
        }
      }
    },
    '/farms': {
      get: {
        tags: ['Farms'],
        summary: 'List All Farms',
        description: 'Retrieves a paginated list of all wind and solar farm assets in the portfolio, including their type classification',
        operationId: 'listFarms',
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'Successful response with farm list',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    farms: {
                      type: 'array',
                      items: { $ref: '#/components/schemas/FarmWithType' }
                    },
                    count: { type: 'integer', description: 'Total number of farms returned' }
                  }
                }
              }
            }
          },
          '401': { description: 'Unauthorized - missing or invalid token' }
        }
      },
      post: {
        tags: ['Farms'],
        summary: 'Create New Farm',
        description: 'Creates a new wind or solar farm asset in the database. The farm code must be unique across the portfolio.',
        operationId: 'createFarm',
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          description: 'Farm data to create',
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/FarmInput' }
            }
          }
        },
        responses: {
          '201': {
            description: 'Farm created successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Farm' }
              }
            }
          },
          '400': { description: 'Validation error - missing or invalid fields' },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '409': { description: 'Conflict - farm code already exists' }
        }
      }
    },
    '/farms/stats': {
      get: {
        tags: ['Analytics'],
        summary: 'Portfolio Statistics',
        description: 'Returns aggregated statistics across the entire wind farm portfolio including counts by type, total turbines, and installed capacity. Implements B2 competencies C9 (SQL aggregation) and C10 (data transformation).',
        operationId: 'getPortfolioStats',
        security: [{ bearerAuth: [] }],
        responses: {
          '200': {
            description: 'Aggregated portfolio statistics',
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    totalFarms: { type: 'integer', description: 'Total number of farms in portfolio' },
                    byType: {
                      type: 'object',
                      description: 'Farm count grouped by type (Wind, Solar, Hybrid)',
                      additionalProperties: { type: 'integer' }
                    },
                    totalTurbines: { type: 'integer', description: 'Total wind turbine generators across all farms' },
                    totalPowerMW: { type: 'number', description: 'Total installed capacity in megawatts' }
                  }
                }
              }
            }
          },
          '401': { description: 'Unauthorized - missing or invalid token' }
        }
      }
    },
    '/farms/{uuid}': {
      get: {
        tags: ['Farms'],
        summary: 'Get Farm Details',
        description: 'Retrieves detailed information for a specific farm including status, location, and technical specifications',
        operationId: 'getFarmById',
        security: [{ bearerAuth: [] }],
        parameters: [
          { name: 'uuid', in: 'path', required: true, description: 'Unique farm identifier', schema: { type: 'string', format: 'uuid' } }
        ],
        responses: {
          '200': {
            description: 'Farm details retrieved successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/FarmDetails' }
              }
            }
          },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '404': { description: 'Farm not found' }
        }
      },
      put: {
        tags: ['Farms'],
        summary: 'Update Farm',
        description: 'Updates an existing farm asset. All fields are required in the request body.',
        operationId: 'updateFarm',
        security: [{ bearerAuth: [] }],
        parameters: [
          { name: 'uuid', in: 'path', required: true, description: 'Unique farm identifier', schema: { type: 'string', format: 'uuid' } }
        ],
        requestBody: {
          required: true,
          description: 'Updated farm data',
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/FarmInput' }
            }
          }
        },
        responses: {
          '200': {
            description: 'Farm updated successfully',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/Farm' }
              }
            }
          },
          '400': { description: 'Validation error - missing or invalid fields' },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '404': { description: 'Farm not found' },
          '409': { description: 'Conflict - farm code already exists' }
        }
      },
      delete: {
        tags: ['Farms'],
        summary: 'Delete Farm (Cascading)',
        description: 'Permanently deletes a farm from the database along with all associated data (substations, turbines, locations, statuses, etc.) in a single cascading operation.',
        operationId: 'deleteFarm',
        security: [{ bearerAuth: [] }],
        parameters: [
          { name: 'uuid', in: 'path', required: true, description: 'Unique farm identifier', schema: { type: 'string', format: 'uuid' } }
        ],
        responses: {
          '200': { description: 'Farm deleted successfully' },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '404': { description: 'Farm not found' },
          '409': { description: 'Conflict - cannot delete farm with related data' }
        }
      }
    },
    '/farms/{uuid}/summary': {
      get: {
        tags: ['Analytics'],
        summary: 'Farm Summary Report',
        description: 'Generates a comprehensive summary report for a specific farm, aggregating data from multiple related tables including technical details, performance metrics, and administrative information. Implements B2 competencies C8 (data extraction) and C10 (data aggregation).',
        operationId: 'getFarmSummary',
        security: [{ bearerAuth: [] }],
        parameters: [
          { name: 'uuid', in: 'path', required: true, description: 'Unique farm identifier', schema: { type: 'string', format: 'uuid' } }
        ],
        responses: {
          '200': {
            description: 'Farm summary report',
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/FarmSummary' }
              }
            }
          },
          '401': { description: 'Unauthorized - missing or invalid token' },
          '404': { description: 'Farm not found' }
        }
      }
    }
  },
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: 'Azure Entra ID access token'
      }
    },
    schemas: {
      User: {
        type: 'object',
        description: 'Authenticated user profile from Microsoft Entra ID',
        properties: {
          id: { type: 'string', description: 'Unique user identifier (OID claim from Entra ID)' },
          email: { type: 'string', format: 'email', description: 'User email address (must be @wpd.fr)' },
          name: { type: 'string', description: 'User display name' }
        }
      },
      Farm: {
        type: 'object',
        description: 'Wind or solar farm asset entity',
        properties: {
          uuid: { type: 'string', format: 'uuid', description: 'Unique farm identifier' },
          spv: { type: 'string', description: 'Special Purpose Vehicle (legal entity name)' },
          project: { type: 'string', description: 'Project name / commercial designation' },
          code: { type: 'string', description: 'Unique alphanumeric farm code (e.g., E02, EOB)', maxLength: 10 },
          farm_type_id: { type: 'integer', description: 'Farm type: 1=Wind, 2=Solar, 3=Hybrid', enum: [1, 2, 3] }
        }
      },
      FarmInput: {
        type: 'object',
        description: 'Request body for creating or updating a farm',
        required: ['spv', 'project', 'code', 'farm_type_id'],
        properties: {
          spv: { type: 'string', description: 'Special Purpose Vehicle (legal entity name)', minLength: 1, maxLength: 100 },
          project: { type: 'string', description: 'Project name / commercial designation', minLength: 1, maxLength: 100 },
          code: { type: 'string', description: 'Unique alphanumeric farm code', minLength: 1, maxLength: 10 },
          farm_type_id: { type: 'integer', description: 'Farm type: 1=Wind, 2=Solar, 3=Hybrid', enum: [1, 2, 3] }
        }
      },
      FarmWithType: {
        allOf: [
          { $ref: '#/components/schemas/Farm' },
          {
            type: 'object',
            properties: {
              farm_types: {
                type: 'object',
                properties: {
                  type_title: { type: 'string', enum: ['Wind', 'Solar', 'Hybrid'] }
                }
              }
            }
          }
        ]
      },
      FarmDetails: {
        allOf: [
          { $ref: '#/components/schemas/FarmWithType' },
          {
            type: 'object',
            properties: {
              farm_statuses: {
                type: 'object',
                properties: {
                  farm_status: { type: 'string' },
                  tcma_status: { type: 'string' }
                }
              },
              farm_locations: {
                type: 'object',
                properties: {
                  country: { type: 'string' },
                  region: { type: 'string' },
                  department: { type: 'string' },
                  municipality: { type: 'string' }
                }
              },
              farm_turbine_details: {
                type: 'object',
                properties: {
                  turbine_count: { type: 'integer' },
                  manufacturer: { type: 'string' },
                  hub_height_m: { type: 'number' },
                  rotor_diameter_m: { type: 'number' },
                  rated_power_installed_mw: { type: 'number' },
                  total_mmw: { type: 'number' }
                }
              }
            }
          }
        ]
      },
      FarmSummary: {
        type: 'object',
        properties: {
          farm: {
            type: 'object',
            properties: {
              uuid: { type: 'string' },
              code: { type: 'string' },
              spv: { type: 'string' },
              project: { type: 'string' },
              type: { type: 'string' }
            }
          },
          status: { type: 'object' },
          location: { type: 'object' },
          technical: {
            type: 'object',
            properties: {
              turbineCount: { type: 'integer' },
              totalPowerMW: { type: 'number' },
              manufacturer: { type: 'string' },
              substationCount: { type: 'integer' },
              wtgCount: { type: 'integer' }
            }
          },
          administration: { type: 'object' },
          recentPerformances: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                year: { type: 'integer' },
                amount: { type: 'number' }
              }
            }
          }
        }
      }
    }
  }
}
