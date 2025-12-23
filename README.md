# Networth Tracker

A full-stack web application to track your net worth across multiple asset types in Australian Dollars (AUD).

## Features

- **Dashboard** - Overview of total net worth with allocation pie chart
- **Bank Accounts** - Track multiple bank accounts (savings, transaction, term deposit, offset)
- **Superannuation** - Track super fund balances with employer/personal contributions
- **ETF Holdings** - Track ETF investments with buy/sell transactions and dividend tracking
- **Crypto Holdings** - Track cryptocurrency with transactions, staking rewards, and airdrops
- **Stock Holdings** - Track individual stocks with transactions and dividend tracking

## Tech Stack

### Backend
- Django 5.2
- Django REST Framework
- SQLite (default, easily switchable to PostgreSQL)

### Frontend
- React 18
- React Router
- TailwindCSS
- Recharts (for charts)
- Lucide React (icons)
- Axios

## Setup Instructions

### Prerequisites
- Python 3.14.2+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies and create virtual environment:
```bash
uv sync
```

4. Run migrations:
```bash
uv run python manage.py migrate
```

5. (Optional) Create a superuser for admin access:
```bash
uv run python manage.py createsuperuser
```

6. Start the development server:
```bash
uv run python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## API Endpoints

### Summary
- `GET /api/summary/` - Get net worth summary across all asset types

### Bank Accounts
- `GET /api/bank-accounts/` - List all bank accounts
- `POST /api/bank-accounts/` - Create a bank account
- `GET /api/bank-accounts/{id}/` - Get a bank account
- `PUT /api/bank-accounts/{id}/` - Update a bank account
- `DELETE /api/bank-accounts/{id}/` - Delete a bank account

### Superannuation
- `GET /api/superannuation/` - List all super accounts
- `POST /api/superannuation/` - Create a super account
- `GET /api/superannuation/{id}/` - Get a super account
- `PUT /api/superannuation/{id}/` - Update a super account
- `DELETE /api/superannuation/{id}/` - Delete a super account

### ETF Holdings & Transactions
- `GET /api/etf-holdings/` - List all ETF holdings
- `POST /api/etf-holdings/` - Create an ETF holding
- `GET /api/etf-holdings/{id}/` - Get an ETF holding with transactions
- `PUT /api/etf-holdings/{id}/` - Update an ETF holding
- `DELETE /api/etf-holdings/{id}/` - Delete an ETF holding
- `GET /api/etf-transactions/` - List all ETF transactions
- `POST /api/etf-transactions/` - Create an ETF transaction
- `DELETE /api/etf-transactions/{id}/` - Delete an ETF transaction

### Crypto Holdings & Transactions
- `GET /api/crypto-holdings/` - List all crypto holdings
- `POST /api/crypto-holdings/` - Create a crypto holding
- `GET /api/crypto-holdings/{id}/` - Get a crypto holding with transactions
- `PUT /api/crypto-holdings/{id}/` - Update a crypto holding
- `DELETE /api/crypto-holdings/{id}/` - Delete a crypto holding
- `GET /api/crypto-transactions/` - List all crypto transactions
- `POST /api/crypto-transactions/` - Create a crypto transaction
- `DELETE /api/crypto-transactions/{id}/` - Delete a crypto transaction

### Stock Holdings & Transactions
- `GET /api/stock-holdings/` - List all stock holdings
- `POST /api/stock-holdings/` - Create a stock holding
- `GET /api/stock-holdings/{id}/` - Get a stock holding with transactions
- `PUT /api/stock-holdings/{id}/` - Update a stock holding
- `DELETE /api/stock-holdings/{id}/` - Delete a stock holding
- `GET /api/stock-transactions/` - List all stock transactions
- `POST /api/stock-transactions/` - Create a stock transaction
- `DELETE /api/stock-transactions/{id}/` - Delete a stock transaction

## Currency

All values are in Australian Dollars (AUD). The application is configured for Australian locale formatting.

## License

MIT
