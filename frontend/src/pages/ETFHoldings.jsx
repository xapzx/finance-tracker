import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, TrendingUp, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import Card, { CardBody } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input, { Select, Textarea } from '../components/Input';
import { 
  getETFHoldings, 
  createETFHolding, 
  updateETFHolding, 
  deleteETFHolding,
  getETFTransactions,
  createETFTransaction,
  deleteETFTransaction,
  getETFPrice,
  refreshETFPrices
} from '../api';
import { formatCurrency, formatNumber, formatDate, getGainLossColor } from '../utils/format';

const TRANSACTION_TYPES = [
  { value: 'buy', label: 'Buy' },
  { value: 'sell', label: 'Sell' },
  { value: 'dividend', label: 'Dividend' },
  { value: 'distribution', label: 'Distribution' },
  { value: 'drp', label: 'Dividend Reinvestment' },
];

const EXCHANGES = [
  { value: 'ASX', label: 'ASX (Australian)' },
  { value: 'NYSE', label: 'NYSE (US)' },
  { value: 'NASDAQ', label: 'NASDAQ (US)' },
  { value: 'LSE', label: 'LSE (UK)' },
  { value: 'OTHER', label: 'Other' },
];

const initialHoldingForm = {
  symbol: '',
  name: '',
  exchange: 'ASX',
  units: '',
  average_price: '',
  current_price: '',
  notes: '',
};

const initialTransactionForm = {
  etf: '',
  transaction_type: 'buy',
  date: new Date().toISOString().split('T')[0],
  units: '',
  price_per_unit: '',
  total_amount: '',
  brokerage: '0',
  notes: '',
};

export default function ETFHoldings() {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [holdingModalOpen, setHoldingModalOpen] = useState(false);
  const [transactionModalOpen, setTransactionModalOpen] = useState(false);
  const [editingHolding, setEditingHolding] = useState(null);
  const [holdingForm, setHoldingForm] = useState(initialHoldingForm);
  const [transactionForm, setTransactionForm] = useState(initialTransactionForm);
  const [saving, setSaving] = useState(false);
  const [expandedHolding, setExpandedHolding] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [fetchingPrice, setFetchingPrice] = useState(false);
  const [refreshingPrices, setRefreshingPrices] = useState(false);

  useEffect(() => {
    fetchHoldings();
  }, []);

  useEffect(() => {
    const fetchCurrentPrice = async () => {
      if (holdingForm.symbol && holdingForm.symbol.trim()) {
        setFetchingPrice(true);
        try {
          const response = await getETFPrice(holdingForm.symbol.trim(), holdingForm.exchange);
          if (response.data.price) {
            setHoldingForm(prev => ({ ...prev, current_price: response.data.price.toString() }));
          }
        } catch (err) {
          console.error('Failed to fetch ETF price:', err);
        } finally {
          setFetchingPrice(false);
        }
      }
    };

    const timeoutId = setTimeout(fetchCurrentPrice, 500);
    return () => clearTimeout(timeoutId);
  }, [holdingForm.symbol, holdingForm.exchange]);

  const fetchHoldings = async () => {
    try {
      setLoading(true);
      const response = await getETFHoldings();
      setHoldings(response.data);
    } catch (err) {
      console.error('Failed to fetch ETF holdings:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async (etfId) => {
    try {
      const response = await getETFTransactions(etfId);
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    }
  };

  const toggleExpand = async (holdingId) => {
    if (expandedHolding === holdingId) {
      setExpandedHolding(null);
      setTransactions([]);
    } else {
      setExpandedHolding(holdingId);
      await fetchTransactions(holdingId);
    }
  };

  const handleRefreshPrices = async () => {
    setRefreshingPrices(true);
    try {
      await refreshETFPrices();
      await fetchHoldings(); // Refresh the list to show updated prices
    } catch (err) {
      console.error('Failed to refresh ETF prices:', err);
    } finally {
      setRefreshingPrices(false);
    }
  };

  const handleOpenHoldingModal = (holding = null) => {
    if (holding) {
      setEditingHolding(holding);
      setHoldingForm({
        symbol: holding.symbol,
        name: holding.name,
        exchange: holding.exchange || 'ASX',
        units: holding.units,
        average_price: holding.average_price,
        current_price: holding.current_price,
        notes: holding.notes || '',
      });
    } else {
      setEditingHolding(null);
      setHoldingForm(initialHoldingForm);
    }
    setHoldingModalOpen(true);
  };

  const handleCloseHoldingModal = () => {
    setHoldingModalOpen(false);
    setEditingHolding(null);
    setHoldingForm(initialHoldingForm);
  };

  const handleOpenTransactionModal = (holding) => {
    setTransactionForm({
      ...initialTransactionForm,
      etf: holding.id,
    });
    setTransactionModalOpen(true);
  };

  const handleCloseTransactionModal = () => {
    setTransactionModalOpen(false);
    setTransactionForm(initialTransactionForm);
  };

  const handleHoldingChange = (e) => {
    const { name, value } = e.target;
    setHoldingForm(prev => ({ ...prev, [name]: value }));
  };

  const handleTransactionChange = (e) => {
    const { name, value } = e.target;
    setTransactionForm(prev => ({ ...prev, [name]: value }));
  };

  const handleHoldingSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...holdingForm,
        units: parseFloat(holdingForm.units) || 0,
        average_price: parseFloat(holdingForm.average_price) || 0,
        current_price: parseFloat(holdingForm.current_price) || 0,
      };

      if (editingHolding) {
        await updateETFHolding(editingHolding.id, data);
      } else {
        await createETFHolding(data);
      }
      handleCloseHoldingModal();
      fetchHoldings();
    } catch (err) {
      console.error('Failed to save ETF holding:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleTransactionSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...transactionForm,
        units: transactionForm.units ? parseFloat(transactionForm.units) : null,
        price_per_unit: transactionForm.price_per_unit 
          ? parseFloat(transactionForm.price_per_unit) 
          : null,
        total_amount: parseFloat(transactionForm.total_amount) || 0,
        brokerage: parseFloat(transactionForm.brokerage) || 0,
      };

      await createETFTransaction(data);
      handleCloseTransactionModal();
      if (expandedHolding) {
        fetchTransactions(expandedHolding);
      }
      fetchHoldings();
    } catch (err) {
      console.error('Failed to save transaction:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteHolding = async (id) => {
    if (!confirm('Are you sure? This will delete all associated transactions.')) return;
    try {
      await deleteETFHolding(id);
      fetchHoldings();
    } catch (err) {
      console.error('Failed to delete ETF holding:', err);
    }
  };

  const handleDeleteTransaction = async (id) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await deleteETFTransaction(id);
      if (expandedHolding) {
        fetchTransactions(expandedHolding);
      }
      fetchHoldings();
    } catch (err) {
      console.error('Failed to delete transaction:', err);
    }
  };

  const totalMarketValue = holdings.reduce(
    (sum, h) => sum + parseFloat(h.market_value || 0), 
    0
  );
  const totalCostBasis = holdings.reduce(
    (sum, h) => sum + parseFloat(h.cost_basis || 0), 
    0
  );
  const totalGain = totalMarketValue - totalCostBasis;

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">ETF Holdings</h1>
          <p className="text-gray-500 mt-1">Track your ETF investments and dividends</p>
        </div>
        <div className="flex gap-3">
          <Button 
            variant="secondary" 
            onClick={handleRefreshPrices}
            disabled={refreshingPrices}
          >
            <RefreshCw size={20} className={refreshingPrices ? 'animate-spin' : ''} />
            {refreshingPrices ? 'Refreshing...' : 'Refresh Prices'}
          </Button>
          <Button onClick={() => handleOpenHoldingModal()}>
            <Plus size={20} />
            Add ETF
          </Button>
        </div>
      </div>

      {/* Summary Card */}
      <Card className="mb-8 bg-gradient-to-r from-amber-500 to-amber-600 text-white">
        <CardBody>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-white/20 p-4 rounded-full">
                <TrendingUp size={32} />
              </div>
              <div>
                <p className="text-amber-100 text-sm">Total Market Value</p>
                <p className="text-3xl font-bold">{formatCurrency(totalMarketValue)}</p>
                <p className="text-amber-100 text-sm mt-1">
                  {holdings.length} {holdings.length === 1 ? 'holding' : 'holdings'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-amber-100 text-sm">Cost Basis</p>
              <p className="text-xl font-semibold">{formatCurrency(totalCostBasis)}</p>
              <p className={`text-sm mt-1 ${totalGain >= 0 ? 'text-green-200' : 'text-red-200'}`}>
                {totalGain >= 0 ? '+' : ''}{formatCurrency(totalGain)} unrealised
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Holdings List */}
      {holdings.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <TrendingUp className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No ETF holdings yet</p>
            <p className="text-gray-400 text-sm mt-1">
              Add your first ETF to start tracking
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-4">
          {holdings.map((holding) => (
            <Card key={holding.id}>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="bg-amber-100 p-3 rounded-lg">
                      <TrendingUp className="text-amber-600" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {holding.symbol}
                      </h3>
                      <p className="text-sm text-gray-500">{holding.name}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatNumber(holding.units, 4)} units @ {formatCurrency(holding.average_price)} avg
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xl font-bold text-gray-900">
                        {formatCurrency(holding.market_value)}
                      </p>
                      <p className="text-xs text-gray-500">
                        Current: {formatCurrency(holding.current_price)}
                      </p>
                      <p className={`text-sm ${getGainLossColor(holding.unrealised_gain)}`}>
                        {parseFloat(holding.unrealised_gain) >= 0 ? '+' : ''}
                        {formatCurrency(holding.unrealised_gain)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpenTransactionModal(holding)}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Add Transaction"
                      >
                        <Plus size={18} />
                      </button>
                      <button
                        onClick={() => handleOpenHoldingModal(holding)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      >
                        <Pencil size={18} />
                      </button>
                      <button
                        onClick={() => handleDeleteHolding(holding.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                      <button
                        onClick={() => toggleExpand(holding.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {expandedHolding === holding.id ? (
                          <ChevronUp size={18} />
                        ) : (
                          <ChevronDown size={18} />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Transactions */}
                {expandedHolding === holding.id && (
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Transactions</h4>
                    {transactions.length === 0 ? (
                      <p className="text-sm text-gray-400">No transactions recorded</p>
                    ) : (
                      <div className="space-y-2">
                        {transactions.map((tx) => (
                          <div 
                            key={tx.id} 
                            className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg text-sm"
                          >
                            <div className="flex items-center gap-4">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                tx.transaction_type === 'buy' ? 'bg-green-100 text-green-700' :
                                tx.transaction_type === 'sell' ? 'bg-red-100 text-red-700' :
                                'bg-blue-100 text-blue-700'
                              }`}>
                                {TRANSACTION_TYPES.find(t => t.value === tx.transaction_type)?.label}
                              </span>
                              <span className="text-gray-600">{formatDate(tx.date)}</span>
                              {tx.units && (
                                <span className="text-gray-500">
                                  {formatNumber(tx.units, 4)} units
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="font-medium">{formatCurrency(tx.total_amount)}</span>
                              <button
                                onClick={() => handleDeleteTransaction(tx.id)}
                                className="text-gray-400 hover:text-red-600"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Holding Modal */}
      <Modal
        isOpen={holdingModalOpen}
        onClose={handleCloseHoldingModal}
        title={editingHolding ? 'Edit ETF Holding' : 'Add ETF Holding'}
      >
        <form onSubmit={handleHoldingSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Symbol"
              name="symbol"
              value={holdingForm.symbol}
              onChange={handleHoldingChange}
              placeholder="e.g., VAS"
              required
            />
            <Select
              label="Exchange"
              name="exchange"
              value={holdingForm.exchange}
              onChange={handleHoldingChange}
              options={EXCHANGES}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="relative">
              <Input
                label="Current Price"
                name="current_price"
                type="number"
                step="0.0001"
                value={holdingForm.current_price}
                onChange={handleHoldingChange}
                placeholder="0.00"
                required
              />
              {fetchingPrice && (
                <div className="absolute right-3 top-9 flex items-center gap-2 text-sm text-blue-600">
                  <TrendingUp size={16} className="animate-pulse" />
                  <span>Fetching price...</span>
                </div>
              )}
            </div>
          </div>
          <Input
            label="Name"
            name="name"
            value={holdingForm.name}
            onChange={handleHoldingChange}
            placeholder="e.g., Vanguard Australian Shares"
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Units"
              name="units"
              type="number"
              step="0.000001"
              value={holdingForm.units}
              onChange={handleHoldingChange}
              placeholder="0"
              required
            />
            <Input
              label="Average Price"
              name="average_price"
              type="number"
              step="0.0001"
              value={holdingForm.average_price}
              onChange={handleHoldingChange}
              placeholder="0.00"
              required
            />
          </div>
          <Textarea
            label="Notes"
            name="notes"
            value={holdingForm.notes}
            onChange={handleHoldingChange}
            placeholder="Optional notes..."
          />
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={handleCloseHoldingModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : editingHolding ? 'Update' : 'Add ETF'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Transaction Modal */}
      <Modal
        isOpen={transactionModalOpen}
        onClose={handleCloseTransactionModal}
        title="Add Transaction"
      >
        <form onSubmit={handleTransactionSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Type"
              name="transaction_type"
              value={transactionForm.transaction_type}
              onChange={handleTransactionChange}
              options={TRANSACTION_TYPES}
            />
            <Input
              label="Date"
              name="date"
              type="date"
              value={transactionForm.date}
              onChange={handleTransactionChange}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Units"
              name="units"
              type="number"
              step="0.000001"
              value={transactionForm.units}
              onChange={handleTransactionChange}
              placeholder="0"
            />
            <Input
              label="Price per Unit"
              name="price_per_unit"
              type="number"
              step="0.0001"
              value={transactionForm.price_per_unit}
              onChange={handleTransactionChange}
              placeholder="0.00"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Total Amount"
              name="total_amount"
              type="number"
              step="0.01"
              value={transactionForm.total_amount}
              onChange={handleTransactionChange}
              placeholder="0.00"
              required
            />
            <Input
              label="Brokerage"
              name="brokerage"
              type="number"
              step="0.01"
              value={transactionForm.brokerage}
              onChange={handleTransactionChange}
              placeholder="0.00"
            />
          </div>
          <Textarea
            label="Notes"
            name="notes"
            value={transactionForm.notes}
            onChange={handleTransactionChange}
            placeholder="Optional notes..."
          />
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={handleCloseTransactionModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Add Transaction'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
