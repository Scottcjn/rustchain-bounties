// Add a route for the /api/hall_of_fame endpoint
app.get('/api/hall_of_fame', (req, res) => {
  // Return the hall of fame data
  res.json(hallOfFameData);
});