import { useState, useEffect } from 'react';
import {
  Landmark,
  Umbrella,
  TrendingUp,
  Bitcoin,
  BarChart3,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import Card, { CardBody, CardHeader } from '../components/Card';
import { getSummary, getNetWorthSnapshots } from '../api';
import { formatCurrency, getGainLossColor } from '../utils/format';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [summaryResponse, snapshotsResponse] = await Promise.all([
        getSummary(),
        getNetWorthSnapshots(),
      ]);
      setSummary(summaryResponse.data);
      setSnapshots(snapshotsResponse.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className='p-8 flex items-center justify-center min-h-screen'>
        <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600'></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='p-8'>
        <div className='bg-red-50 text-red-600 p-4 rounded-lg'>{error}</div>
      </div>
    );
  }

  const breakdown = summary?.breakdown || {};

  const pieData = [
    {
      name: 'Bank Accounts',
      value: parseFloat(breakdown.bank_accounts?.total || 0),
    },
    {
      name: 'Superannuation',
      value: parseFloat(breakdown.superannuation?.total || 0),
    },
    { name: 'ETFs', value: parseFloat(breakdown.etf?.market_value || 0) },
    { name: 'Crypto', value: parseFloat(breakdown.crypto?.market_value || 0) },
    { name: 'Stocks', value: parseFloat(breakdown.stocks?.market_value || 0) },
  ].filter(item => item.value > 0);

  const totalNetworth = parseFloat(summary?.total_networth || 0);
  const investmentSummary = summary?.investment_summary || {};

  // Calculate Total Savings (excluding superannuation) over time with breakdown
  const savingsChartData = snapshots
    .map(snapshot => {
      return {
        date: new Date(snapshot.date).toLocaleDateString('en-AU', {
          month: 'short',
          year: 'numeric',
        }),
        'Bank Accounts': parseFloat(snapshot.bank_accounts || 0),
        'ETF Holdings': parseFloat(snapshot.etf_holdings || 0),
        'Stock Holdings': parseFloat(snapshot.stock_holdings || 0),
        'Crypto Holdings': parseFloat(snapshot.crypto_holdings || 0),
        timestamp: new Date(snapshot.date).getTime(),
      };
    })
    .sort((a, b) => a.timestamp - b.timestamp);

  // Calculate current total savings (excluding super)
  const currentTotalSavings =
    parseFloat(breakdown.bank_accounts?.total || 0) +
    parseFloat(breakdown.etf?.market_value || 0) +
    parseFloat(breakdown.stocks?.market_value || 0) +
    parseFloat(breakdown.crypto?.market_value || 0);

  const assetCards = [
    {
      title: 'Bank Accounts',
      icon: Landmark,
      value: breakdown.bank_accounts?.total || '0',
      count: breakdown.bank_accounts?.count || 0,
      color: 'bg-blue-500',
    },
    {
      title: 'Superannuation',
      icon: Umbrella,
      value: breakdown.superannuation?.total || '0',
      count: breakdown.superannuation?.count || 0,
      color: 'bg-green-500',
    },
    {
      title: 'ETFs',
      icon: TrendingUp,
      value: breakdown.etf?.market_value || '0',
      count: breakdown.etf?.count || 0,
      gain: breakdown.etf?.unrealised_gain || '0',
      color: 'bg-amber-500',
    },
    {
      title: 'Crypto',
      icon: Bitcoin,
      value: breakdown.crypto?.market_value || '0',
      count: breakdown.crypto?.count || 0,
      gain: breakdown.crypto?.unrealised_gain || '0',
      color: 'bg-purple-500',
    },
    {
      title: 'Stocks',
      icon: BarChart3,
      value: breakdown.stocks?.market_value || '0',
      count: breakdown.stocks?.count || 0,
      gain: breakdown.stocks?.unrealised_gain || '0',
      color: 'bg-pink-500',
    },
  ];

  return (
    <div className='p-8'>
      <div className='mb-8'>
        <h1 className='text-3xl font-bold text-gray-900'>Dashboard</h1>
        <p className='text-gray-500 mt-1'>Overview of your net worth</p>
      </div>

      {/* Total Networth Card */}
      <Card className='mb-8 bg-gradient-to-r from-blue-600 to-blue-700 text-white'>
        <CardBody>
          <div className='flex items-center justify-between'>
            <div>
              <p className='text-blue-100 text-sm font-medium'>
                Total Net Worth
              </p>
              <p className='text-4xl font-bold mt-2'>
                {formatCurrency(totalNetworth)}
              </p>
              <p className='text-blue-100 text-sm mt-2'>
                Australian Dollars (AUD)
              </p>
            </div>
            <div className='bg-white/20 p-4 rounded-full'>
              <Wallet size={40} />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Investment Summary */}
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-8'>
        <Card>
          <CardBody>
            <div className='flex items-center gap-4'>
              <div className='bg-blue-100 p-3 rounded-lg'>
                <DollarSign className='text-blue-600' size={24} />
              </div>
              <div>
                <p className='text-sm text-gray-500'>Total Invested</p>
                <p className='text-xl font-semibold'>
                  {formatCurrency(investmentSummary.total_invested || 0)}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className='flex items-center gap-4'>
              <div
                className={`p-3 rounded-lg ${
                  parseFloat(investmentSummary.total_unrealised_gain || 0) >= 0
                    ? 'bg-green-100'
                    : 'bg-red-100'
                }`}
              >
                {parseFloat(investmentSummary.total_unrealised_gain || 0) >=
                0 ? (
                  <ArrowUpRight className='text-green-600' size={24} />
                ) : (
                  <ArrowDownRight className='text-red-600' size={24} />
                )}
              </div>
              <div>
                <p className='text-sm text-gray-500'>Unrealised Gain/Loss</p>
                <p
                  className={`text-xl font-semibold ${getGainLossColor(
                    investmentSummary.total_unrealised_gain || 0
                  )}`}
                >
                  {formatCurrency(investmentSummary.total_unrealised_gain || 0)}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <div className='flex items-center gap-4'>
              <div className='bg-green-100 p-3 rounded-lg'>
                <TrendingUp className='text-green-600' size={24} />
              </div>
              <div>
                <p className='text-sm text-gray-500'>Total Dividends</p>
                <p className='text-xl font-semibold text-green-600'>
                  {formatCurrency(investmentSummary.total_dividends || 0)}
                </p>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Total Savings Chart */}
      {savingsChartData.length > 0 && (
        <Card className='mb-8'>
          <CardBody>
            <div className='flex items-center justify-between mb-4'>
              <div>
                <h2 className='text-xl font-semibold text-gray-900'>
                  Total Savings Tracker
                </h2>
                <p className='text-sm text-gray-500 mt-1'>
                  All assets excluding superannuation
                </p>
              </div>
              <div className='text-right'>
                <p className='text-sm text-gray-500'>Current Total Savings</p>
                <p className='text-2xl font-bold text-blue-600'>
                  {formatCurrency(currentTotalSavings)}
                </p>
              </div>
            </div>
            <ResponsiveContainer width='100%' height={350}>
              <AreaChart data={savingsChartData}>
                <defs>
                  <linearGradient id='colorBank' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='5%' stopColor='#3b82f6' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#3b82f6' stopOpacity={0.3} />
                  </linearGradient>
                  <linearGradient id='colorETF' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='5%' stopColor='#f59e0b' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#f59e0b' stopOpacity={0.3} />
                  </linearGradient>
                  <linearGradient id='colorStock' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='5%' stopColor='#ec4899' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#ec4899' stopOpacity={0.3} />
                  </linearGradient>
                  <linearGradient id='colorCrypto' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='5%' stopColor='#8b5cf6' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#8b5cf6' stopOpacity={0.3} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray='3 3' stroke='#e5e7eb' />
                <XAxis
                  dataKey='date'
                  tick={{ fontSize: 12 }}
                  stroke='#6b7280'
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke='#6b7280'
                  tickFormatter={value => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={value => formatCurrency(value)}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Area
                  type='monotone'
                  dataKey='Bank Accounts'
                  stackId='1'
                  stroke='#3b82f6'
                  fill='url(#colorBank)'
                />
                <Area
                  type='monotone'
                  dataKey='ETF Holdings'
                  stackId='1'
                  stroke='#f59e0b'
                  fill='url(#colorETF)'
                />
                <Area
                  type='monotone'
                  dataKey='Stock Holdings'
                  stackId='1'
                  stroke='#ec4899'
                  fill='url(#colorStock)'
                />
                <Area
                  type='monotone'
                  dataKey='Crypto Holdings'
                  stackId='1'
                  stroke='#8b5cf6'
                  fill='url(#colorCrypto)'
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      )}

      {/* Asset Breakdown */}
      <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
        {/* Asset Cards */}
        <div className='lg:col-span-2'>
          <h2 className='text-xl font-semibold text-gray-900 mb-4'>
            Asset Breakdown
          </h2>
          <div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
            {assetCards.map(asset => (
              <Card key={asset.title}>
                <CardBody>
                  <div className='flex items-start justify-between'>
                    <div className={`${asset.color} p-3 rounded-lg`}>
                      <asset.icon className='text-white' size={24} />
                    </div>
                    <span className='text-xs text-gray-400'>
                      {asset.count} {asset.count === 1 ? 'account' : 'accounts'}
                    </span>
                  </div>
                  <div className='mt-4'>
                    <p className='text-sm text-gray-500'>{asset.title}</p>
                    <p className='text-2xl font-bold text-gray-900 mt-1'>
                      {formatCurrency(asset.value)}
                    </p>
                    {asset.gain !== undefined && (
                      <p
                        className={`text-sm mt-1 ${getGainLossColor(asset.gain)}`}
                      >
                        {parseFloat(asset.gain) >= 0 ? '+' : ''}
                        {formatCurrency(asset.gain)} unrealised
                      </p>
                    )}
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>

        {/* Pie Chart */}
        <div>
          <h2 className='text-xl font-semibold text-gray-900 mb-4'>
            Allocation
          </h2>
          <Card>
            <CardBody>
              {pieData.length > 0 ? (
                <ResponsiveContainer width='100%' height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx='50%'
                      cy='50%'
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey='value'
                    >
                      {pieData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip formatter={value => formatCurrency(value)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className='h-[300px] flex items-center justify-center text-gray-400'>
                  No assets to display
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
