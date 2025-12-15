import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Umbrella, ChevronDown, ChevronUp, Calendar, TrendingUp, TrendingDown } from 'lucide-react';
import Card, { CardBody } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input, { Textarea } from '../components/Input';
import { 
  getSuperannuationAccounts, 
  createSuperannuationAccount, 
  updateSuperannuationAccount, 
  deleteSuperannuationAccount,
  getSuperSnapshots,
  createSuperSnapshot,
  deleteSuperSnapshot,
} from '../api';
import { formatCurrency, formatDate } from '../utils/format';

const initialFormData = {
  fund_name: '',
  account_name: '',
  member_number: '',
  balance: '',
  employer_contribution: '',
  personal_contribution: '',
  investment_option: '',
  notes: '',
};

const initialSnapshotForm = {
  date: new Date().toISOString().split('T')[0],
  balance: '',
  employer_contribution: '',
  personal_contribution: '',
  notes: '',
};

export default function Superannuation() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [formData, setFormData] = useState(initialFormData);
  const [saving, setSaving] = useState(false);
  
  // Snapshot state
  const [expandedAccount, setExpandedAccount] = useState(null);
  const [snapshots, setSnapshots] = useState({});
  const [snapshotModalOpen, setSnapshotModalOpen] = useState(false);
  const [snapshotAccount, setSnapshotAccount] = useState(null);
  const [snapshotForm, setSnapshotForm] = useState(initialSnapshotForm);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await getSuperannuationAccounts();
      setAccounts(response.data);
    } catch (err) {
      console.error('Failed to fetch superannuation accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (account = null) => {
    if (account) {
      setEditingAccount(account);
      setFormData({
        fund_name: account.fund_name,
        account_name: account.account_name || '',
        member_number: account.member_number || '',
        balance: account.balance,
        employer_contribution: account.employer_contribution || '',
        personal_contribution: account.personal_contribution || '',
        investment_option: account.investment_option || '',
        notes: account.notes || '',
      });
    } else {
      setEditingAccount(null);
      setFormData(initialFormData);
    }
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingAccount(null);
    setFormData(initialFormData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...formData,
        balance: parseFloat(formData.balance) || 0,
        employer_contribution: parseFloat(formData.employer_contribution) || 0,
        personal_contribution: parseFloat(formData.personal_contribution) || 0,
      };

      if (editingAccount) {
        await updateSuperannuationAccount(editingAccount.id, data);
      } else {
        await createSuperannuationAccount(data);
      }
      handleCloseModal();
      fetchAccounts();
    } catch (err) {
      console.error('Failed to save superannuation account:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this account?')) return;
    try {
      await deleteSuperannuationAccount(id);
      fetchAccounts();
    } catch (err) {
      console.error('Failed to delete superannuation account:', err);
    }
  };

  // Snapshot functions
  const toggleExpanded = async (accountId) => {
    if (expandedAccount === accountId) {
      setExpandedAccount(null);
    } else {
      setExpandedAccount(accountId);
      if (!snapshots[accountId]) {
        await fetchSnapshots(accountId);
      }
    }
  };

  const fetchSnapshots = async (accountId) => {
    try {
      const response = await getSuperSnapshots(accountId);
      setSnapshots(prev => ({ ...prev, [accountId]: response.data }));
    } catch (err) {
      console.error('Failed to fetch snapshots:', err);
    }
  };

  const handleOpenSnapshotModal = (account) => {
    setSnapshotAccount(account);
    setSnapshotForm({
      ...initialSnapshotForm,
      balance: account.balance,
    });
    setSnapshotModalOpen(true);
  };

  const handleSnapshotChange = (e) => {
    const { name, value } = e.target;
    setSnapshotForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSnapshotSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createSuperSnapshot({
        account: snapshotAccount.id,
        date: snapshotForm.date,
        balance: parseFloat(snapshotForm.balance) || 0,
        employer_contribution: parseFloat(snapshotForm.employer_contribution) || 0,
        personal_contribution: parseFloat(snapshotForm.personal_contribution) || 0,
        notes: snapshotForm.notes,
      });
      setSnapshotModalOpen(false);
      setSnapshotAccount(null);
      await fetchSnapshots(snapshotAccount.id);
    } catch (err) {
      console.error('Failed to save snapshot:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSnapshot = async (snapshotId, accountId) => {
    if (!confirm('Delete this monthly record?')) return;
    try {
      await deleteSuperSnapshot(snapshotId);
      await fetchSnapshots(accountId);
    } catch (err) {
      console.error('Failed to delete snapshot:', err);
    }
  };

  const totalBalance = accounts.reduce(
    (sum, acc) => sum + parseFloat(acc.balance || 0), 
    0
  );

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Superannuation</h1>
          <p className="text-gray-500 mt-1">Track your super fund balances</p>
        </div>
        <Button onClick={() => handleOpenModal()}>
          <Plus size={20} />
          Add Super Account
        </Button>
      </div>

      {/* Summary Card */}
      <Card className="mb-8 bg-gradient-to-r from-green-500 to-green-600 text-white">
        <CardBody>
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-4 rounded-full">
              <Umbrella size={32} />
            </div>
            <div>
              <p className="text-green-100 text-sm">Total Super Balance</p>
              <p className="text-3xl font-bold">{formatCurrency(totalBalance)}</p>
              <p className="text-green-100 text-sm mt-1">
                {accounts.length} {accounts.length === 1 ? 'fund' : 'funds'}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Accounts List */}
      {accounts.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <Umbrella className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No superannuation accounts yet</p>
            <p className="text-gray-400 text-sm mt-1">
              Add your super fund to start tracking
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <Card key={account.id}>
              <CardBody>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="bg-green-100 p-3 rounded-lg">
                      <Umbrella className="text-green-600" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {account.fund_name}
                      </h3>
                      {account.account_name && (
                        <p className="text-sm text-gray-600">{account.account_name}</p>
                      )}
                      {account.member_number && (
                        <p className="text-xs text-gray-400 mt-1">
                          Member: {account.member_number}
                        </p>
                      )}
                      {account.investment_option && (
                        <p className="text-xs text-blue-600 mt-1">
                          {account.investment_option}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(account.balance)}
                      </p>
                      <div className="text-xs text-gray-500 mt-2 space-y-1">
                        {parseFloat(account.employer_contribution) > 0 && (
                          <p>Employer: {formatCurrency(account.employer_contribution)}</p>
                        )}
                        {parseFloat(account.personal_contribution) > 0 && (
                          <p>Personal: {formatCurrency(account.personal_contribution)}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpenSnapshotModal(account)}
                        className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                        title="Record monthly balance"
                      >
                        <Calendar size={18} />
                      </button>
                      <button
                        onClick={() => handleOpenModal(account)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      >
                        <Pencil size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(account.id)}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
                {account.notes && (
                  <p className="text-sm text-gray-500 mt-3 pt-3 border-t">
                    {account.notes}
                  </p>
                )}
                
                {/* Monthly History Toggle */}
                <button
                  onClick={() => toggleExpanded(account.id)}
                  className="flex items-center gap-2 mt-4 pt-3 border-t w-full text-sm text-gray-600 hover:text-gray-900"
                >
                  {expandedAccount === account.id ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                  Monthly History
                </button>
                
                {/* Snapshots List */}
                {expandedAccount === account.id && (
                  <div className="mt-4 space-y-2">
                    {!snapshots[account.id] || snapshots[account.id].length === 0 ? (
                      <p className="text-sm text-gray-400 text-center py-4">
                        No monthly records yet. Click the calendar icon to add one.
                      </p>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-gray-500 border-b">
                              <th className="pb-2 font-medium">Date</th>
                              <th className="pb-2 font-medium text-right">Balance</th>
                              <th className="pb-2 font-medium text-right">Contributions</th>
                              <th className="pb-2 font-medium text-right">Gain/Loss</th>
                              <th className="pb-2 w-10"></th>
                            </tr>
                          </thead>
                          <tbody>
                            {snapshots[account.id].map((snapshot) => {
                              const gain = parseFloat(snapshot.investment_gain || 0);
                              return (
                                <tr key={snapshot.id} className="border-b border-gray-50">
                                  <td className="py-2">{formatDate(snapshot.date)}</td>
                                  <td className="py-2 text-right font-medium">
                                    {formatCurrency(snapshot.balance)}
                                  </td>
                                  <td className="py-2 text-right text-gray-500">
                                    {formatCurrency(snapshot.total_contributions)}
                                  </td>
                                  <td className={`py-2 text-right font-medium flex items-center justify-end gap-1 ${
                                    gain >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {gain >= 0 ? (
                                      <TrendingUp size={14} />
                                    ) : (
                                      <TrendingDown size={14} />
                                    )}
                                    {formatCurrency(Math.abs(gain))}
                                  </td>
                                  <td className="py-2">
                                    <button
                                      onClick={() => handleDeleteSnapshot(snapshot.id, account.id)}
                                      className="p-1 text-gray-400 hover:text-red-600"
                                    >
                                      <Trash2 size={14} />
                                    </button>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        title={editingAccount ? 'Edit Super Account' : 'Add Super Account'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Fund Name"
            name="fund_name"
            value={formData.fund_name}
            onChange={handleChange}
            placeholder="e.g., Australian Super"
            required
          />
          <Input
            label="Account Name"
            name="account_name"
            value={formData.account_name}
            onChange={handleChange}
            placeholder="e.g., Personal Super"
          />
          <Input
            label="Member Number"
            name="member_number"
            value={formData.member_number}
            onChange={handleChange}
            placeholder="e.g., 123456789"
          />
          <Input
            label="Current Balance (AUD)"
            name="balance"
            type="number"
            step="0.01"
            value={formData.balance}
            onChange={handleChange}
            placeholder="0.00"
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Employer Contribution"
              name="employer_contribution"
              type="number"
              step="0.01"
              value={formData.employer_contribution}
              onChange={handleChange}
              placeholder="0.00"
            />
            <Input
              label="Personal Contribution"
              name="personal_contribution"
              type="number"
              step="0.01"
              value={formData.personal_contribution}
              onChange={handleChange}
              placeholder="0.00"
            />
          </div>
          <Input
            label="Investment Option"
            name="investment_option"
            value={formData.investment_option}
            onChange={handleChange}
            placeholder="e.g., Balanced Growth"
          />
          <Textarea
            label="Notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Optional notes..."
          />
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : editingAccount ? 'Update' : 'Add Account'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Snapshot Modal */}
      <Modal
        isOpen={snapshotModalOpen}
        onClose={() => setSnapshotModalOpen(false)}
        title="Record Monthly Balance"
      >
        <form onSubmit={handleSnapshotSubmit} className="space-y-4">
          <p className="text-sm text-gray-500 mb-4">
            Record your super balance for {snapshotAccount?.fund_name} to track monthly gain/loss.
          </p>
          <Input
            label="Date"
            name="date"
            type="date"
            value={snapshotForm.date}
            onChange={handleSnapshotChange}
            required
          />
          <Input
            label="Balance (AUD)"
            name="balance"
            type="number"
            step="0.01"
            value={snapshotForm.balance}
            onChange={handleSnapshotChange}
            placeholder="0.00"
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Employer Contribution"
              name="employer_contribution"
              type="number"
              step="0.01"
              value={snapshotForm.employer_contribution}
              onChange={handleSnapshotChange}
              placeholder="This month"
            />
            <Input
              label="Personal Contribution"
              name="personal_contribution"
              type="number"
              step="0.01"
              value={snapshotForm.personal_contribution}
              onChange={handleSnapshotChange}
              placeholder="This month"
            />
          </div>
          <Textarea
            label="Notes"
            name="notes"
            value={snapshotForm.notes}
            onChange={handleSnapshotChange}
            placeholder="Optional notes..."
          />
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => setSnapshotModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Record'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
