// Update the API endpoint URL
const apiEndpoint = '/api/hall_of_fame';

// Make sure to handle the case when the API returns 404
fetch(apiEndpoint)
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('Failed to fetch data');
    }
  })
  .then(data => {
    // Update the UI with the fetched data
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });