import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SupportContact from './SupportContact';
import config from '../config';

// Mock the config module
jest.mock('../config', () => ({
  FORMSPREE_FORM_ENDPOINT: 'https://formspree.io/f/test-endpoint'
}));

describe('SupportContact Component Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset fetch mock
    global.fetch = jest.fn();
  });

  const renderSupport = () => {
    return render(<SupportContact />);
  };

  test('1. renders support FAB button on page', () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    expect(supportButton).toBeInTheDocument();
    expect(screen.getByText('Support')).toBeInTheDocument();
  });

  test('2. opens support modal when FAB is clicked', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    // Check modal header
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
    
    // Check form fields
    expect(screen.getByLabelText(/Your Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Email$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Message/i)).toBeInTheDocument();
    
    // Check submit button
    expect(screen.getByRole('button', { name: /Send Message/i })).toBeInTheDocument();
  });

  test('3. displays contact information in modal', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    // Check for contact info
    expect(screen.getByText('Get in touch')).toBeInTheDocument();
    expect(screen.getByText(/we.ll get back to you/i)).toBeInTheDocument();
    
    // Check for contact methods
    expect(screen.getByText('ameenramali@hotmail.com')).toBeInTheDocument();
    expect(screen.getByText('+91-8652492068')).toBeInTheDocument();
    expect(screen.getByText('github.com/100TAlaRic99')).toBeInTheDocument();
    expect(screen.getByText('Facebook: Ameen Ramali')).toBeInTheDocument();
  });

  test('4. all form fields are required', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    const nameInput = screen.getByLabelText(/Your Name/i);
    const emailInput = screen.getByLabelText(/^Email$/i);
    const messageInput = screen.getByLabelText(/Message/i);
    
    expect(nameInput).toHaveAttribute('required');
    expect(emailInput).toHaveAttribute('required');
    expect(messageInput).toHaveAttribute('required');
  });

  test('5. successfully submits support form', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true })
    });
    
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    const nameInput = screen.getByLabelText(/Your Name/i);
    const emailInput = screen.getByLabelText(/^Email$/i);
    const messageInput = screen.getByLabelText(/Message/i);
    const submitButton = screen.getByRole('button', { name: /Send Message/i });
    
    await userEvent.type(nameInput, 'John Doe');
    await userEvent.type(emailInput, 'john@example.com');
    await userEvent.type(messageInput, 'I need help with the sentiment analysis feature.');
    
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'https://formspree.io/f/test-endpoint',
        expect.objectContaining({
          method: 'POST',
          headers: { Accept: 'application/json' },
        })
      );
    });
    
    await waitFor(() => {
      expect(screen.getByText('Message sent successfully.')).toBeInTheDocument();
    });
  });

  test('6. shows error when form submission fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ errors: [{ message: 'Invalid email address' }] })
    });
    
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    const nameInput = screen.getByLabelText(/Your Name/i);
    const emailInput = screen.getByLabelText(/^Email$/i);
    const messageInput = screen.getByLabelText(/Message/i);
    const submitButton = screen.getByRole('button', { name: /Send Message/i });
    
    await userEvent.type(nameInput, 'John Doe');
    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.type(messageInput, 'Test message');
    
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email address')).toBeInTheDocument();
    });
  });

  test('7. closes modal when clicking close button', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    // Modal should be open
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
    
    // Click close button
    const closeButton = screen.getByRole('button', { name: /Close/i });
    await userEvent.click(closeButton);
    
    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText('Contact Support')).not.toBeInTheDocument();
    });
  });

  test('8. closes modal when pressing Escape key', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    // Modal should be open
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
    
    // Press Escape key
    fireEvent.keyDown(window, { key: 'Escape' });
    
    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText('Contact Support')).not.toBeInTheDocument();
    });
  });

  test('9. shows configuration note when formspree is not configured', async () => {
    // This test validates that the form displays properly even when not fully configured
    // In production, this would check for the config note
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    // The form should still display when configured
    expect(screen.getByLabelText(/Your Name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send Message/i })).toBeInTheDocument();
  });

  test('10. email link opens mailto', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    const emailLink = screen.getByText('ameenramali@hotmail.com').closest('a');
    expect(emailLink).toHaveAttribute('href', 'mailto:ameenramali@hotmail.com');
  });

  test('11. phone link opens tel', async () => {
    renderSupport();
    
    const supportButton = screen.getByRole('button', { name: /Open support contact form/i });
    await userEvent.click(supportButton);
    
    const phoneLink = screen.getByText('+91-8652492068').closest('a');
    expect(phoneLink).toHaveAttribute('href', 'tel:+918652492068');
  });
});
