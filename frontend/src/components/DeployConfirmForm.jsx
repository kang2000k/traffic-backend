import React, {useEffect, useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const DeployConfirmForm = ({model, onClose, fetchModel}) => {
  const navigate = useNavigate();
  const [task, setTask] = useState([]);
  const [selected_task, setSelected_task] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    description: '',
    train_model_id: '',
    file_id: '',
    file_name: '',
    task_type: '',
  });

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/ViewTask')
      .then(response => {
        setTask(response.data);
        console.log(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
        setLoading(false);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (selected_task?.train_model_id != null) {
      const confirmSubmit = window.confirm("This task is using another model. Proceed to change model?");
      if (!confirmSubmit) {
        alert('Deployment Cancelled');
        fetchModel();
        onClose();
        return;
      }
    }

    try {

      const response = await axios.put('http://127.0.0.1:5000/deployModel', formData, {
        headers: {
          'Content-Type': 'application/json',
        }})
        if (response.status === 200) {
          alert('Deployed Successfully');
          onClose();
          navigate('/dashboard');
        }
    } catch (error) {
        alert('Deployed failed');
        fetchModel();
        onClose();
    }
  };

  if (loading) {
    return <p>Loading tasks...</p>;
  }

  return (
      <form onSubmit={handleSubmit}>
          <h3>
              <label>Name: {model.name}</label>
              <label>Description: {model.description}</label>
              <label>Created date: {model.created_date}</label>
          </h3>
          <br/>
          <hr/>
          <div>
              <tr>
                  <td>
                      <label htmlFor="task">Task:</label>
                  </td>
                  <td>
                      <select
                          id="task"
                          value={formData.id}
                          onChange={(e) => {
                            const selected = task.find(t => t.id === e.target.value);
                            setSelected_task(selected);
                            setFormData({
                            ...formData,
                            id: e.target.value,
                            name: selected ? selected.name : "",
                            description: selected ? selected.description : "",
                            train_model_id: model.id,
                            file_id: selected ? selected.file_id : "",
                            file_name: selected ? selected.file_name : "",
                            task_type: selected ? selected.task_type : "",
                            });
                          }}
                          style={{width: '1540px', marginLeft: '60px'}}
                      >
                          <option value="" disabled>Select Task</option>
                          {task.map((t) => (
                              <option key={t.id} value={t.id}>
                                  {t.name}
                              </option>
                          ))}
                      </select>
                  </td>
              </tr>
          </div>

          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default DeployConfirmForm;
