import { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  User,
  Lock,
  Globe,
  Check,
  MapPin,
} from 'lucide-react';
import Card, { CardBody, CardHeader } from '../components/Card';
import Button from '../components/Button';
import Input, { Select } from '../components/Input';
import { useAuth } from '../context/AuthContext';
import { updateProfile, changePassword, updatePreferences } from '../api';

const COUNTRY_OPTIONS = [
  { value: 'Australia', label: 'Australia' },
  { value: 'New Zealand', label: 'New Zealand' },
  { value: 'United States', label: 'United States' },
  { value: 'United Kingdom', label: 'United Kingdom' },
  { value: 'Canada', label: 'Canada' },
  { value: 'Singapore', label: 'Singapore' },
  { value: 'Hong Kong', label: 'Hong Kong' },
  { value: 'Japan', label: 'Japan' },
  { value: 'Germany', label: 'Germany' },
  { value: 'France', label: 'France' },
  { value: 'Other', label: 'Other' },
];

const AU_STATE_OPTIONS = [
  { value: '', label: 'Select state...' },
  { value: 'NSW', label: 'New South Wales' },
  { value: 'VIC', label: 'Victoria' },
  { value: 'QLD', label: 'Queensland' },
  { value: 'WA', label: 'Western Australia' },
  { value: 'SA', label: 'South Australia' },
  { value: 'TAS', label: 'Tasmania' },
  { value: 'ACT', label: 'Australian Capital Territory' },
  { value: 'NT', label: 'Northern Territory' },
];

const CURRENCY_OPTIONS = [
  { value: 'AUD', label: 'Australian Dollar (AUD)' },
  { value: 'USD', label: 'US Dollar (USD)' },
  { value: 'EUR', label: 'Euro (EUR)' },
  { value: 'GBP', label: 'British Pound (GBP)' },
  { value: 'NZD', label: 'New Zealand Dollar (NZD)' },
  { value: 'CAD', label: 'Canadian Dollar (CAD)' },
  { value: 'JPY', label: 'Japanese Yen (JPY)' },
  { value: 'SGD', label: 'Singapore Dollar (SGD)' },
  { value: 'HKD', label: 'Hong Kong Dollar (HKD)' },
  { value: 'CHF', label: 'Swiss Franc (CHF)' },
];

const TIMEZONE_OPTIONS = [
  { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)' },
  { value: 'Australia/Melbourne', label: 'Melbourne (AEST/AEDT)' },
  { value: 'Australia/Brisbane', label: 'Brisbane (AEST)' },
  { value: 'Australia/Perth', label: 'Perth (AWST)' },
  { value: 'Australia/Adelaide', label: 'Adelaide (ACST/ACDT)' },
  { value: 'Australia/Darwin', label: 'Darwin (ACST)' },
  { value: 'Australia/Hobart', label: 'Hobart (AEST/AEDT)' },
  { value: 'Pacific/Auckland', label: 'Auckland (NZST/NZDT)' },
  { value: 'Asia/Singapore', label: 'Singapore (SGT)' },
  { value: 'Asia/Hong_Kong', label: 'Hong Kong (HKT)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
  { value: 'America/New_York', label: 'New York (EST/EDT)' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (PST/PDT)' },
  { value: 'UTC', label: 'UTC' },
];

export default function Settings() {
  const { user, checkAuth } = useAuth();

  // Profile form
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });
  const [profileErrors, setProfileErrors] = useState({});
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);

  // Password form
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    new_password2: '',
  });
  const [passwordErrors, setPasswordErrors] = useState({});
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Preferences form (includes DOB, address, currency, timezone)
  const [preferencesForm, setPreferencesForm] = useState({
    date_of_birth: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postcode: '',
    country: 'Australia',
    currency: 'AUD',
    timezone: 'Australia/Sydney',
  });
  const [preferencesSaving, setPreferencesSaving] = useState(false);
  const [preferencesSuccess, setPreferencesSuccess] = useState(false);

  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
      });
      if (user.preferences) {
        setPreferencesForm({
          date_of_birth: user.preferences.date_of_birth || '',
          address_line1: user.preferences.address_line1 || '',
          address_line2: user.preferences.address_line2 || '',
          city: user.preferences.city || '',
          state: user.preferences.state || '',
          postcode: user.preferences.postcode || '',
          country: user.preferences.country || 'Australia',
          currency: user.preferences.currency || 'AUD',
          timezone: user.preferences.timezone || 'Australia/Sydney',
        });
      }
    }
  }, [user]);

  const handleProfileChange = e => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
    setProfileErrors(prev => ({ ...prev, [name]: '' }));
    setProfileSuccess(false);
  };

  const handlePasswordChange = e => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({ ...prev, [name]: value }));
    setPasswordErrors(prev => ({ ...prev, [name]: '' }));
    setPasswordSuccess(false);
  };

  const handlePreferencesChange = e => {
    const { name, value } = e.target;
    setPreferencesForm(prev => ({ ...prev, [name]: value }));
    setPreferencesSuccess(false);
  };

  const handleProfileSubmit = async e => {
    e.preventDefault();
    setProfileSaving(true);
    setProfileErrors({});
    setProfileSuccess(false);

    try {
      await updateProfile(profileForm);
      await checkAuth();
      setProfileSuccess(true);
    } catch (err) {
      if (err.response?.data) {
        setProfileErrors(err.response.data);
      }
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordSubmit = async e => {
    e.preventDefault();
    setPasswordSaving(true);
    setPasswordErrors({});
    setPasswordSuccess(false);

    try {
      await changePassword(passwordForm);
      setPasswordSuccess(true);
      setPasswordForm({
        old_password: '',
        new_password: '',
        new_password2: '',
      });
    } catch (err) {
      if (err.response?.data) {
        setPasswordErrors(err.response.data);
      }
    } finally {
      setPasswordSaving(false);
    }
  };

  const handlePreferencesSubmit = async e => {
    e.preventDefault();
    setPreferencesSaving(true);
    setPreferencesSuccess(false);

    try {
      // Convert empty date_of_birth to null for the API
      const dataToSend = {
        ...preferencesForm,
        date_of_birth: preferencesForm.date_of_birth || null,
      };
      await updatePreferences(dataToSend);
      await checkAuth();
      setPreferencesSuccess(true);
    } catch (err) {
      console.error('Failed to update preferences:', err);
    } finally {
      setPreferencesSaving(false);
    }
  };

  return (
    <div className='p-8'>
      <div className='mb-8'>
        <h1 className='text-3xl font-bold text-gray-900'>Account Settings</h1>
        <p className='text-gray-500 mt-1'>
          Manage your account and preferences
        </p>
      </div>

      <div className='max-w-2xl space-y-6'>
        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <div className='flex items-center gap-3'>
              <div className='bg-blue-100 p-2 rounded-lg'>
                <User className='text-blue-600' size={20} />
              </div>
              <div>
                <h2 className='font-semibold text-gray-900'>
                  Profile Information
                </h2>
                <p className='text-sm text-gray-500'>
                  Update your name and email
                </p>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleProfileSubmit} className='space-y-4'>
              <div className='grid grid-cols-2 gap-4'>
                <Input
                  label='First Name'
                  name='first_name'
                  value={profileForm.first_name}
                  onChange={handleProfileChange}
                  error={profileErrors.first_name}
                />
                <Input
                  label='Last Name'
                  name='last_name'
                  value={profileForm.last_name}
                  onChange={handleProfileChange}
                  error={profileErrors.last_name}
                />
              </div>
              <Input
                label='Email'
                name='email'
                type='email'
                value={profileForm.email}
                onChange={handleProfileChange}
                error={profileErrors.email}
              />
              <div className='flex items-center gap-4'>
                <Button type='submit' disabled={profileSaving}>
                  {profileSaving ? 'Saving...' : 'Save Changes'}
                </Button>
                {profileSuccess && (
                  <span className='flex items-center gap-1 text-green-600 text-sm'>
                    <Check size={16} />
                    Profile updated
                  </span>
                )}
              </div>
            </form>
          </CardBody>
        </Card>

        {/* Password Settings */}
        <Card>
          <CardHeader>
            <div className='flex items-center gap-3'>
              <div className='bg-amber-100 p-2 rounded-lg'>
                <Lock className='text-amber-600' size={20} />
              </div>
              <div>
                <h2 className='font-semibold text-gray-900'>Change Password</h2>
                <p className='text-sm text-gray-500'>Update your password</p>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            <form onSubmit={handlePasswordSubmit} className='space-y-4'>
              <Input
                label='Current Password'
                name='old_password'
                type='password'
                value={passwordForm.old_password}
                onChange={handlePasswordChange}
                error={passwordErrors.old_password}
              />
              <Input
                label='New Password'
                name='new_password'
                type='password'
                value={passwordForm.new_password}
                onChange={handlePasswordChange}
                error={passwordErrors.new_password}
              />
              <Input
                label='Confirm New Password'
                name='new_password2'
                type='password'
                value={passwordForm.new_password2}
                onChange={handlePasswordChange}
                error={passwordErrors.new_password2}
              />
              <div className='flex items-center gap-4'>
                <Button type='submit' disabled={passwordSaving}>
                  {passwordSaving ? 'Changing...' : 'Change Password'}
                </Button>
                {passwordSuccess && (
                  <span className='flex items-center gap-1 text-green-600 text-sm'>
                    <Check size={16} />
                    Password changed
                  </span>
                )}
              </div>
            </form>
          </CardBody>
        </Card>

        {/* Personal Details */}
        <Card>
          <CardHeader>
            <div className='flex items-center gap-3'>
              <div className='bg-purple-100 p-2 rounded-lg'>
                <MapPin className='text-purple-600' size={20} />
              </div>
              <div>
                <h2 className='font-semibold text-gray-900'>
                  Personal Details
                </h2>
                <p className='text-sm text-gray-500'>
                  Date of birth and address
                </p>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            <form onSubmit={handlePreferencesSubmit} className='space-y-4'>
              <Input
                label='Date of Birth'
                name='date_of_birth'
                type='date'
                value={preferencesForm.date_of_birth}
                onChange={handlePreferencesChange}
              />

              <div className='border-t pt-4 mt-4'>
                <p className='text-sm font-medium text-gray-700 mb-3'>
                  Address
                </p>
                <div className='space-y-4'>
                  <Input
                    label='Address Line 1'
                    name='address_line1'
                    value={preferencesForm.address_line1}
                    onChange={handlePreferencesChange}
                    placeholder='Street address'
                  />
                  <Input
                    label='Address Line 2'
                    name='address_line2'
                    value={preferencesForm.address_line2}
                    onChange={handlePreferencesChange}
                    placeholder='Apartment, suite, unit, etc. (optional)'
                  />
                  <div className='grid grid-cols-2 gap-4'>
                    <Input
                      label='City / Suburb'
                      name='city'
                      value={preferencesForm.city}
                      onChange={handlePreferencesChange}
                    />
                    {preferencesForm.country === 'Australia' ? (
                      <Select
                        label='State'
                        name='state'
                        value={preferencesForm.state}
                        onChange={handlePreferencesChange}
                        options={AU_STATE_OPTIONS}
                      />
                    ) : (
                      <Input
                        label='State / Province'
                        name='state'
                        value={preferencesForm.state}
                        onChange={handlePreferencesChange}
                      />
                    )}
                  </div>
                  <div className='grid grid-cols-2 gap-4'>
                    <Input
                      label='Postcode'
                      name='postcode'
                      value={preferencesForm.postcode}
                      onChange={handlePreferencesChange}
                    />
                    <Select
                      label='Country'
                      name='country'
                      value={preferencesForm.country}
                      onChange={handlePreferencesChange}
                      options={COUNTRY_OPTIONS}
                    />
                  </div>
                </div>
              </div>

              <div className='flex items-center gap-4 pt-2'>
                <Button type='submit' disabled={preferencesSaving}>
                  {preferencesSaving ? 'Saving...' : 'Save Details'}
                </Button>
                {preferencesSuccess && (
                  <span className='flex items-center gap-1 text-green-600 text-sm'>
                    <Check size={16} />
                    Details saved
                  </span>
                )}
              </div>
            </form>
          </CardBody>
        </Card>

        {/* Preferences Settings */}
        <Card>
          <CardHeader>
            <div className='flex items-center gap-3'>
              <div className='bg-green-100 p-2 rounded-lg'>
                <Globe className='text-green-600' size={20} />
              </div>
              <div>
                <h2 className='font-semibold text-gray-900'>Preferences</h2>
                <p className='text-sm text-gray-500'>
                  Set your currency and timezone
                </p>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            <form onSubmit={handlePreferencesSubmit} className='space-y-4'>
              <Select
                label='Currency'
                name='currency'
                value={preferencesForm.currency}
                onChange={handlePreferencesChange}
                options={CURRENCY_OPTIONS}
              />
              <Select
                label='Timezone'
                name='timezone'
                value={preferencesForm.timezone}
                onChange={handlePreferencesChange}
                options={TIMEZONE_OPTIONS}
              />
              <div className='flex items-center gap-4'>
                <Button type='submit' disabled={preferencesSaving}>
                  {preferencesSaving ? 'Saving...' : 'Save Preferences'}
                </Button>
                {preferencesSuccess && (
                  <span className='flex items-center gap-1 text-green-600 text-sm'>
                    <Check size={16} />
                    Preferences saved
                  </span>
                )}
              </div>
            </form>
          </CardBody>
        </Card>

        {/* Account Info */}
        <Card>
          <CardHeader>
            <div className='flex items-center gap-3'>
              <div className='bg-gray-100 p-2 rounded-lg'>
                <SettingsIcon className='text-gray-600' size={20} />
              </div>
              <div>
                <h2 className='font-semibold text-gray-900'>
                  Account Information
                </h2>
                <p className='text-sm text-gray-500'>Your account details</p>
              </div>
            </div>
          </CardHeader>
          <CardBody>
            <div className='space-y-3 text-sm'>
              <div className='flex justify-between py-2 border-b border-gray-100'>
                <span className='text-gray-500'>Username</span>
                <span className='font-medium text-gray-900'>
                  {user?.username}
                </span>
              </div>
              <div className='flex justify-between py-2 border-b border-gray-100'>
                <span className='text-gray-500'>Email</span>
                <span className='font-medium text-gray-900'>{user?.email}</span>
              </div>
              <div className='flex justify-between py-2'>
                <span className='text-gray-500'>Account ID</span>
                <span className='font-medium text-gray-900'>#{user?.id}</span>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
