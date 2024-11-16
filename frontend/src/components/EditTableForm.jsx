import React, {useEffect, useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const EditTableForm = ({ table, onClose , fetchTable}) => {
  const navigate = useNavigate();
  const [file, setFile] = useState([]);
  const [selected_file, setSelected_file] = useState(null);
  const [type, setType] = useState([]);
  const [formData, setFormData] = useState({
    id: table.id,
    name: table.name || '',
    description: table.description || '',
    file_id: table.file_id || '',
    file_name: table.file_name || '',
    columns: table.columns || '',
    model_type_id: '',
    model_type: table.model_type,
    hyper_parameters: JSON.stringify(table.hyper_parameters) || ''
  });

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

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewModelType')
      .then(response => {
        setType(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });
  }, []);

  useEffect(() => {
    if (type.length > 0 && table.model_type) {
      const matchingType = type.find(t => t.type_name === table.model_type);
      if (matchingType) {
        setFormData(prevFormData => ({
          ...prevFormData,
          model_type_id: matchingType.id
        }));
      }
    }
  }, [type, table.model_type]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'columns') {
        setFormData({ ...formData,
            columns: value.split(',') });
    } else {
        setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`http://127.0.0.1:5000/editTableConfig`, formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 200) {
        alert('Updated Successfully');
        fetchTable();
        onClose();
      }
    } catch (error) {
      alert('Update failed');
      fetchTable();
      onClose();
    }
  };

  return (
      <form onSubmit={handleSubmit}>
          <label>
              Name:
              <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  style={{ width: '1515px', marginLeft: '39px'}}
              />
          </label>

          <label>
              Description:
              <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  style={{ width: '1530px', height: '100px', fontSize: '20px', marginLeft: '10px'}}
              />
          </label>

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
          <label>
              <div>
                  <tr>
                      <td>
                          Columns selected eg.(a, b, c):
                      </td>
                  </tr>
              </div>
              <input
                  type="text"
                  name="columns"
                  value={formData.columns}
                  onChange={handleChange}
                  style={{ width: '1600px'}}
              />
          </label>
          <br/>
          <div>
              <tr>
                  <td>
                      <label htmlFor="type">Model Type:</label>
                  </td>
                  <td>
                      <select
                          id="type"
                          value={formData.model_type_id}
                          onChange={(e) => {
                              setFormData({
                                  ...formData,
                                  model_type_id: e.target.value,
                              });
                          }}
                          style={{width: '1510px', marginLeft: '40px'}}
                      >
                          <option value={formData.model_type}>{formData.model_type}</option>
                          {type.map((t) => (
                              <option key={t.id} value={t.id}>
                                  {t.type_name}
                              </option>
                          ))}
                      </select>
                  </td>
              </tr>
          </div>
          <br/>
          <label>
              Hyper parameters:
              <input
                  type="text"
                  name="hyper_parameters"
                  value={formData.hyper_parameters}
                  onChange={handleChange}
                  style={{ width: '1475px', marginLeft: '13px'}}
              />
          </label>

          {/* Add more input fields for other properties as necessary */}

          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default EditTableForm;
