import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wallet } from 'lucide-react';
import Card, { CardBody } from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { register, login, getCurrentUser } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useAuth();

  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    try {
      await register(formData);

      // Auto-login after registration
      const loginResponse = await login(formData.username, formData.password);
      const tokens = loginResponse.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      const userResponse = await getCurrentUser();
      loginUser(tokens, userResponse.data);
      navigate('/');
    } catch (err) {
      if (err.response?.data) {
        const data = err.response.data;
        const newErrors = {};
        Object.keys(data).forEach(key => {
          if (Array.isArray(data[key])) {
            newErrors[key] = data[key][0];
          } else {
            newErrors[key] = data[key];
          }
        });
        setErrors(newErrors);
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
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
          <h1 className='text-2xl font-bold text-gray-900'>Create Account</h1>
          <p className='text-gray-500 mt-1'>Start tracking your net worth</p>
        </div>

        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className='space-y-4'>
              {errors.general && (
                <div className='bg-red-50 text-red-600 p-3 rounded-lg text-sm'>
                  {errors.general}
                </div>
              )}

              <div className='grid grid-cols-2 gap-4'>
                <Input
                  label='First Name'
                  name='first_name'
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder='John'
                  error={errors.first_name}
                />
                <Input
                  label='Last Name'
                  name='last_name'
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder='Doe'
                  error={errors.last_name}
                />
              </div>

              <Input
                label='Username'
                name='username'
                value={formData.username}
                onChange={handleChange}
                placeholder='johndoe'
                error={errors.username}
                required
              />

              <Input
                label='Email'
                name='email'
                type='email'
                value={formData.email}
                onChange={handleChange}
                placeholder='john@example.com'
                error={errors.email}
                required
              />

              <Input
                label='Password'
                name='password'
                type='password'
                value={formData.password}
                onChange={handleChange}
                placeholder='Create a password'
                error={errors.password}
                required
              />

              <Input
                label='Confirm Password'
                name='password2'
                type='password'
                value={formData.password2}
                onChange={handleChange}
                placeholder='Confirm your password'
                error={errors.password2}
                required
              />

              <Button type='submit' className='w-full' disabled={loading}>
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            <div className='mt-6 text-center text-sm text-gray-500'>
              Already have an account?{' '}
              <Link
                to='/login'
                className='text-blue-600 hover:text-blue-700 font-medium'
              >
                Sign in
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
