import { render, screen } from '@testing-library/react';
import ContributionPage from '../creator-analytics/templates/ContributionPage';  // Clear and controlled import

describe('Contribution Page', () => {
    it('renders merged contributions correctly', () => {
        const { container } = render(<ContributionPage />); // Render once for testing
        expect(screen.getByText(/OpenSSL/i)).toBeInTheDocument(); // Check for OpenSSL presence
        expect(screen.getByText(/26K/i)).toBeInTheDocument(); // Validate star count
        expect(screen.getByText(/libdragon/i)).toBeInTheDocument(); // Confirm libdragon entry
        expect(screen.getByText(/capstone/i)).toBeInTheDocument(); // Check for capstone presence
        expect(screen.getByText(/wolfSSL/i)).toBeInTheDocument(); // Confirm wolfSSL presence
    });
    it('renders contributions in review correctly:', () => {
        const { container } = render(<ContributionPage />); // Render for contributions under review
        expect(screen.getByText(/wolfSSL/i)).toBeInTheDocument(); // Verify wolfSSL presence
        expect(screen.getByText(/2K/i)).toBeInTheDocument(); // Check stars under review
    });
});