import '../Styles/Side-menu.css'
const SideMenu = () => {

  return (
        <div className="menu-box">
            <h3 style={{marginLeft: '70px'}}>
                <a href="/dashboard">Dashboard</a>
                <a href="/pulling">View Pulling Configuration</a>
                <a href="/table">View Table Configuration</a>
                <a href="/model">View Trained Model</a>
            </h3>
        </div>
  );
};

export default SideMenu;
