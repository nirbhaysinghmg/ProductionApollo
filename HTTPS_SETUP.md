# HTTPS Setup for Apollo Tyres Chatbot

This project now runs on HTTPS instead of HTTP for enhanced security.

## SSL Certificates

The application uses self-signed SSL certificates located in the `ssl/` directory:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - Private key

## Automatic Certificate Generation

Both `start-frontend.sh` and `restart-backend.sh` scripts automatically check for SSL certificates and generate them if they don't exist.

## Manual Certificate Generation

To manually generate SSL certificates, run:
```bash
./generate-ssl.sh
```

## Accessing the Application

### Frontend
- **HTTPS URL**: `https://localhost:3006`
- **HTTP URL**: `http://localhost:3006` (fallback)

### Backend API
- **HTTPS URL**: `https://localhost:9006`
- **HTTP URL**: `http://localhost:9006` (fallback)

## Browser Security Warning

Since we're using self-signed certificates, browsers will show a security warning. You can:
1. Click "Advanced" and then "Proceed to localhost"
2. Or add the certificate to your browser's trusted certificates

## Production Deployment

For production, replace the self-signed certificates with proper SSL certificates from a trusted Certificate Authority (CA).

## Scripts

- `start-frontend.sh` - Starts the frontend server with HTTPS
- `restart-backend.sh` - Restarts the backend server with HTTPS
- `generate-ssl.sh` - Generates self-signed SSL certificates 