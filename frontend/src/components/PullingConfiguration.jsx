import React, {useEffect, useState} from 'react';
import PullingDetails from './PullingDetails';
import Top_Bar from "./Top-bar";
import EditPullingForm from './EditPullingForm';
import AddPullingForm from "./AddPullingForm";
import SideMenu from "./Side-menu";
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const PullingList = () => {
  const [pullings, setPulling] = useState([]);
  const [selectedPullings, setSelectedPullings] = useState(null);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [isAddModalOpen, setAddModalOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const fetchPullingData = async () => {
    try {
      const response =
          await axios.get('http://127.0.0.1:5000/viewPull');
      setPulling(response.data);
    } catch (error) {
      console.error('Error fetching pulling:', error);
    }
  };

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewPull', {
      withCredentials: true
    })
        .then(response => {
          setPulling(response.data);
          console.log(response.data);
        })
        .catch(error => {
          console.error('Error fetching pulling:', error);
        });
  }, []);

  const handleAddConfig = () => {
    if (isAddModalOpen === true){
      setAddModalOpen(false);
    } else {
      setAddModalOpen(true);
    }
  }

  const handleCloseAddModal = () => {
    setAddModalOpen(false);
  };

  const handleViewDetails = (pulling) => {
    if (isModalOpen === true) {
      setMessage(null);
      setIsModalOpen(false);
    } else {
      setMessage(null);
      setSelectedPullings(pulling);
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setMessage(null);
    setIsModalOpen(false);
  };

  const handleEditDetails = async (pulling) => {
    if (isEditModalOpen === true) {
      setMessage(null);
      setEditModalOpen(false);
    } else {
      setMessage(null);
      setSelectedPullings(pulling);
      setEditModalOpen(true);
    }
  }

  const handleCloseEditModal = () => {
    setMessage(null);
    setEditModalOpen(false);
  };

  const handleDelete = async (pulling) => {
    try {
      const response = await axios.delete('http://127.0.0.1:5000/deletePull', {
        headers: {
          'Content-Type': 'application/json',
        },
        params: {
          id: pulling.id,
          name: pulling.name,
          description: pulling.description,
          data_source: pulling.data_source,
          header: pulling.headers,
          frequency_min: pulling.frequency_min,
          last_pulled_at: pulling.last_pulled_at,
          created_date: pulling.created_date,
          params: pulling.params
        }

      }, {withCredentials: true});
      setMessage(response.data.message);
      console.log('API response message:', response.data.message);
      if (response.status === 200) {
        setPulling((prevPullings) =>
            prevPullings.filter(pull => pull.id !== pulling.id)
        );
        alert('The configuration deleted successfully.');
        navigate('/pulling');
      }
    } catch (error) {
      alert('The configuration deleted unsuccessfully.');
      console.error('Error response:', error.response);
    }
  };

  return (
      <div>
        <Top_Bar title="Pulling Configuration"/>
        <SideMenu/>
        <div style={{display: 'flex'}}>
          <div style={{flex: 1, padding: '10px', textAlign: 'center'}}>
            <h1>Pulling Configuration List</h1>
            {pullings.length === 0 ? (
                <h1 style={{border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>No available configuration</h1>
            ) : (
                pullings.map(pulling => (
                    <div key={pulling.id} className="pulling-card" style={{ border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
                      <h2>{pulling.name}</h2>
                      <h3>{pulling.description}</h3>
                      <div style={{ border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
                        <button onClick={() => handleViewDetails(pulling)}>
                        View Details 👁️
                      </button>
                      {isModalOpen && selectedPullings?.id === pulling.id && (
                          <PullingDetails config={selectedPullings} onClose={handleCloseModal}/>
                      )}
                      </div>
                      <div style={{ border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px' }}>
                        <button onClick={() => handleEditDetails(pulling)}>
                            Edit ✏️
                        </button>
                        {isEditModalOpen && selectedPullings?.id === pulling.id && (
                          <div className="modal">
                            <EditPullingForm pulling={selectedPullings} onClose={handleCloseEditModal}
                                             fetchData={fetchPullingData}/>
                          </div>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleDelete(pulling)}>
                          Delete 🗑️
                        </button>
                      </div>
                    </div>
                ))
            )}
          </div>
        </div>
      <div style={{ border: '2px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px',
        display: 'flex', justifyContent: 'center', Items: 'center', textAlign: 'center'}}>
        <tr>
          <td>
            <button onClick={() => handleAddConfig()}>
              <h3>Add ➕</h3>
            </button>
          </td>
          {isAddModalOpen && (
              <div className="addModal">
              <AddPullingForm onClose={handleCloseAddModal} fetchData={fetchPullingData}/>
            </div>
          )}
        </tr>
        </div>

      </div>
  );
};

export default PullingList;