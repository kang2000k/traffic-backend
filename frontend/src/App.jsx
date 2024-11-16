import { Route, Routes} from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import PullingConfiguration from "./components/PullingConfiguration";
import TableConfiguration from "./components/TableConfiguration";
import TrainedModel from "./components/TrainedModel";
import Renew from './components/Renew';
import GetDriveServiceAccess from './components/GetDriveServiceAccess';

function App() {


  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/renew" element={<Renew />} />
      <Route path="/getDriveServiceAccess" element={<GetDriveServiceAccess />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/pulling" element={<PullingConfiguration />} />
      <Route path="/table" element={<TableConfiguration />} />
      <Route path="/model" element={<TrainedModel />} />
      <Route path="/" element={<Login />} />
    </Routes>
  );
}

export default App;
