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

test('shows mismatch error when passwords differ', async () => {
  renderWithRouter(<Register onRegister={jest.fn()} />);

  await userEvent.type(screen.getByLabelText(/username/i), 'alice');
  await userEvent.type(screen.getByLabelText(/^email/i), 'a@example.com');
  await userEvent.type(screen.getByLabelText(/^password$/i), 'pw1');
  await userEvent.type(screen.getByLabelText(/confirm password/i), 'pw2');

  await userEvent.click(screen.getByRole('button', { name: /register/i }));
  expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

test('submits registration and calls onRegister', async () => {
  api.post.mockResolvedValueOnce({
    data: { access_token: 't1', user: { id: 'u1', username: 'alice', email: 'a@example.com' } },
  });

  const onRegister = jest.fn();
  renderWithRouter(<Register onRegister={onRegister} />);

  await userEvent.type(screen.getByLabelText(/username/i), 'alice');
  await userEvent.type(screen.getByLabelText(/^email/i), 'a@example.com');
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

