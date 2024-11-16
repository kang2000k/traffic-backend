import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { faBars } from '@fortawesome/free-solid-svg-icons';
import React, {useState} from 'react';
import '../Styles/Top-bar.css'


const Top_Bar = ({ title }) => {
  // State to manage dropdown visibility
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
  };

  return (
    <div className="top-bar">
      <h1 className="title">{title}</h1>
        <div className="profile-container">
            {/* Profile Button */}
            <button className="profile-button" onClick={toggleDropdown}>
                <FontAwesomeIcon icon={faUser}/>
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
                <div className="dropdown-menu">
                    <h3>System Admin</h3>
                    <ul>
                        <li><a href="/getDriveServiceAccess">Get Google Drive Service Access</a></li>
                        <li><a href="/renew">Renew Credentials</a></li>
                        <li><a href="/login">Sign Out</a></li>
                    </ul>
                </div>
            )}
        </div>
    </div>
  );
};

export default Top_Bar;