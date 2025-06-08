import { IonApp, IonRouterOutlet, setupIonicReact } from '@ionic/react';
import { BrowserRouter } from 'react-router-dom';  // CAMBIO: usar BrowserRouter
import { Routes, Route, Navigate } from 'react-router-dom';
import ChatScreen from './components/ChatScreen';
/* Core CSS required for Ionic components to work properly */
import '@ionic/react/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';

/* Optional CSS utils that can be commented out */
import '@ionic/react/css/padding.css';
import '@ionic/react/css/float-elements.css';
import '@ionic/react/css/text-alignment.css';
import '@ionic/react/css/text-transformation.css';
import '@ionic/react/css/flex-utils.css';
import '@ionic/react/css/display.css';

/* Ionic Dark Mode */
/* import '@ionic/react/css/palettes/dark.always.css'; */
/* import '@ionic/react/css/palettes/dark.class.css'; */
import '@ionic/react/css/palettes/dark.system.css';

/* Theme variables */
import './theme/variables.css';

setupIonicReact();

const App: React.FC = () => {
  return (
    <IonApp>
      <BrowserRouter>   {/* CAMBIO AQUI */}
        <IonRouterOutlet>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatScreen />} />
          </Routes>
        </IonRouterOutlet>
      </BrowserRouter>
    </IonApp>
  );
};

export default App;
