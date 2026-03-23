import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chat from './Chat';

jest.mock('../api/axios', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
    delete: jest.fn(),
  },
}));

import api from '../api/axios';

const mockUser = { username: 'testuser', email: 'test@example.com' };
const mockOnLogout = jest.fn();

// Mock window event dispatching
const mockDispatchEvent = jest.spyOn(window, 'dispatchEvent');

describe('Chat Component Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderChat = () => {
    return render(<Chat user={mockUser} onLogout={mockOnLogout} />);
  };

   const getSendButton = () => {
     const form = screen.getByPlaceholderText('Type your message here...').closest('form');
     return within(form).getByRole('button');
   };

  test('1. renders chat page with all elements', () => {
    renderChat();
    
    // Check app header
    expect(screen.getByText('Semantic Detection System')).toBeInTheDocument();
    
    // Check chat header
    expect(screen.getByText('Analyze the sentiment of your text')).toBeInTheDocument();
    
    // Check for user info
    expect(screen.getByText('testuser')).toBeInTheDocument();
    
    // Check for buttons using title attributes
    expect(screen.getByTitle(/View History/i)).toBeInTheDocument();
    expect(screen.getByTitle(/Support/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument();
    
    // Check for empty state
    expect(screen.getByText('Start a conversation by typing a message below!')).toBeInTheDocument();
    
    // Check for analyzer selector
    expect(screen.getByRole('combobox')).toBeInTheDocument();
    
    // Check for input and send button
    expect(screen.getByPlaceholderText('Type your message here...')).toBeInTheDocument();
    expect(getSendButton()).toBeInTheDocument();
  });

  test('2. can select different analyzers', async () => {
    renderChat();
    
    const select = screen.getByRole('combobox');
    
    // Check default value
    expect(select).toHaveValue('hybrid');
    
    // Change to VADER
    await userEvent.selectOptions(select, 'vader');
    expect(select).toHaveValue('vader');
    
    // Change to LLM
    await userEvent.selectOptions(select, 'llm');
    expect(select).toHaveValue('llm');
  });

  test('3. sends message and displays user message in chat', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        text: 'This is a great movie!',
        sentiment: {
          label: 'Positive',
          emoji: '😊',
          scores: { pos: 0.8, neu: 0.15, neg: 0.05 },
          compound: 0.75,
          analyzer: 'hybrid'
        }
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'This is a great movie!');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getAllByText('This is a great movie!').length).toBeGreaterThanOrEqual(1);
    });
  });

  test('4. calls logout when logout button is clicked', () => {
    renderChat();
    
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    
    expect(mockOnLogout).toHaveBeenCalled();
  });

  test('5. dispatches support event when support button is clicked', () => {
    renderChat();
    
    const supportButton = screen.getByTitle(/Support/i);
    fireEvent.click(supportButton);
    
    expect(mockDispatchEvent).toHaveBeenCalledWith(expect.any(Event));
  });

  test('6. SENTIMENT ANALYSIS - POSITIVE movie review: detects positive sentiment', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        text: 'This movie was absolutely fantastic! The acting was superb and the story was captivating.',
        sentiment: {
          label: 'Positive',
          emoji: '😊',
          scores: { pos: 0.85, neu: 0.10, neg: 0.05 },
          compound: 0.82,
          analyzer: 'hybrid'
        }
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'This movie was absolutely fantastic! The acting was superb and the story was captivating.');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Positive')).toBeInTheDocument();
      expect(screen.getByText('😊')).toBeInTheDocument();
    });
  });

  test('7. SENTIMENT ANALYSIS - NEGATIVE movie review: detects negative sentiment', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        text: 'This movie was terrible. The plot was boring and the acting was awful. I want my money back!',
        sentiment: {
          label: 'Negative',
          emoji: '😞',
          scores: { pos: 0.05, neu: 0.15, neg: 0.80 },
          compound: -0.75,
          analyzer: 'hybrid'
        }
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'This movie was terrible. The plot was boring and the acting was awful. I want my money back!');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Negative')).toBeInTheDocument();
      expect(screen.getByText('😞')).toBeInTheDocument();
    });
  });

  test('8. SENTIMENT ANALYSIS - NEUTRAL movie review: detects neutral sentiment', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        text: 'The movie was okay. It had some good moments and some bad moments.',
        sentiment: {
          label: 'Neutral',
          emoji: '😐',
          scores: { pos: 0.25, neu: 0.60, neg: 0.15 },
          compound: 0.10,
          analyzer: 'hybrid'
        }
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'The movie was okay. It had some good moments and some bad moments.');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Neutral')).toBeInTheDocument();
      expect(screen.getByText('😐')).toBeInTheDocument();
    });
  });

  test('9. displays sentiment scores correctly', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        text: 'Amazing film!',
        sentiment: {
          label: 'Positive',
          emoji: '😊',
          scores: { pos: 0.85, neu: 0.10, neg: 0.05 },
          compound: 0.82,
          analyzer: 'hybrid'
        }
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'Amazing film!');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Positive:')).toBeInTheDocument();
      expect(screen.getByText('85.0%')).toBeInTheDocument();
      expect(screen.getByText('Neutral:')).toBeInTheDocument();
      expect(screen.getByText('10.0%')).toBeInTheDocument();
      expect(screen.getByText('Negative:')).toBeInTheDocument();
      expect(screen.getByText('5.0%')).toBeInTheDocument();
    });
  });

  test('10. shows loading state while analyzing sentiment', async () => {
    api.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 200)));
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'Test message');
    fireEvent.click(sendButton);
    
    // Button should be disabled during loading
    await waitFor(() => {
      expect(sendButton).toBeDisabled();
    });
  });

  test('11. displays error message on API failure', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        data: { error: 'Failed to analyze sentiment' },
        status: 500
      }
    });
    
    renderChat();
    
    const input = screen.getByPlaceholderText('Type your message here...');
    const sendButton = getSendButton();
    
    await userEvent.type(input, 'Test message');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to analyze sentiment')).toBeInTheDocument();
    });
  });
});
