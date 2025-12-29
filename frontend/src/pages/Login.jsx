import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wallet } from 'lucide-react';
import Card, { CardBody } from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { login, getCurrentUser } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useAuth();

  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(formData.username, formData.password);
      const tokens = response.data;

      // Store tokens temporarily to fetch user
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      const userResponse = await getCurrentUser();
      loginUser(tokens, userResponse.data);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid username or password');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='min-h-screen bg-gray-50 flex items-center justify-center p-4'>
      <div className='w-full max-w-md'>
        <div className='text-center mb-8'>
          <div className='inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4'>
            <Wallet className='text-white' size={32} />
          </div>
          <h1 className='text-2xl font-bold text-gray-900'>Networth Tracker</h1>
          <p className='text-gray-500 mt-1'>Sign in to your account</p>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className='space-y-4'>
              {error && (
                <div className='bg-red-50 text-red-600 p-3 rounded-lg text-sm'>
                  {error}
                </div>
              )}

              <Input
                label='Username'
                name='username'
                value={formData.username}
                onChange={handleChange}
                placeholder='Enter your username'
                required
              />

              <Input
                label='Password'
                name='password'
                type='password'
                value={formData.password}
                onChange={handleChange}
                placeholder='Enter your password'
                required
              />

              <Button type='submit' className='w-full' disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className='mt-6 text-center text-sm text-gray-500'>
              Don't have an account?{' '}
              <Link
                to='/register'
                className='text-blue-600 hover:text-blue-700 font-medium'
              >
                Create one
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
