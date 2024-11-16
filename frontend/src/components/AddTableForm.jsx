import React, {useEffect, useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const AddTableForm = ({onClose, fetchTable}) => {
  const navigate = useNavigate();
  const [file, setFile] = useState([]);
  const [selected_file, setSelected_file] = useState(null);
  const [type, setType] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description:  '',
    file_id: '',
    file_name: '',
    columns: '',
    model_type_id: '',
    hyper_parameters: ''
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/addTableConfig', formData, {
        headers: {
            'Content-Type': 'application/json',
        }
})

      if (response.status === 200) {
        alert('Created Successfully');
        fetchTable();
        onClose();
      }
    } catch (error) {
      alert('Created failed');
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
                  style={{ width: '1538px', marginLeft: '37px'}}
              />
          </label>

          <label>
              Description:
              <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  style={{ width: '1550px', height: '100px', fontSize: '20px', marginLeft: '10px'}}
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
              <tr>
                  <td>
                      Columns selected eg.(a, b, c):
                  </td>
              </tr>
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
                          <option value="" disabled>Select Model Type</option>
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
                  style={{ width: '1435px', marginLeft: '62px'}}
              />
          </label>

          {/* Add more input fields for other properties as necessary */}

          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default AddTableForm;
