import { render, screen } from '@testing-library/react';
import ContributionShowcase from '../creator-analytics/templates/ContributionShowcase.jsx';

describe('Contribution Showcase Integration', () => {
    test('renders the entire showcase without crashing', () => {
        const { container } = render(<ContributionShowcase />);
        expect(container).toBeTruthy();
    });

    test('displays contributions correctly', () => {
        render(<ContributionShowcase />);
        const contributionList = screen.getByRole('list');
        expect(contributionList).toBeInTheDocument();
        expect(contributionList.children.length).toBeGreaterThan(0);
    });
});