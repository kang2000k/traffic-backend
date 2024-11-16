import React, { useEffect, useState, useContext } from 'react';
import ModelDetails from './ModelDetails';
import Top_Bar from "./Top-bar";
import EditModelForm from './EditModelForm';
import DeployConfirmForm from "./DeployConfirmForm";
import SideMenu from "./Side-menu";
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const ModelList = () => {
  const [models, setModel] = useState([]);
  const [modelStatuses, setModelStatuses] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [isDeployModalOpen, setDeployModalOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const fetchModelData = async () => {
    try {
      const response =
        await axios.get('http://127.0.0.1:5000/viewModel');
        setModel(response.data);
    } catch (error) {
      console.error('Error fetching pulling:', error);
    }
  };

  const fetchStatuses = async () => {
    try {
      const response =
        await axios.get('http://127.0.0.1:5000/getModelStatus');
        setModelStatuses(response.data);
    } catch (error) {
      console.error('Error fetching pulling:', error);
    }
  };

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewModel')
      .then(response => {
        setModel(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });

  }, []);

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/getModelStatus')
      .then(response => {
        setModelStatuses(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching pulling:', error);
      });

    const intervalId = setInterval(fetchStatuses, 5000);

    return () => clearInterval(intervalId);

  }, []);

  const getStatus = (model_id) => {
    const statusObj = modelStatuses.find(status => status.id === model_id);
    return statusObj ? statusObj.status : 'Not started';
  };

  const getMessage = (model_id) => {
    const messageObj = modelStatuses.find(message => message.id === model_id);
    return messageObj ? messageObj.message : '';
  };

  const handleDeployModel = (model) => {
    if (isDeployModalOpen === true) {
      setDeployModalOpen(false);
    } else {
      setDeployModalOpen(true);
      setSelectedModel(model);
    }

  }

  const handleCloseDeployModal = () => {
    setDeployModalOpen(false);
  };

  const handleViewDetails = (model) => {
    if (isModalOpen === true) {
      setMessage(null);
      setIsModalOpen(false);
    } else {
      setMessage(null);
      setSelectedModel(model);
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setMessage(null);
    setIsModalOpen(false);
  };

  const handleEditDetails = async (model) => {
    if (isEditModalOpen === true) {
      setMessage(null);
      setEditModalOpen(false);
    } else {
      setMessage(null);
      setSelectedModel(model);
      setEditModalOpen(true);
    }

  }

  const handleCloseEditModal = () => {
    setMessage(null);
    setEditModalOpen(false);
  };

  const handleDelete = async (model) => {
    try {
      const response = await axios.delete('http://127.0.0.1:5000/deleteModel', {
        headers: {
          'Content-Type': 'application/json',
        },
        params: {
          id: model.id,
          name: model.name,
          description: model.description,
          model_file: model.model_file,
          created_date: model.created_date,
          table_configuration_id: model.table_configuration_id
        }

      }, {withCredentials: true});

      setMessage(response.data.message);
      console.log('API response message:', response.data.message);

      if (response.status === 200) {
        setModel((prevModel) =>
        prevModel.filter(m => m.id !== model.id)
      );
        alert('The model deleted successfully.');
        navigate('/model');
      }
  } catch (error) {
      alert('The model deleted unsuccessfully.');
      console.error('Error response:', error.response);
  }
};

  return (
      <div>
        <Top_Bar title="Trained Model"/> {/* Use the top bar here */}
        <SideMenu/>
        <div style={{display: 'flex'}}>
          <div style={{flex: 1, padding: '20px', textAlign: 'center'}}>
            <h1>Trained Model List</h1>
            {models.length === 0 ? (
                <h1 style={{border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>No available model</h1>
            ) : (
                models.map(model => (
                    <div key={model.id} className="models-card" style={{border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                      <h3>{model.name}</h3>
                      <p>{model.description}</p>
                      <p>Status: {getStatus(model.id)}</p>
                      <p>Message: {getMessage(model.id)}</p>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleViewDetails(model)}>
                          View Details 👁️
                        </button>
                        {isModalOpen && selectedModel?.id === model.id && (
                          <ModelDetails model={selectedModel} onClose={handleCloseModal}/>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleEditDetails(model)}>
                          Edit ✏️
                        </button>
                        {isEditModalOpen && selectedModel?.id === model.id && (
                          <div className="modal">
                            <EditModelForm model={selectedModel} onClose={handleCloseEditModal}
                             fetchModel={fetchModelData} />
                          </div>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                      <button onClick={() => handleDeployModel(model)}>
                        Deploy 🚀
                      </button>
                      {isDeployModalOpen && selectedModel?.id === model.id && (
                        <div className="deployModal">
                          <DeployConfirmForm model={selectedModel} onClose={handleCloseDeployModal}
                              fetchModel={fetchModelData} />
                        </div>
                      )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleDelete(model)}>
                          Delete 🗑️
                        </button>
                      </div>
                    </div>
                ))
            )}
          </div>
        </div>
      </div>
  );
};


export default ModelList;