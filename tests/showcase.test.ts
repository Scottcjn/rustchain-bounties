import { render } from '@testing-library/react';
import ContributionPage from '../creator-analytics/templates/ContributionPage'; // Clear, controlled import

describe('Integration: Showcase Page Rendering', () => {
    it('should display the showcase page with contributions', () => {
        const { container } = render(<ContributionPage />); // Correct rendering of component // Rendering once
        expect(container).toMatchSnapshot(); // Validate snapshot correctness
    });
});