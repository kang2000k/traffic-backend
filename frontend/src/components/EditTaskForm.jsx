import React, {useEffect, useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const EditTaskForm = ({ task, onClose , fetchTask}) => {
  const navigate = useNavigate();
  const [modelName, setModelName] = useState(null);
  const [file, setFile] = useState([]);
  const [selected_file, setSelected_file] = useState(null);
  const [type] = useState(['Regression', 'Classification']);
  const [formData, setFormData] = useState({
    id: task.id,
    name: task.name || '',
    description: task.description || '',
    train_model_id: task.train_model_id,
    file_id: task.file_id || '',
    file_name: task.file_name || '',
    task_type: task.task_type || '',
  });

  useEffect(() => {
    if (task.train_model_id === null) {
      setModelName("No Model");
    } else {
      // Fetch tasks from Flask backend using Axios
      axios.get('http://127.0.0.1:5000/viewModel')
      .then(response => {
        setModelName(response.data.name);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });
    }
  }, [task.train_model_id]);

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewFile')
      .then(response => {
        setFile(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`http://127.0.0.1:5000/editTask`, formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 200) {
        alert('Updated Successfully');
        fetchTask();
        onClose();
      }
    } catch (error) {
      alert('Update failed');
      fetchTask();
      onClose();
    }
  };

  return (
      <form onSubmit={handleSubmit}>
          <tr>
              <label>
                  Name: {task.name}
              </label>
          </tr>
          <label>
              Description:
              <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  style={{ width: '1530px', height: '100px', fontSize: '20px', marginLeft: '10px'}}
              />
          </label>
          <tr>
              <label>
                  Model: {modelName ? modelName : 'Loading model name...'}
              </label>
          </tr>

          <div>
              <tr>
                  <td>
                      <label htmlFor="file">File:</label>
                  </td>
                  <td>
                      <select
                          id="file"
                          value={formData.file_id}
                          onChange={(e) => {
                              const selected = file.find(f => f.id === e.target.value);
                              setSelected_file(selected);
                              setFormData({
                                  ...formData,
                                  file_id: e.target.value,
                                  file_name: selected ? selected.name : ""
                              });
                          }}
                          style={{width: '1540px', marginLeft: '60px'}}
                      >
                          <option value="" disabled>Select File</option>
                          {file.map((f) => (
                              <option key={f.id} value={f.id}>
                                  {f.name}
                              </option>
                          ))}
                      </select>
                  </td>
              </tr>
              {selected_file && selected_file.webViewLink && (
                  <a href={selected_file.webViewLink} target="_blank" rel="noopener noreferrer">
                      {selected_file.webViewLink}
                  </a>
              )}
          </div>
          <br/>
          <div>
              <tr>
                  <td>
                      <label htmlFor="task_type">Task type:</label>
                  </td>
                  <td>
                      <select
                          id="task_type"
                          value={formData.task_type}
                          onChange={(e) => {
                              setFormData({
                                  ...formData,
                                  task_type: e.target.value,
                              });
                          }}
                          style={{width: '1505px', marginLeft: '60px'}}
                      >
                          <option value="" disabled>Select Task Type</option>
                          {type.map((t) => (
                              <option key={t} value={t}>
                                  {t}
                              </option>
                          ))}
                      </select>
                  </td>
              </tr>
          </div>

          {/* Add more input fields for other properties as necessary */}

          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default EditTaskForm;