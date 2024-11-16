import React, {useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const TrainModelForm = ({table, onClose}) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
      name: '',
      description: '',
      table_configuration_id: table.id,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      formData.table_configuration_id = parseInt(formData.table_configuration_id, 10);
      const response = await axios.post('http://127.0.0.1:5000/trainModel', formData, {
        headers: {
    'Content-Type': 'application/json',
        }
})

      if (response.status === 200) {
        alert('Start Train');
        onClose();
        navigate('/model');
      }
    } catch (error) {
      alert('Failed to start Train');
      onClose();
      navigate('/table');
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
          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default TrainModelForm;
