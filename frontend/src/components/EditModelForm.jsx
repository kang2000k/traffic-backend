import React, {useState} from 'react';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const EditModelForm = ({ model, onClose , fetchModel}) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    id: model.id,
    name: model.name,
    description: model.description || '',
    model_file: model.model_file,
    created_date: model.created_date,
    table_configuration_id: model.table_configuration_id,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`http://127.0.0.1:5000/editModel`, formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 200) {
        alert('Updated Successfully');
        fetchModel();
        onClose();
      }
    } catch (error) {
      alert('Update failed');
      fetchModel();
      onClose();
    }
  };

  return (
      <form onSubmit={handleSubmit}>
          <tr>
              <label>Name: {formData.name}</label>
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
          <button type="submit">Submit ✅</button>
          <button type="button" onClick={onClose}>Cancel ❌</button>
      </form>
  );
};

export default EditModelForm;
