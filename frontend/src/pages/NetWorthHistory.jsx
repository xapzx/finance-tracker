import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Calendar, Plus, Trash2 } from 'lucide-react';
import Card, { CardBody } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input from '../components/Input';

export default function NetWorthHistory() {
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [snapshotDate, setSnapshotDate] = useState('');
  const [snapshotNotes, setSnapshotNotes] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchSnapshots();
  }, []);

  const fetchSnapshots = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/networth-snapshots/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSnapshots(data);
      }
    } catch (error) {
      console.error('Error fetching snapshots:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSnapshot = async (e) => {
    e.preventDefault();
    setCreating(true);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/networth-snapshots/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          date: snapshotDate,
          notes: snapshotNotes,
        }),
      });

      if (response.ok) {
        await fetchSnapshots();
        setIsModalOpen(false);
        setSnapshotDate('');
        setSnapshotNotes('');
      }
    } catch (error) {
      console.error('Error creating snapshot:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSnapshot = async (id) => {
    if (!confirm('Are you sure you want to delete this snapshot?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/networth-snapshots/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchSnapshots();
      }
    } catch (error) {
      console.error('Error deleting snapshot:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const chartData = snapshots.map(snapshot => ({
    date: formatDate(snapshot.date),
    'Total Assets': parseFloat(snapshot.total_assets),
    'Bank Accounts': parseFloat(snapshot.bank_accounts),
    'Superannuation': parseFloat(snapshot.superannuation),
    'ETF Holdings': parseFloat(snapshot.etf_holdings),
    'Stock Holdings': parseFloat(snapshot.stock_holdings),
    'Crypto Holdings': parseFloat(snapshot.crypto_holdings),
  })).reverse();

  const latestSnapshot = snapshots[0];
  const previousSnapshot = snapshots[1];

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Net Worth History</h1>
          <p className="text-gray-500 mt-1">Track your net worth over time</p>
        </div>

        <div className="flex justify-end">
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Snapshot
          </Button>
        </div>
      </div>

      {latestSnapshot && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardBody>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Current Net Worth</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(latestSnapshot.total_assets)}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    as of {formatDate(latestSnapshot.date)}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          {previousSnapshot && (
            <>
              <Card>
                <CardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Change</p>
                      <p className={`text-2xl font-bold ${
                        parseFloat(latestSnapshot.change_from_previous) >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}>
                        {formatCurrency(latestSnapshot.change_from_previous)}
                      </p>
                    </div>
                    {parseFloat(latestSnapshot.change_from_previous) >= 0 ? (
                      <TrendingUp className="w-8 h-8 text-green-600" />
                    ) : (
                      <TrendingDown className="w-8 h-8 text-red-600" />
                    )}
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardBody>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Change %</p>
                      <p className={`text-2xl font-bold ${
                        parseFloat(latestSnapshot.change_percentage) >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}>
                        {parseFloat(latestSnapshot.change_percentage).toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </>
          )}
        </div>
      )}

      {chartData.length > 0 && (
        <Card className="mb-8">
          <CardBody>
            <h2 className="text-xl font-semibold mb-4">Net Worth Over Time</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Total Assets"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      )}

      {chartData.length > 0 && (
        <Card className="mb-8">
          <CardBody>
            <h2 className="text-xl font-semibold mb-4">Asset Breakdown Over Time</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Line type="monotone" dataKey="Bank Accounts" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="Superannuation" stroke="#f59e0b" strokeWidth={2} />
                <Line type="monotone" dataKey="ETF Holdings" stroke="#8b5cf6" strokeWidth={2} />
                <Line type="monotone" dataKey="Stock Holdings" stroke="#ec4899" strokeWidth={2} />
                <Line type="monotone" dataKey="Crypto Holdings" stroke="#06b6d4" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      )}

      <Card className="mb-8">
        <CardBody>
          <h2 className="text-xl font-semibold mb-4">Snapshot History</h2>
          <div className="space-y-6">
            {snapshots.map((snapshot) => (
              <div key={snapshot.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {formatDate(snapshot.date)}
                    </h3>
                    <p className="text-2xl font-bold text-blue-600 mt-1">
                      {formatCurrency(snapshot.total_assets)}
                    </p>
                    {parseFloat(snapshot.change_from_previous) !== 0 && (
                      <p className={`text-sm mt-1 ${
                        parseFloat(snapshot.change_from_previous) >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}>
                        {parseFloat(snapshot.change_from_previous) >= 0 ? '+' : ''}
                        {formatCurrency(snapshot.change_from_previous)}
                        {' '}
                        ({parseFloat(snapshot.change_percentage).toFixed(2)}%)
                      </p>
                    )}
                    {snapshot.notes && (
                      <p className="text-sm text-gray-500 mt-2">{snapshot.notes}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteSnapshot(snapshot.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                {snapshot.asset_snapshots && snapshot.asset_snapshots.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Asset Breakdown</h4>
                    <div className="space-y-4">
                      {/* Group assets by type */}
                      {['bank', 'super', 'etf', 'stock', 'crypto'].map((type) => {
                        const assetsOfType = snapshot.asset_snapshots.filter(a => a.asset_type === type);
                        if (assetsOfType.length === 0) return null;
                        
                        const categoryTotal = assetsOfType.reduce((sum, a) => sum + parseFloat(a.value), 0);
                        const categoryLabels = {
                          bank: 'Bank Accounts',
                          super: 'Superannuation',
                          etf: 'ETF Holdings',
                          stock: 'Stock Holdings',
                          crypto: 'Cryptocurrency'
                        };

                        return (
                          <div key={type} className="border-l-4 border-blue-500 pl-3">
                            <div className="flex justify-between items-center mb-2">
                              <h5 className="text-sm font-semibold text-gray-700">
                                {categoryLabels[type]}
                              </h5>
                              <span className="text-sm font-bold text-blue-600">
                                {formatCurrency(categoryTotal)}
                              </span>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                              {assetsOfType.map((asset, idx) => (
                                <div key={idx} className="bg-gray-50 p-2 rounded">
                                  <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                      <p className="text-sm font-medium text-gray-900">
                                        {asset.asset_name}
                                      </p>
                                      {asset.asset_identifier && (
                                        <p className="text-xs text-gray-500">{asset.asset_identifier}</p>
                                      )}
                                      {asset.quantity && asset.price_per_unit && (
                                        <p className="text-xs text-gray-500 mt-1">
                                          {parseFloat(asset.quantity).toFixed(4)} @ {formatCurrency(asset.price_per_unit)}
                                        </p>
                                      )}
                                    </div>
                                    <p className="text-sm font-semibold text-gray-900 ml-2">
                                      {formatCurrency(asset.value)}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Net Worth Snapshot">
        <form onSubmit={handleCreateSnapshot} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <Input
              type="date"
              value={snapshotDate}
              onChange={(e) => setSnapshotDate(e.target.value)}
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              The snapshot will automatically calculate your current net worth as of this date.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes (Optional)
            </label>
            <textarea
              value={snapshotNotes}
              onChange={(e) => setSnapshotNotes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Add any notes about this snapshot..."
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={creating}>
              {creating ? 'Creating...' : 'Create Snapshot'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
