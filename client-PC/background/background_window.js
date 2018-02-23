import {
  BrowserWindow,
} from 'electron';

import url from 'url';
import path from 'path';

function createBackgroundWindow() {
  const backgroundWindow = new BrowserWindow({
    show: false,
    nodeIntegrationInWorker: true,
  });

  // Load html into window
  backgroundWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/background/index.html'),
    protocol: 'file:',
    slashes: true,
  }));
  return backgroundWindow;
}

export default createBackgroundWindow;
