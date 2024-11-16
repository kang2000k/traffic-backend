import React, {useEffect, useState} from 'react';
import axios from "axios";
import '../Styles/Button.css';

const ModelDetails = ({ model, onClose }) => {
  const [tables, setTables] = useState([]);

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewTable')
      .then(response => {
        setTables(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });
  }, []);

  const getTableName = () => {
    if (!tables) return '';
    for (let i = 0; i < tables.length; i++) {
        if (tables[i].id === model.table_configuration_id) {
            return tables[i].name;
        }
    }
    return 'Table not found';
  }

  if (!model) return null;

  return (
    <div className="modal">
        <div className="modal-content">
            <label>
                <h2>Details</h2>
                <p>Name: {model.name}</p>
                <p>Description: {model.description}</p>
                <p>Model file: {model.model_file}</p>
                <p>Created date: {model.created_date}</p>
                <p>Table name: {getTableName() || 'Loading table name...'}</p>
            </label>
            <button onClick={onClose}>Close ❌</button>
        </div>
    </div>
  );
};

export default ModelDetails;