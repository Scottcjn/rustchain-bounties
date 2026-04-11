import { render, screen } from '@testing-library/react';
import ContributionShowcase from '../creator-analytics/templates/ContributionShowcase.jsx';

describe('ContributionShowcase', () => {
    test('renders merged contributions section', () => {
        render(<ContributionShowcase />);
        const headingElement = screen.getByText(/Merged Contributions/i);
        expect(headingElement).toBeInTheDocument();
    });

    test('renders individual contributions with links', () => {
        render(<ContributionShowcase />);
        const linkElement = screen.getByText(/OpenSSL/i);
        expect(linkElement).toHaveAttribute('href', 'https://github.com/openssl/openssl/pull/30437');
    });
});