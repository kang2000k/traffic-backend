import React, {useEffect, useState} from 'react';
import axios from "axios";
import '../Styles/Button.css';

const TaskDetails = ({ task, onClose }) => {
  const [models, setModels] = useState([]);

  const getGoogleDriveViewLink = (fileId) => {
    return `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;
  };

  useEffect(() => {
      // Fetch tasks from Flask backend using Axios
      axios.get('http://127.0.0.1:5000/viewModel')
      .then(response => {
        setModels(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });
  }, []);

  const getModelName = () => {
    if (!models) return '';
    for (let i = 0; i < models.length; i++) {
        if (models[i].id === task.train_model_id) {
            return models[i].name;
        }
    }
    return 'Model not found';
  }

  if (!task) return null;

  return (
    <div className="modal">
        <div className="modal-content">
            <label>
                <h2>Details</h2>
                <p>Name: {task.name}</p>
                <p>Description: {task.description}</p>
                <p>Model: {getModelName() || 'Loading model name...'}</p>
                <p>File: {task.file_name || 'No file'} </p>
                <a href={getGoogleDriveViewLink(task.file_id)} target="_blank" rel="noopener noreferrer">
                    {task.file_name ? getGoogleDriveViewLink(task.file_id) : ''}
                </a>
                <p>Task type: {task.task_type}</p>
            </label>
            <button onClick={onClose}>Close ❌</button>
        </div>
    </div>
  );
};

export default TaskDetails;