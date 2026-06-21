# Vespera Frontend Development Environment Setup

Complete guide to setting up and running the Vespera frontend development environment.

## Prerequisites

### Required
- **Node.js**: v18 or higher (v20 recommended)
- **npm**: v9 or higher, or **yarn** v3+, or **pnpm** v8+
- **Git**: Latest version
- **Code Editor**: VS Code recommended

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk Space**: 2GB for node_modules and build artifacts

## Installation

### 1. Install Node.js

**Windows:**
```bash
# Using Chocolatey
choco install nodejs --version=20.0.0

# Or download from https://nodejs.org/
```

**macOS:**
```bash
# Using Homebrew
brew install node@20

# Or using nvm (Node Version Manager - recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### 2. Verify Installation

```bash
node --version      # Should be v20.x.x or higher
npm --version       # Should be v9.x.x or higher
```

### 3. Clone Repository

```bash
git clone https://github.com/vespera-labs/Vespera.git
cd Vespera/frontend
```

### 4. Install Dependencies

```bash
# Using npm (default)
npm install

# Or using yarn
yarn install

# Or using pnpm (faster alternative)
pnpm install
```

## Environment Variables

Create `.env.local` file in the `frontend/` directory with the following variables:

### Required Variables

```env
# Stellar Network Configuration
NEXT_PUBLIC_STELLAR_NETWORK=testnet
# Values: testnet, public

# Horizon Server URL
NEXT_PUBLIC_HORIZON_URL=https://horizon-testnet.stellar.org
# Testnet: https://horizon-testnet.stellar.org
# Mainnet: https://horizon.stellar.org

# Rental Contract ID (Smart Contract Address)
NEXT_PUBLIC_RENTAL_CONTRACT_ID=CCRS5O3EFCGJHQQGJMOXTHQIRGWBCQMM5D6KKFKLM2FLM4XQ2F6VLPUD
```

### Optional Variables

```env
# API Base URL (if backend is separate)
NEXT_PUBLIC_API_URL=http://localhost:3001

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_TESTNET_FAUCET=true
```

### Example .env.local

```env
NEXT_PUBLIC_STELLAR_NETWORK=testnet
NEXT_PUBLIC_HORIZON_URL=https://horizon-testnet.stellar.org
NEXT_PUBLIC_RENTAL_CONTRACT_ID=CCRS5O3EFCGJHQQGJMOXTHQIRGWBCQMM5D6KKFKLM2FLM4XQ2F6VLPUD
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_ENABLE_TESTNET_FAUCET=true
```

## Running Development Server

### Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Access Points

- **Frontend**: http://localhost:3000
- **API**: http://localhost:3001 (if running separately)
- **Stellar Testnet Horizon**: https://horizon-testnet.stellar.org

### Development Server Features

- Hot Module Replacement (HMR) - auto-refresh on code changes
- Server-side rendering (SSR)
- API routes support
- Built-in TypeScript support

## Building for Production

### Build Optimized Version

```bash
npm run build
```

This creates an optimized production build in the `.next/` directory.

### Run Production Build Locally

```bash
npm run build
npm run start
```

The production build will run at `http://localhost:3000`

### Build Output

```
.next/
├── server/      # Server-side code
├── static/      # Static assets
└── standalone/  # Standalone deployment files
```

## Testing

### Run Unit Tests

```bash
npm run test
```

### Run Tests in Watch Mode

```bash
npm run test:watch
```

### Run E2E Tests (if available)

```bash
npm run test:e2e
```

### Test Coverage

```bash
npm run test:coverage
```

## Code Quality

### Linting

```bash
npm run lint
```

### Format Code (Prettier)

```bash
npm run format
```

### Type Checking

```bash
npm run type-check
```

## IDE Setup

### Visual Studio Code (Recommended)

1. **Install Extensions:**
   - ES7+ React/Redux/React-Native snippets
   - Prettier - Code formatter
   - ESLint
   - TypeScript Vue Plugin (Volar)

2. **VS Code Settings** (`.vscode/settings.json`):
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

3. **Launch Debug Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "restart": true,
      "protocol": "inspector"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "pwa-chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    }
  ]
}
```

## Common Issues & Troubleshooting

### Issue: Port 3000 Already in Use

**Solution:**
```bash
# Kill process on port 3000
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Issue: Module Not Found Errors

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm package-lock.json
npm install
```

### Issue: Environment Variables Not Loading

**Solution:**
```bash
# Ensure .env.local exists in frontend/ directory
# Restart development server
# Verify variable names start with NEXT_PUBLIC_
```

### Issue: Stellar Network Connection Failed

**Solution:**
```bash
# Verify NEXT_PUBLIC_HORIZON_URL is correct
# Check internet connection
# Verify testnet is accessible:
curl https://horizon-testnet.stellar.org

# For mainnet, use:
# https://horizon.stellar.org
```

### Issue: Build Fails with Memory Error

**Solution:**
```bash
# Increase Node memory
NODE_OPTIONS=--max_old_space_size=4096 npm run build
```

## Performance Optimization

### Enable Next.js Analytics

Add to `next.config.js`:
```javascript
module.exports = {
  analytics: {
    provider: 'vercel',
  },
}
```

### Image Optimization

Use Next.js Image component:
```jsx
import Image from 'next/image'

export default function Hero() {
  return (
    <Image
      src="/hero.png"
      alt="Hero"
      width={1200}
      height={400}
      priority
    />
  )
}
```

## Deployment

### Deploy to Vercel (Recommended)

```bash
npm i -g vercel
vercel
```

### Deploy to Other Platforms

- **Netlify**: `npm run build` → deploy `.next` and `public/`
- **Docker**: Use Node.js base image, `npm run build && npm start`
- **Traditional Server**: Build locally, SCP `.next` directory

## Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **Stellar Docs**: https://developers.stellar.org/
- **Vespera Repository**: https://github.com/vespera-labs/Vespera
- **Horizon API Reference**: https://developers.stellar.org/api

## Contributing

When making changes to the frontend:

1. Follow the existing code style
2. Write tests for new features
3. Update documentation if needed
4. Run `npm run lint` and `npm run format`
5. Ensure all tests pass: `npm run test`

## Support

For issues or questions:
- Check existing GitHub issues
- Create a new GitHub issue with:
  - Environment details (Node version, OS)
  - Steps to reproduce
  - Error messages
  - Screenshots if applicable

---

**Last Updated:** 2026-06-21  
**Maintainer:** Vespera Development Team
