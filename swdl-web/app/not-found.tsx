import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="text-center py-16 px-4">
        <div className="text-8xl mb-6">🌍</div>
        <h1 className="font-display text-4xl font-bold text-navy mb-4">404</h1>
        <p className="text-slate text-lg mb-8">
          A página que você procura não existe ou foi movida.
          <br />
          The page you are looking for does not exist or was moved.
        </p>
        <Link
          href="/pt-BR"
          className="inline-flex items-center px-6 py-3 bg-navy text-white rounded-sm font-medium hover:bg-navy-light transition-colors no-underline"
        >
          Voltar — Back
        </Link>
      </div>
    </div>
  );
}
