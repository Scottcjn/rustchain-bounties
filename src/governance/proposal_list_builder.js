// Replace innerHTML with a safer alternative to prevent DOM XSS
function buildProposalList(proposals) {
  const list = document.getElementById('proposal-list');
  list.innerHTML = ''; // Clear the list

  proposals.forEach((proposal) => {
    const proposalElement = document.createElement('div');
    proposalElement.textContent = proposal.name; // Use textContent instead of innerHTML
    list.appendChild(proposalElement);
  });
}