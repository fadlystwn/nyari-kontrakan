# Security Implementation Guide

This document outlines the security measures implemented in the Property Scraper backend and provides guidance for secure deployment.

## Implemented Security Features

### 1. API Authentication
- **API Key Authentication**: All API endpoints now require API key authentication via `X-API-Key` header
- **Development Mode**: Authentication can be disabled in development by leaving `API_KEY` empty
- **Health Check Exception**: Health check endpoint supports optional authentication for monitoring

### 2. CORS Configuration
- **Restricted Origins**: CORS is now restricted to specific origins defined in `ALLOWED_ORIGINS`
- **Environment-based**: Default localhost origins for development, should be configured for production
- **Method Restrictions**: Only allows GET, POST, and OPTIONS methods

### 3. Rate Limiting
- **Global Rate Limiting**: Implemented using `slowapi` library
- **Endpoint-specific**: Curation trigger endpoint limited to 5 requests per minute per IP
- **Prevention**: Protects against DoS attacks and API abuse

### 4. Security Headers
- **X-Content-Type-Options**: Prevents MIME-sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables XSS protection
- **Strict-Transport-Security**: Enforces HTTPS connections
- **Content-Security-Policy**: Restricts content sources

### 5. Database Security
- **Strong Passwords**: Database password changed to strong credential
- **No Port Exposure**: PostgreSQL port no longer exposed to host network
- **SSL/TLS Support**: Database connections support SSL with configurable mode
- **Internal Network**: Database accessible only via Docker internal network

### 6. Docker Security
- **Resource Limits**: CPU and memory limits implemented for all containers
- **Resource Reservations**: Minimum resources guaranteed for each service
- **Network Isolation**: Services communicate via internal Docker network
- **No Root Access**: PostgreSQL runs as non-root user by default

### 7. API Documentation Security
- **Environment-based**: API docs (`/docs`, `/redoc`) only available in development
- **Production Protection**: Documentation endpoints disabled in production environment
- **Reduced Attack Surface**: Limits information available to potential attackers

## Configuration

### Environment Variables

```bash
# Database Configuration
POSTGRES_DB=scraper_db
POSTGRES_USER=scraper_user
POSTGRES_PASSWORD=CHANGE_THIS_TO_A_STRONG_UNIQUE_PASSWORD
DATABASE_SSL_MODE=require  # Options: disable, allow, prefer, require, verify-ca, verify-full

# API Security
API_KEY=CHANGE_THIS_TO_A_STRONG_API_KEY
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=development  # Options: development, production

# Proxy Configuration
PROXY_LIST=

# Gemini API
GEMINI_API_KEY=
CURATION_BATCH_SIZE=10
CURATION_RATE_LIMIT_DELAY=1

# Scraper Configuration
SCRAPE_ON_STARTUP=true
```

### SSL/TLS Modes

- `disable`: No SSL
- `allow`: Try SSL, fall back to non-SSL
- `prefer`: Try SSL, fall back to non-SSL (default)
- `require`: Require SSL (recommended for production)
- `verify-ca`: Require SSL + verify CA certificate
- `verify-full`: Require SSL + verify CA + verify hostname

## Deployment Guide

### Development Setup

1. Copy `.env.template` to `.env`
2. Set `ENVIRONMENT=development`
3. Set `API_KEY` (optional for development)
4. Set `ALLOWED_ORIGINS` to your frontend URL
5. Set `DATABASE_SSL_MODE=prefer`
6. Start services: `docker-compose up`

### Production Setup

1. Copy `.env.template` to `.env`
2. Set `ENVIRONMENT=production`
3. Set strong `API_KEY` (required)
4. Set `ALLOWED_ORIGINS` to production frontend URL
5. Set `DATABASE_SSL_MODE=require` or higher
6. Generate strong `POSTGRES_PASSWORD`
7. Set `GEMINI_API_KEY` if using curation
8. Start services: `docker-compose up -d`

### API Usage

#### With Authentication
```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/listings
```

#### Health Check (Optional Authentication)
```bash
curl http://localhost:8000/health
```

## Security Best Practices

### Immediate Actions Required
1. **Change Default Passwords**: Replace all default passwords with strong, unique ones
2. **Set API Key**: Configure a strong API key for production
3. **Configure Origins**: Set appropriate CORS origins for your environment
4. **Enable SSL**: Set `DATABASE_SSL_MODE=require` for production

### Ongoing Security Maintenance
1. **Regular Updates**: Keep dependencies updated
2. **Monitor Logs**: Review logs for security events
3. **Rotate Keys**: Periodically rotate API keys and passwords
4. **Audit Access**: Review who has access to API keys
5. **Backup**: Regular database backups with encryption

### Monitoring
- Monitor rate limit violations
- Track failed authentication attempts
- Review database connection logs
- Monitor resource usage alerts

## Troubleshooting

### Authentication Issues
- Verify API key is set in environment
- Check `X-API-Key` header is being sent
- Ensure API key matches exactly

### CORS Issues
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check browser console for CORS errors
- Ensure proper protocol (http vs https)

### Database Connection Issues
- Verify PostgreSQL container is running
- Check database credentials
- Verify SSL mode is compatible
- Review Docker network configuration

### Rate Limiting Issues
- Check rate limit configuration
- Verify IP address is correct
- Review rate limit logs

## Security Checklist

- [ ] Change all default passwords
- [ ] Set strong API key
- [ ] Configure CORS origins
- [ ] Enable SSL for database
- [ ] Set environment to production
- [ ] Remove database port exposure
- [ ] Configure resource limits
- [ ] Test authentication
- [ ] Test rate limiting
- [ ] Review security headers
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review logs regularly

## Additional Recommendations

1. **Implement HTTPS**: Use reverse proxy (nginx) with SSL/TLS
2. **Add Logging**: Implement comprehensive security logging
3. **Input Validation**: Add additional input sanitization
4. **Dependency Scanning**: Implement automated dependency vulnerability scanning
5. **Secrets Management**: Use proper secrets management solution for production
6. **Network Security**: Implement network policies and firewalls
7. **Regular Audits**: Schedule regular security audits
8. **Incident Response**: Create security incident response plan

## Contact

For security concerns or questions about this implementation, please contact the development team.