import { Hero } from '@/components/home/Hero';
import { InscricoesCountdown } from '@/components/home/InscricoesCountdown';
import { Stats } from '@/components/home/Stats';
import { NewsGrid } from '@/components/home/NewsGrid';
import { CommitteesPreview } from '@/components/home/CommitteesPreview';
import { AgendaStrip } from '@/components/home/AgendaStrip';
import { Testimonials } from '@/components/home/Testimonials';
import { StaggeredGallery } from '@/components/home/StaggeredGallery';

export default function HomePage() {
  return (
    <>
      <Hero />
      <InscricoesCountdown />
      <Stats />
      <NewsGrid />
      <CommitteesPreview />
      <AgendaStrip />
      <StaggeredGallery />
      <Testimonials />
    </>
  );
}
