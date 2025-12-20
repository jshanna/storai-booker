import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/utils';
import { HomePage } from './HomePage';

describe('HomePage', () => {
  it('renders the hero section with title', () => {
    render(<HomePage />);
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('renders the call to action buttons', () => {
    render(<HomePage />);
    // Check for the main CTA button
    const createButton = screen.getByRole('link', { name: /create/i });
    expect(createButton).toBeInTheDocument();
    expect(createButton).toHaveAttribute('href', '/generate');
  });

  it('renders the features section', () => {
    render(<HomePage />);
    // Check for feature cards - they use Card component with specific text
    expect(screen.getByText(/personalized stories/i)).toBeInTheDocument();
    expect(screen.getByText(/beautiful illustrations/i)).toBeInTheDocument();
    expect(screen.getByText(/multiple formats/i)).toBeInTheDocument();
  });

  it('has accessible navigation links', () => {
    render(<HomePage />);
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
  });
});
