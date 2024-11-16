import React from 'react';
import '../Styles/Button.css';

const TableDetails = ({ config, onClose }) => {
  if (!config) return null;

  const getGoogleDriveViewLink = (fileId) => {
    return `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;
  };

  return (
    <div className="modal">
        <div className="modal-content">
            <label>
                <h2>Details</h2>
                <p>Name: {config.name}</p>
                <p>Description: {config.description}</p>
                <p>File: {config.file_name || 'No File'}</p>
                <a href={getGoogleDriveViewLink(config.file_id)} target="_blank" rel="noopener noreferrer">
                    {config.file_name ? getGoogleDriveViewLink(config.file_id) : ''}
                </a>
                <div>
                    <p>Columns:

                    {config.columns === [] ? config.columns.map((column, index) => (
                        <p key={index} style={{marginLeft: '20px'}}> {index + 1}) {column}</p>
                    )) : 'No selected columns'} </p>
                </div>
                <p>Model Type: {config.model_type}</p>
                <p>Hyper parameters: {JSON.stringify(config.hyper_parameters)}</p>
                <p>Created Date: {config.created_date}</p>
            </label>
            <button onClick={onClose}>Close ❌</button>
        </div>
    </div>
  );
};

export default TableDetails;