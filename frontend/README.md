# Networth Tracker Frontend

React frontend for the Networth Tracker application.

## Development Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173`

## Code Quality with ESLint and Prettier

This project uses ESLint for linting and Prettier for code formatting.

### Manual Usage

- **Check for issues**: `npm run lint`
- **Fix issues automatically**: `npm run lint:fix`
- **Format code**: `npm run format`
- **Check formatting**: `npm run format:check`
- **Run both linting and formatting**: `npm run lint-and-format`

### Configuration

**ESLint** (`eslint.config.js`):
- JavaScript/JSX linting with modern ES2025+ features
- React Hooks rules enforcement
- Browser and Node globals support
- Auto-fixable rules for common issues

**Prettier** (`.prettierrc`):
- Single quotes
- Trailing commas (ES5)
- 80 character line length
- 2-space indentation
- LF line endings

### Pre-commit Integration

To add pre-commit hooks for automatic linting and formatting:

```bash
# Install husky (optional)
npm install --save-dev husky

# Set up pre-commit hook
npx husky add .husky/pre-commit "npm run lint-and-format"
```

### VS Code Integration

For the best experience, install these VS Code extensions:

- **ESLint**: Provides real-time linting feedback
- **Prettier - Code formatter**: Format code on save
- **Auto Rename Tag**: Rename paired HTML/XML tags
- **Bracket Pair Colorizer**: Visual bracket matching

Add to your `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  }
}
```

## Build and Deploy

- **Build for production**: `npm run build`
- **Preview production build**: `npm run preview`

## Tech Stack

- **React 19.2.0** - UI framework
- **React Router 6.28.0** - Client-side routing
- **TailwindCSS 3.4.17** - Utility-first CSS
- **Recharts 2.14.1** - Chart library
- **Lucide React 0.462.0** - Icon library
- **Axios 1.7.9** - HTTP client
- **Vite 6.0.7** - Build tool and dev server
