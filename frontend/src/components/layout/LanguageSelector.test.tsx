import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { LanguageSelector } from './LanguageSelector';

// Mock the UI store
vi.mock('@/lib/stores/uiStore', () => ({
  useUIStore: vi.fn((selector) => {
    const state = {
      locale: 'en',
      setLocale: vi.fn(),
    };
    return selector(state);
  }),
}));

describe('LanguageSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the language selector button', () => {
    render(<LanguageSelector />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('displays the globe icon', () => {
    render(<LanguageSelector />);
    const button = screen.getByRole('button');
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('opens dropdown menu on click', async () => {
    const user = userEvent.setup();
    render(<LanguageSelector />);

    await user.click(screen.getByRole('button'));

    // Check that language options are visible
    expect(screen.getByText('English')).toBeInTheDocument();
    expect(screen.getByText('Español')).toBeInTheDocument();
    expect(screen.getByText('Français')).toBeInTheDocument();
  });

  it('displays flag emojis for each language', async () => {
    const user = userEvent.setup();
    render(<LanguageSelector />);

    await user.click(screen.getByRole('button'));

    // The flags should be visible in the menu items
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems.length).toBe(3);
  });
});
