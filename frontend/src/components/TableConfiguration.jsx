import React, { useEffect, useState } from 'react';
import TableDetails from './TableDetails';
import Top_Bar from "./Top-bar";
import EditTableForm from './EditTableForm';
import AddTableForm from "./AddTableForm";
import TrainModelForm from "./TrainModelForm";
import SideMenu from "./Side-menu";
import axios from "axios";
import {useNavigate} from "react-router-dom";
import '../Styles/Button.css';

const TableList = () => {
  const [tables, setTable] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [isTrainModalOpen, setTrainModalOpen] = useState(false);
  const [isAddModalOpen, setAddModalOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const fetchTableData = async () => {
    try {
      const response =
          await axios.get('http://127.0.0.1:5000/viewTable');
      setTable(response.data);
    } catch (error) {
      console.error('Error fetching pulling:', error);
    }
  };

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/viewTable')
        .then(response => {
          setTable(response.data);
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

  const handleViewDetails = (table) => {
    if (isModalOpen === true) {
      setMessage(null);
      setIsModalOpen(false);
    } else {
      setMessage(null);
      setSelectedTable(table);
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setMessage(null);
    setIsModalOpen(false);
  };

  const handleEditDetails = async (table) => {
    if (isEditModalOpen === true) {
      setMessage(null);
      setEditModalOpen(false);
    } else {
      setMessage(null);
      setSelectedTable(table);
      setEditModalOpen(true);
    }
  }

  const handleCloseEditModal = () => {
    setMessage(null);
    setEditModalOpen(false);
  };

  const handleOpenTrainModel = (table) => {
    if (isTrainModalOpen === true) {
      setMessage(null);
      setTrainModalOpen(false);
    } else {
      setMessage(null);
      setSelectedTable(table);
      setTrainModalOpen(true);
    }
  }

  const handleCloseTrainModel = () => {
    setMessage(null);
    setTrainModalOpen(false);
  }

  const handleDelete = async (table) => {
    try {
      const response = await axios.delete('http://127.0.0.1:5000/deleteTableConfig', {
        headers: {
          'Content-Type': 'application/json',
        },
        params: {
          id: table.id,
          name: table.name,
          description: table.description,
          file_id: table.file_id,
          file_name: table.file_name,
          columns: table.columns,
          model_type: table.model_type,
          hyper_parameters: table.hyper_parameters,
          created_date: table.created_date
        }

      }, {withCredentials: true});
      setMessage(response.data.message);
      console.log('API response message:', response.data.message);
      if (response.status === 200) {
        setTable((prevTables) =>
            prevTables.filter(tab => tab.id !== table.id)
        );
        alert('The configuration deleted successfully.');
        navigate('/table');
      }
    } catch (error) {
      alert('The configuration deleted unsuccessfully.');
      console.error('Error response:', error.response);
    }
  };
  return (
      <div>
        <Top_Bar title="Table Configuration"/>
        <SideMenu/>
        <div style={{display: 'flex'}}>
          <div style={{flex: 1, padding: '20px', textAlign: 'center'}}>
            <h1>Table Configuration List</h1>
            {tables.length === 0 ? (
                <h1 style={{border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>No available configuration</h1>
            ) : (
                tables.map(table => (
                    <div key={table.id} className="table-card"
                         style={{border: '3px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                      <h3>{table.name}</h3>
                      <p>{table.description}</p>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleViewDetails(table)}>
                          View Details 👁️
                        </button>
                        {isModalOpen && selectedTable?.id === table.id && (
                            <TableDetails config={selectedTable} onClose={handleCloseModal}/>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleEditDetails(table)}>
                          Edit ✏️
                        </button>
                        {isEditModalOpen && selectedTable?.id === table.id && (
                            <div className="modal">
                              <EditTableForm table={selectedTable} onClose={handleCloseEditModal}
                                             fetchTable={fetchTableData}/>
                            </div>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleOpenTrainModel(table)}>
                          Train Model 🛠️
                        </button>
                        {isTrainModalOpen && selectedTable?.id === table.id && (
                            <div className="addModal">
                              <TrainModelForm table={selectedTable} onClose={handleCloseTrainModel}/>
                            </div>
                        )}
                      </div>
                      <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                        <button onClick={() => handleDelete(table)}>
                          Delete 🗑️
                        </button>
                      </div>
                    </div>
                ))
            )}
          </div>
        </div>
        <div style={{
          border: '2px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px',
          display: 'flex', justifyContent: 'center', Items: 'center', textAlign: 'center'}}>
          <tr>
            <td>
              <button onClick={() => handleAddConfig()}>
                <h3>Add ➕</h3>
              </button>
            </td>
              {isAddModalOpen && (
                <div className="addModal">
                  <AddTableForm onClose={handleCloseAddModal} fetchTable={fetchTableData}/>
                </div>
              )}
          </tr>
        </div>
      </div>
  );
};


export default TableList;