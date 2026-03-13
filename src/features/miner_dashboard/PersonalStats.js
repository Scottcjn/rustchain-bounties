import React, { useEffect, useState } from 'react';
import axios from 'axios';

const PersonalStats = ({ minerId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`https://api.example.com/miners/${minerId}/stats`);
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error fetching stats');
        setLoading(false);
      }
    };
    fetchStats();
  }, [minerId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Miner Stats</h2>
      <p>Balance: {stats.balance} RTC</p>
      <p>Total Rewards: {stats.totalRewards} RTC</p>
      <h3>Reward History</h3>
      <ul>
        {stats.rewardHistory.map((reward, index) => (
          <li key={index}>Date: {reward.date}, Amount: {reward.amount} RTC</li>
        ))}
      </ul>
    </div>
  );
};

export default PersonalStats;