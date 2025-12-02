import React from 'react';

function WelcomeCard({ title, description }) {
  return (
    <div className="card">
      <h1>{title}</h1>
      <p>{description}</p>
      <AuthGuard>
        <StatsCard label="Total Users" value="1234" />
        <StatsCard label="Active Sessions" value="56" />
      </AuthGuard>
    </div>
  );
}

export default WelcomeCard;
