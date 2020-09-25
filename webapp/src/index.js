import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import Amplify from 'aws-amplify';
import awsconfig from './aws-exports';
import Analytics from '@aws-amplify/analytics';
import Auth from '@aws-amplify/auth';

Amplify.configure(awsconfig);

const amplifyConfig = {
  Auth: {
    identityPoolId: '<region>:<identitypoolid>',
    region: '<region>'
  }
}
Auth.configure(amplifyConfig);

const analyticsConfig = {
  AWSPinpoint: {
        appId: '<pinpointid>',
        region: '<region>',
        mandatorySignIn: false,
  }
}

Analytics.configure(analyticsConfig)

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

serviceWorker.unregister();
