// Update API endpoint to use explorer subdomain
const API = 'https://explorer.rustchain.org';

// ...

fetchJSON(`${API}/agent/stats`)
  .then(data => {
    // ...
  })
  .catch(error => {
    // ...
  });

fetchJSON(`${API}/agent/jobs`)
  .then(data => {
    // ...
  })
  .catch(error => {
    // ...
  });