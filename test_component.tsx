// test_component.tsx
// Test file for JSX Parameter Extractor

import React from 'react';

export default function TestComponent() {
  return (
    <div className="container" data-testid="main-container">
      <h1 label="Page Title">Welcome</h1>
      <Button 
        label="Click Me" 
        onClick={handleClick}
        variant="primary"
      />
      <Card label="User Card">
        <div className="content">
          <p label="Description">This is a test component</p>
          <span>{dynamicText}</span>
        </div>
      </Card>
      <AuthGuard>
        <Dashboard label="Main Dashboard" />
        <StatsCard label="Statistics" count={42} />
      </AuthGuard>
    </div>
  );
}
