import React from 'react';

export default function TestComponent() {
  return (
    <div>
      <Button 
        label="Click Me"
        variant="primary"
        size="large"
        disabled={false}
      />
      <Input 
        placeholder="Enter text"
        maxLength={100}
        required={true}
      />
      <Card
        title="Test Card"
        description="This is a test"
        imageUrl="/test.jpg"
      />
    </div>
  );
}
