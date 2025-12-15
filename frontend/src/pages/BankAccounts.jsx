import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Landmark } from 'lucide-react';
import Card, { CardBody, CardHeader } from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input, { Select, Textarea } from '../components/Input';
import { 
  getBankAccounts, 
  createBankAccount, 
  updateBankAccount, 
  deleteBankAccount 
} from '../api';
import { formatCurrency } from '../utils/format';

const ACCOUNT_TYPES = [
  { value: 'savings', label: 'Savings' },
  { value: 'transaction', label: 'Transaction' },
  { value: 'term_deposit', label: 'Term Deposit' },
  { value: 'offset', label: 'Offset' },
  { value: 'other', label: 'Other' },
];

const initialFormData = {
  name: '',
  bank_name: '',
  account_type: 'savings',
  balance: '',
  interest_rate: '',
  notes: '',
};

export default function BankAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [formData, setFormData] = useState(initialFormData);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await getBankAccounts();
      setAccounts(response.data);
    } catch (err) {
      console.error('Failed to fetch bank accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (account = null) => {
    if (account) {
      setEditingAccount(account);
      setFormData({
        name: account.name,
        bank_name: account.bank_name,
        account_type: account.account_type,
        balance: account.balance,
        interest_rate: account.interest_rate || '',
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
        interest_rate: formData.interest_rate 
          ? parseFloat(formData.interest_rate) 
          : null,
      };

      if (editingAccount) {
        await updateBankAccount(editingAccount.id, data);
      } else {
        await createBankAccount(data);
      }
      handleCloseModal();
      fetchAccounts();
    } catch (err) {
      console.error('Failed to save bank account:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this account?')) return;
    try {
      await deleteBankAccount(id);
      fetchAccounts();
    } catch (err) {
      console.error('Failed to delete bank account:', err);
    }
  };

  const totalBalance = accounts.reduce(
    (sum, acc) => sum + parseFloat(acc.balance || 0), 
    0
  );

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bank Accounts</h1>
          <p className="text-gray-500 mt-1">Manage your bank account balances</p>
        </div>
        <Button onClick={() => handleOpenModal()}>
          <Plus size={20} />
          Add Account
        </Button>
      </div>

      {/* Summary Card */}
      <Card className="mb-8 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
        <CardBody>
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-4 rounded-full">
              <Landmark size={32} />
            </div>
            <div>
              <p className="text-blue-100 text-sm">Total Balance</p>
              <p className="text-3xl font-bold">{formatCurrency(totalBalance)}</p>
              <p className="text-blue-100 text-sm mt-1">
                {accounts.length} {accounts.length === 1 ? 'account' : 'accounts'}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Accounts List */}
      {accounts.length === 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <Landmark className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No bank accounts yet</p>
            <p className="text-gray-400 text-sm mt-1">
              Add your first bank account to start tracking
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid gap-4">
          {accounts.map((account) => (
            <Card key={account.id}>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="bg-blue-100 p-3 rounded-lg">
                      <Landmark className="text-blue-600" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {account.name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {account.bank_name} • {
                          ACCOUNT_TYPES.find(t => t.value === account.account_type)?.label
                        }
                      </p>
                      {account.interest_rate && (
                        <p className="text-xs text-green-600 mt-1">
                          {account.interest_rate}% p.a.
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(account.balance)}
                    </p>
                    <div className="flex gap-2">
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
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        title={editingAccount ? 'Edit Bank Account' : 'Add Bank Account'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Account Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Everyday Account"
            required
          />
          <Input
            label="Bank Name"
            name="bank_name"
            value={formData.bank_name}
            onChange={handleChange}
            placeholder="e.g., Commonwealth Bank"
            required
          />
          <Select
            label="Account Type"
            name="account_type"
            value={formData.account_type}
            onChange={handleChange}
            options={ACCOUNT_TYPES}
          />
          <Input
            label="Balance (AUD)"
            name="balance"
            type="number"
            step="0.01"
            value={formData.balance}
            onChange={handleChange}
            placeholder="0.00"
            required
          />
          <Input
            label="Interest Rate (% p.a.)"
            name="interest_rate"
            type="number"
            step="0.01"
            value={formData.interest_rate}
            onChange={handleChange}
            placeholder="e.g., 4.50"
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
    </div>
  );
}
