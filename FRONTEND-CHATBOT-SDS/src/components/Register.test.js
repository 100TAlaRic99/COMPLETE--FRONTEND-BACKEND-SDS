import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Register from './Register';

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

describe('Register Component Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('1. renders register form with all fields and elements', () => {
    renderWithRouter(<Register onRegister={jest.fn()} />);
    
    // Check for header elements
    expect(screen.getByText('Create Account')).toBeInTheDocument();
    expect(screen.getByText('Join us to start analyzing sentiments')).toBeInTheDocument();
    
    // Check for form fields
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    
    // Check for register button
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
    
    // Check for login link
    expect(screen.getByText(/Already have an account/i)).toBeInTheDocument();
    expect(screen.getByText(/Login here/i)).toBeInTheDocument();
    
    // Check for support link
    expect(screen.getByRole('button', { name: /Support/i })).toBeInTheDocument();
  });

  test('2. all form fields are required', () => {
    renderWithRouter(<Register onRegister={jest.fn()} />);
    
    const usernameInput = screen.getByLabelText(/username/i);
    const emailInput = screen.getByLabelText(/^email$/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    
    expect(usernameInput).toHaveAttribute('required');
    expect(emailInput).toHaveAttribute('required');
    expect(passwordInput).toHaveAttribute('required');
    expect(confirmPasswordInput).toHaveAttribute('required');
  });

  test('3. shows mismatch error when passwords differ', async () => {
    renderWithRouter(<Register onRegister={jest.fn()} />);

    await userEvent.type(screen.getByLabelText(/username/i), 'alice');
    await userEvent.type(screen.getByLabelText(/^email$/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pw1');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'pw2');

    await userEvent.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  test('4. successfully registers with valid credentials', async () => {
    api.post.mockResolvedValueOnce({
      data: { access_token: 't1', user: { id: 'u1', username: 'alice', email: 'a@example.com' } },
    });

    const onRegister = jest.fn();
    renderWithRouter(<Register onRegister={onRegister} />);

    await userEvent.type(screen.getByLabelText(/username/i), 'alice');
    await userEvent.type(screen.getByLabelText(/^email$/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pw');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'pw');

    await userEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => expect(api.post).toHaveBeenCalledTimes(1));
    expect(api.post).toHaveBeenCalledWith('/api/register', {
      username: 'alice',
      email: 'a@example.com',
      password: 'pw',
    });
    expect(onRegister).toHaveBeenCalledWith('t1', { id: 'u1', username: 'alice', email: 'a@example.com' });
  });

  test('5. toggles password and confirm password visibility', async () => {
    renderWithRouter(<Register onRegister={jest.fn()} />);
    
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const toggleButtons = screen.getAllByRole('button', { name: '' });
    
    // Passwords should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    
    // Toggle password visibility
    await userEvent.click(toggleButtons[0]);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Toggle confirm password visibility
    await userEvent.click(toggleButtons[1]);
    expect(confirmPasswordInput).toHaveAttribute('type', 'text');
    
    // Toggle back
    await userEvent.click(toggleButtons[0]);
    await userEvent.click(toggleButtons[1]);
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
  });

  test('6. displays error message on registration failure', async () => {
    api.post.mockRejectedValueOnce({
      response: { data: { error: 'Email already exists' } },
    });

    renderWithRouter(<Register onRegister={jest.fn()} />);

    await userEvent.type(screen.getByLabelText(/username/i), 'alice');
    await userEvent.type(screen.getByLabelText(/^email$/i), 'existing@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pw');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'pw');
    await userEvent.click(screen.getByRole('button', { name: /register/i }));

    expect(await screen.findByText(/Email already exists/i)).toBeInTheDocument();
  });

  test('7. shows loading state while submitting', async () => {
    api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderWithRouter(<Register onRegister={jest.fn()} />);

    await userEvent.type(screen.getByLabelText(/username/i), 'alice');
    await userEvent.type(screen.getByLabelText(/^email$/i), 'a@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pw');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'pw');
    await userEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText('Creating account...')).toBeInTheDocument();
    });
  });
});

