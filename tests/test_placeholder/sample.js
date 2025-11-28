import React from 'react';

function HomePage() {
  return (
    <div>
      <h1>Home Page</h1>
      <p>Welcome to our website</p>
      <button>Submit</button>
    </div>
  );
}

function AboutPage() {
  return (
    <div>
      <h1>About Us</h1>
      <p>Learn more about our company</p>
      <button>Save Changes</button>
    </div>
  );
}

function ContactPage() {
  return (
    <div>
      <h1>Contact</h1>
      <label>Email Address</label>
      <label>Phone Number</label>
      <button>Cancel</button>
    </div>
  );
}

export { HomePage, AboutPage, ContactPage };
