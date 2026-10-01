import { Metadata } from 'next';
import { Suspense } from 'react';
import { getTranslations } from 'next-intl/server';
import { CertificadoContent } from '@/components/certificado/CertificadoContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('meta');
    return {
      title: t('certificado_title'),
      description: t('certificado_desc'),
    };
  } catch {
    return {
      title: 'Verificar Certificado — SWDL',
      description:
        'Consulte a autenticidade de um certificado de participação da SWDL pelo código de verificação.',
    };
  }
}

export default function CertificadoPage() {
  return (
    <Suspense fallback={<div className="pt-[68px] min-h-[50vh]" />}>
      <CertificadoContent />
    </Suspense>
  );
}
