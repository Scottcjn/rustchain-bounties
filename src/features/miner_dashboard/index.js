import React from 'react';
import ReactDOM from 'react-dom';
import MinerDashboard from './MinerDashboard';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

ReactDOM.render(
  <Router>
    <Routes>
      <Route path='/miner/:minerId' element={<MinerDashboard />} />
    </Routes>
  </Router>,
  document.getElementById('root')
);