import React, { useEffect, useState } from 'react';
import TaskDetails from './TaskDetails';
import TopBar from "./Top-bar";
import SideMenu from "./Side-menu";
import axios from "axios";
import EditTaskForm from "./EditTaskForm";
import '../Styles/Button.css';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [message, setMessage] = useState('');

  const fetchTaskData = async () => {
    try {
      const response =
          await axios.get('http://127.0.0.1:5000/ViewTask');
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching pulling:', error);
    }
  };

  useEffect(() => {
    // Fetch tasks from Flask backend using Axios
    axios.get('http://127.0.0.1:5000/ViewTask', {
      withCredentials: true
    })
      .then(response => {
        setTasks(response.data);
        console.log(response.data);
      })
      .catch(error => {
        console.error('Error fetching tasks:', error);
      });
  }, []);

  const handleViewDetails = (task) => {
    if (isModalOpen === true) {
      setIsModalOpen(false);
    } else {
      setSelectedTask(task);
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleEditDetails = async (task) => {
    if (isEditModalOpen === true) {
      setMessage(null);
      setEditModalOpen(false);
    } else {
      setMessage(null);
      setSelectedTask(task);
      setEditModalOpen(true);
    }
  }

  const handleCloseEditModal = () => {
    setMessage(null);
    setEditModalOpen(false);
  };

  return (
    <div>
      <TopBar title="Dashboard" />
      <SideMenu />
      <div style={{ display: 'flex' }}>
        <div style={{ flex: 1, padding: '20px', textAlign: 'center'}}>
          <h1>Task List</h1>
          {tasks.length === 0 ? (
            <h2>No available tasks</h2>
          ) : (
            tasks.map(task => (
                <div key={task.id}
                     style={{border: '1px solid #ccc', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                  <h2>{task.name}</h2>
                  <h3>{task.description}</h3>
                  <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                    <button onClick={() => handleViewDetails(task)}>
                      View Details 👁️
                    </button>
                    {isModalOpen && selectedTask?.id === task.id && (
                        <TaskDetails task={selectedTask} onClose={handleCloseModal}/>
                    )}
                  </div>
                  <div style={{border: '1px solid black', padding: '10px', margin: '10px 0', borderRadius: '5px'}}>
                    <button onClick={() => handleEditDetails(task)} style={{marginLeft: '10px'}}>
                      Edit ✏️
                    </button>
                    {isEditModalOpen && selectedTask?.id === task.id && (
                      <div className="modal">
                        <EditTaskForm task={selectedTask} onClose={handleCloseEditModal} fetchTask={fetchTaskData}/>
                      </div>
                    )}
                  </div>
                </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskList;