import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="text-center py-16 px-4">
        <p className="font-mono text-[0.7rem] tracking-[0.3em] uppercase text-[#C9A84C] mb-4">Error 404</p>
        <h1 className="font-display text-7xl md:text-8xl font-bold text-navy leading-none mb-6">404</h1>
        <div className="w-12 h-px bg-[#C9A84C] mx-auto mb-6" />
        <p className="text-slate text-lg mb-10">
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
