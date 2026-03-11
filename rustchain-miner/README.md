# RustChain Testnet Faucet

A simple faucet service that provides free test RTC tokens for developers working on the RustChain testnet.

## Features

- Free test RTC tokens for developers
- 24-hour cooldown period between requests
- Daily request limits to prevent abuse
- CAPTCHA verification to prevent bots
- Simple web interface and API

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the faucet:
   ```bash
   python faucet.py
   ```

3. Access the faucet at `http://localhost:5000`

## API Endpoints

- `GET /` - Faucet web interface
- `POST /request` - Request tokens (requires JSON with walletAddress and captcha)
- `GET /stats` - Get faucet statistics

## Configuration

Edit the configuration variables at the top of `faucet.py`:

- `FAUCET_AMOUNT`: Number of RTC tokens to dispense
- `COOLDOWN_PERIOD`: Cooldown period in seconds
- `MAX_DAILY_REQUESTS`: Maximum requests per IP per day

## Production Deployment

For production deployment:

1. Use a proper database instead of in-memory storage
2. Implement real CAPTCHA verification
3. Set up proper monitoring and logging
4. Use a production WSGI server like Gunicorn
5. Set up reverse proxy with Nginx
6. Configure proper CORS policies

## Security Considerations

- Implement rate limiting
- Use HTTPS in production
- Store sensitive data securely
- Monitor for abuse and implement additional anti-bot measures

## License

This faucet is part of the RustChain ecosystem and follows the project's license terms.