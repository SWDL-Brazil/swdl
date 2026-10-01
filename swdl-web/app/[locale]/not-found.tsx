import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { NotFoundContent } from '@/components/ui/NotFoundContent';

export default async function LocaleNotFound() {
  try {
    const messages = await getMessages();
    return (
      <NextIntlClientProvider messages={messages}>
        <NotFoundContent />
      </NextIntlClientProvider>
    );
  } catch {
    return <NotFoundContent />;
  }
}
