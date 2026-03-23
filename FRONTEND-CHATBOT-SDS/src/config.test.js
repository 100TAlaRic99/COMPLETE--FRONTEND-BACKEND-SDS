describe('config', () => {
  afterEach(() => {
    delete process.env.REACT_APP_API_URL;
    delete process.env.REACT_APP_FORMSPREE_FORM_ENDPOINT;
    jest.resetModules();
  });

  test('uses env vars when set', async () => {
    process.env.REACT_APP_API_URL = 'http://example.test';
    process.env.REACT_APP_FORMSPREE_FORM_ENDPOINT = 'https://formspree.test';
    const module = await import('./config');
    expect(module.default.API_BASE_URL).toBe('http://example.test');
    expect(module.default.FORMSPREE_FORM_ENDPOINT).toBe('https://formspree.test');
  });

  test('falls back to defaults when env vars missing', async () => {
    const module = await import('./config');
    expect(module.default.API_BASE_URL).toBe('http://localhost:5000');
    expect(module.default.FORMSPREE_FORM_ENDPOINT).toBe('');
  });
});

