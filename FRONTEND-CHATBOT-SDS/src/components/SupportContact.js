import React, { useEffect, useRef, useState } from 'react';
import { LifeBuoy, Mail, User, MessageSquare, Phone, Github } from 'lucide-react';
import config from '../config';
import './SupportContact.css';

function SupportContact() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const formRef = useRef(null);
  const nameInputRef = useRef(null);

  const formspreeEndpoint = (() => {
    const value = (config.FORMSPREE_FORM_ENDPOINT || '').trim();
    if (!value) return '';
    if (value.includes('YOUR_FORM_ID')) return '';
    return value;
  })();

  useEffect(() => {
    const onOpen = () => setOpen(true);
    window.addEventListener('support:open', onOpen);
    return () => window.removeEventListener('support:open', onOpen);
  }, []);

  useEffect(() => {
    if (!open) return undefined;

    const onKeyDown = (e) => {
      if (e.key === 'Escape') setOpen(false);
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    setStatus('idle');
    setError('');
    setTimeout(() => nameInputRef.current?.focus(), 0);
  }, [open]);

  const close = () => setOpen(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formspreeEndpoint) {
      setStatus('error');
      setError('Support form is not configured yet. Please add your Formspree endpoint.');
      return;
    }

    const formEl = formRef.current;
    if (!formEl) return;

    setStatus('sending');
    try {
      const response = await fetch(formspreeEndpoint, {
        method: 'POST',
        body: new FormData(formEl),
        headers: { Accept: 'application/json' },
      });

      if (!response.ok) {
        let message = 'Failed to send message. Please try again.';
        try {
          const data = await response.json();
          if (data?.errors?.length) message = data.errors.map((x) => x.message).join(', ');
        } catch (err) {
        }
        throw new Error(message);
      }

      formEl.reset();
      setStatus('success');
    } catch (err) {
      setStatus('error');
      setError(err?.message || 'Failed to send message. Please try again.');
    }
  };

  return (
    <>
      <button
        type="button"
        className="support-fab"
        onClick={() => setOpen(true)}
        aria-label="Open support contact form"
      >
        <LifeBuoy size={18} />
        <span>Support</span>
      </button>

      {open && (
        <div className="support-overlay" onClick={close} role="dialog" aria-modal="true">
          <div className="support-modal" onClick={(e) => e.stopPropagation()}>
            <div className="support-modal-header">
              <div className="support-modal-title">
                <LifeBuoy size={18} />
                <h2>Contact Support</h2>
              </div>
              <button type="button" className="support-close" onClick={close} aria-label="Close">
                ×
              </button>
            </div>

            <div className="support-modal-body">
              <div className="support-info">
                <h3>Get in touch</h3>
                <p>Send us your query and we’ll get back to you.</p>
                <div className="support-contact-list">
                  <a className="support-contact-item" href="mailto:ameenramali@hotmail.com">
                    <Mail size={16} />
                    <span>ameenramali@hotmail.com</span>
                  </a>
                  <a className="support-contact-item" href="tel:+918652492068">
                    <Phone size={16} />
                    <span>+91-8652492068</span>
                  </a>
                  <a
                    className="support-contact-item"
                    href="https://github.com/100TAlaRic99"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Github size={16} />
                    <span>github.com/100TAlaRic99</span>
                  </a>
                  <div className="support-contact-item">
                    <User size={16} />
                    <span>Facebook: Ameen Ramali</span>
                  </div>
                </div>
                <div className="support-hints">
                  <div className="support-hint">
                    <Mail size={16} />
                    <span>We reply via email</span>
                  </div>
                  <div className="support-hint">
                    <MessageSquare size={16} />
                    <span>Share details for faster help</span>
                  </div>
                </div>
              </div>

              <form ref={formRef} className="support-form" onSubmit={handleSubmit}>
                <div className="support-field">
                  <label htmlFor="support_name">
                    <User size={16} />
                    Your Name
                  </label>
                  <input
                    ref={nameInputRef}
                    id="support_name"
                    name="name"
                    type="text"
                    placeholder="Your name"
                    required
                    disabled={status === 'sending'}
                  />
                </div>

                <div className="support-field">
                  <label htmlFor="support_email">
                    <Mail size={16} />
                    Email
                  </label>
                  <input
                    id="support_email"
                    name="email"
                    type="email"
                    placeholder="you@example.com"
                    required
                    disabled={status === 'sending'}
                  />
                  <p className="support-description">
                    This will help us respond to your query via an email.
                  </p>
                </div>

                <div className="support-field">
                  <label htmlFor="support_message">
                    <MessageSquare size={16} />
                    Message
                  </label>
                  <textarea
                    id="support_message"
                    name="message"
                    rows="5"
                    placeholder="Your message"
                    required
                    disabled={status === 'sending'}
                  />
                  <p className="support-description">What would you like to discuss?</p>
                </div>

                {(status === 'success' || status === 'error') && (
                  <div className={`support-status ${status}`}>
                    {status === 'success'
                      ? 'Message sent successfully.'
                      : error || 'Failed to send message.'}
                  </div>
                )}

                <button
                  type="submit"
                  className="support-submit"
                  disabled={status === 'sending' || !formspreeEndpoint}
                >
                  {status === 'sending' ? 'Sending...' : 'Send Message'}
                </button>

                {!formspreeEndpoint && (
                  <div className="support-config-note">
                    Set REACT_APP_FORMSPREE_FORM_ENDPOINT in your frontend env to enable sending.
                  </div>
                )}
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default SupportContact;
