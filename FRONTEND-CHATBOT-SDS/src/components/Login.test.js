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

test('renders login form fields', () => {
  renderWithRouter(<Login onLogin={jest.fn()} />);
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});

test('submits credentials and calls onLogin', async () => {
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

test('shows error message on failure', async () => {
  api.post.mockRejectedValueOnce({
    response: { data: { error: 'Invalid credentials' } },
  });

  renderWithRouter(<Login onLogin={jest.fn()} />);

  await userEvent.type(screen.getByLabelText(/email/i), 'a@example.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'pw');
  await userEvent.click(screen.getByRole('button', { name: /login/i }));

  expect(await screen.findByText(/invalid credentials/i)).toBeInTheDocument();
});

