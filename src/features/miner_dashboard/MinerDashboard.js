import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import PersonalStats from './PersonalStats';

const MinerDashboard = () => {
  const { minerId } = useParams();

  return (
    <div>
      <h1>Miner Dashboard</h1>
      <PersonalStats minerId={minerId} />
    </div>
  );
};

export default MinerDashboard;