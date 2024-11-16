import React from 'react';
import '../Styles/Button.css';

const PullingDetails = ({ config, onClose }) => {
  if (!config) return null;

  return (
    <div className="modal">
        <div className="modal-content">
            <label>
                <h2>Details</h2>
                <p>Name: {config.name}</p>
                <p>Description: {config.description}</p>
                <p>Data source: {config.data_source}</p>
                <p>Headers: {JSON.stringify(config.headers)}</p>
                <p>Parameters: {JSON.stringify(config.params)}</p>
                <p>Frequency min: {config.frequency_min}</p>
                <p>Last pulled at: {config.last_pulled_at}</p>
                <p>Created date:{config.created_date}</p>
            </label>
            <button onClick={onClose}>Close ❌</button>
        </div>
    </div>
  );
};

export default PullingDetails;