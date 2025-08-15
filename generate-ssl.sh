#!/usr/bin/env bash
# generate-ssl.sh
# Generates self-signed SSL certificates for HTTPS

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=IN/ST=State/L=City/O=Apollo Tyres/CN=localhost"

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "SSL certificates generated successfully in ssl/ directory"
echo "Certificate: ssl/cert.pem"
echo "Private Key: ssl/key.pem" 