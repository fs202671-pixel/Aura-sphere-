import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeBuilder } from './ThemeBuilder';

describe('ThemeBuilder', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the Theme Builder UI and allows preset selection', async () => {
    render(<ThemeBuilder />);

    expect(screen.getByRole('heading', { name: /Theme Builder/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Salvar Tema/i })).toBeInTheDocument();

    const oceanButton = screen.getByRole('button', { name: /Ocean/i });
    await userEvent.click(oceanButton);

    const primaryInputs = screen.getAllByDisplayValue('#0369a1');
    expect(primaryInputs.length).toBeGreaterThan(0);
    const secondaryInputs = screen.getAllByDisplayValue('#001f3f');
    expect(secondaryInputs.length).toBeGreaterThan(0);
  });

  it('saves a custom theme to localStorage and can reset to default', async () => {
    render(<ThemeBuilder />);

    const primaryInputs = screen.getAllByDisplayValue('#3b82f6');
    const primaryTextInput = primaryInputs.find((input) => input.getAttribute('type') === 'text');
    expect(primaryTextInput).toBeTruthy();
    await userEvent.clear(primaryTextInput!);
    await userEvent.type(primaryTextInput!, '#ff0000');

    const saveButton = screen.getByRole('button', { name: /Salvar Tema/i });
    await userEvent.click(saveButton);

    const stored = JSON.parse(localStorage.getItem('caos_custom_themes') ?? '[]');
    expect(stored.length).toBe(1);
    expect(stored[0].primary).toBe('#ff0000');

    const resetButton = screen.getByRole('button', { name: /Reset/i });
    await userEvent.click(resetButton);

    const resetInputs = screen.getAllByDisplayValue('#3b82f6');
    expect(resetInputs.length).toBeGreaterThan(0);
  });
});
