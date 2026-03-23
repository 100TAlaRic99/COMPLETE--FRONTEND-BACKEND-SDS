import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';

jest.mock('../api/axios', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
  },
}));

import api from '../api/axios';

function renderWithRouter(ui) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('Login Component Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('1. renders login form with all fields and elements', () => {
    renderWithRouter(<Login onLogin={jest.fn()} />);
    
    // Check for header elements
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    expect(screen.getByText('Login to analyze sentiments')).toBeInTheDocument();
    
    // Check for form fields
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    
    // Check for login button
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    
    // Check for register link
    expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument();
    expect(screen.getByText(/Register here/i)).toBeInTheDocument();
    
    // Check for support link
    expect(screen.getByRole('button', { name: /Support/i })).toBeInTheDocument();
  });

  test('2. email and password fields are required', () => {
    renderWithRouter(<Login onLogin={jest.fn()} />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    expect(emailInput).toHaveAttribute('required');
    expect(passwordInput).toHaveAttribute('required');
  });

  test('3. successfully logs in with valid credentials', async () => {
    api.post.mockResolvedValueOnce({
      data: { access_token: 't1', user: { id: 'u1', username: 'alice', email: 'a@example.com' } },
    });

    const onLogin = jest.fn();
    renderWithRouter(<Login onLogin={onLogin} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'pw');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith('/api/login', { email: 'a@example.com', password: 'pw' });
    expect(onLogin).toHaveBeenCalledWith('t1', { id: 'u1', username: 'alice', email: 'a@example.com' });
  });

  test('4. shows error message on failed login', async () => {
    api.post.mockRejectedValueOnce({
      response: { data: { error: 'Invalid credentials' } },
    });

    renderWithRouter(<Login onLogin={jest.fn()} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'pw');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));

    expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
  });

  test('5. toggles password visibility when clicking eye icon', async () => {
    renderWithRouter(<Login onLogin={jest.fn()} />);
    
    const passwordInput = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole('button', { name: '' });
    
    // Password should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click to show password
    await userEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click again to hide password
    await userEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('6. shows loading state while submitting', async () => {
    api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderWithRouter(<Login onLogin={jest.fn()} />);

    await userEvent.type(screen.getByLabelText(/email/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'pw');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText('Logging in...')).toBeInTheDocument();
    });
  });
});

