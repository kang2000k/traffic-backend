import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import '../Styles/Login.css';

const Login = () => {
  const [role, setRole] = useState('System Admin');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      // Send the POST request to the Flask API
      const response = await axios.post('http://127.0.0.1:5000/Login', {
        username: username,
        password: password,
        role: role
      }, {withCredentials: true});
      setMessage(response.data.message);
      console.log('API response message:', response.data.message);
      if (response.status === 200) {
        navigate('/dashboard');
      }
  } catch (error) {
        alert('Login failed. Invalid credentials.');
  }
};


  return (
    <div className="login-container">
      <div className="login-image">
        <img src="/Modern_British_LED_Traffic_Light.jpg" alt="Traffic light" />
      </div>
      <div className="login-form">
        <br/>
        <h2>Welcome</h2>
        <form onSubmit={handleLogin}>
          <br/>
          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
            >
              <option value="System Admin">System Admin</option>
              <option value="User">User</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />
          </div>
          <br/>
          <button type="submit" className="sign-in-btn">
            Sign In &rarr;
          </button>
        </form>
        <br/>
        <p className="message">{message}</p>
        <div className="extra-links">
          <br/>
        </div>
      </div>
    </div>
  );
}

export default Login;
