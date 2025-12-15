import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Landmark, 
  Umbrella, 
  TrendingUp, 
  Bitcoin, 
  BarChart3,
  LogOut,
  Settings
} from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import BankAccounts from './pages/BankAccounts';
import Superannuation from './pages/Superannuation';
import ETFHoldings from './pages/ETFHoldings';
import CryptoHoldings from './pages/CryptoHoldings';
import StockHoldings from './pages/StockHoldings';
import SettingsPage from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/bank-accounts', icon: Landmark, label: 'Bank Accounts' },
  { path: '/superannuation', icon: Umbrella, label: 'Superannuation' },
  { path: '/etf', icon: TrendingUp, label: 'ETFs' },
  { path: '/crypto', icon: Bitcoin, label: 'Crypto' },
  { path: '/stocks', icon: BarChart3, label: 'Stocks' },
];

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

function AppLayout() {
  const { user, logoutUser } = useAuth();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold">Networth Tracker</h1>
          <p className="text-sm text-slate-400 mt-1">AUD Currency</p>
        </div>
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-slate-300 hover:bg-slate-800'
                    }`
                  }
                >
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="p-4 border-t border-slate-700">
          <div className="px-4 py-2 text-slate-300 mb-2">
            <p className="text-sm font-medium truncate">{user?.first_name || user?.username}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 w-full rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`
            }
          >
            <Settings size={18} />
            <span className="text-sm">Settings</span>
          </NavLink>
          <button
            onClick={logoutUser}
            className="flex items-center gap-3 px-4 py-2 w-full text-slate-300 hover:bg-slate-800 rounded-lg transition-colors mt-1"
          >
            <LogOut size={18} />
            <span className="text-sm">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bank-accounts" element={<BankAccounts />} />
          <Route path="/superannuation" element={<Superannuation />} />
          <Route path="/etf" element={<ETFHoldings />} />
          <Route path="/crypto" element={<CryptoHoldings />} />
          <Route path="/stocks" element={<StockHoldings />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
      />
      <Route 
        path="/register" 
        element={isAuthenticated ? <Navigate to="/" replace /> : <Register />} 
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
