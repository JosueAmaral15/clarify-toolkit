'use client';

import React, { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Mail, Send, User, MessageSquare } from 'lucide-react';
import { useTranslation } from '@/lib/i18n/context';

export default function contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const {t} = useTranslation();
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://pteasy-backend-test-26c90e3f6e3a.herokuapp.com';
      // Remove trailing /api if present to avoid double /api
      const apiUrl = baseUrl.replace(/\/api\/?$/, '');

      const response = await fetch(`${apiUrl}/api/contact/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok && data.ok) {
        setSubmitStatus('success');

        // Reset form after 3 seconds
        setTimeout(() => {
          setFormData({ name: '', email: '', subject: '', message: '' });
          setSubmitStatus('idle');
        }, 3000);
      } else {
        console.error('Failed to send message:', data.error);
        setSubmitStatus('error');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-4">
              <Mail size={32} />
            </div>
            <h1 className="text-4xl font-bold mb-4">{t.pages.contact.hero.title}</h1>
            <p className="text-xl text-blue-100">
              {t.pages.contact.hero.haveAQuestionOrNeedHelp}
            </p>
          </div>
        </div>
      </div>

      {/* Contact Info Cards */}
      <div className="container mx-auto px-4 -mt-8">
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-lg p-6 flex items-start gap-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Mail className="text-blue-600" size={24} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">{t.pages.contact.info.email}</h3>
              <p className="text-gray-600">support@pteasy.com.au</p>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6 flex items-start gap-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <MessageSquare className="text-green-600" size={24} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">{t.pages.contact.responseTime}</h3>
              <p className="text-gray-600">{t.pages.contact.within24Hours}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Form */}
      <div className="container mx-auto px-4 pb-16">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">{t.pages.contact.sendUsAMessage}</h2>

          {submitStatus === 'success' && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
              {t.pages.contact.thankYouForContactingUs}
            </div>
          )}

          {submitStatus === 'error' && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              {t.pages.contact.failedToSendYourMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <User size={16} />
                {t.pages.contact.form.labels.name}
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder={t.pages.contact.form.placeholders.yourFullName}
                required
                disabled={isSubmitting}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="email" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Mail size={16} />
                {t.pages.contact.form.labels.emailFill}
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
                required
                disabled={isSubmitting}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="subject" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <MessageSquare size={16} />
                {t.pages.contact.form.labels.subject}
              </label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                placeholder={t.pages.contact.form.placeholders.whatIsThisAbout}
                required
                disabled={isSubmitting}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="message" className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <MessageSquare size={16} />
                {t.pages.contact.form.labels.message}
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                placeholder={t.pages.contact.form.placeholders.tellUsHowWeCanHelpYou}
                rows={6}
                required
                disabled={isSubmitting}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>

            <div className="flex items-center justify-between pt-4">
              <p className="text-sm text-gray-500">{t.pages.contact.form.labels.requiredFields}</p>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isSubmitting ? (
                  <>{t.pages.contact.form.buttons.sending}</>
                ) : (
                  <>
                    <Send size={20} />
                    {t.pages.contact.form.buttons.send}
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              {t.pages.contact.lookingForQuickAnswers} <a href="/faq" className="text-blue-600 hover:text-blue-700 font-medium">{t.pages.contact.faqPage}</a>
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
