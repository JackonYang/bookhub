const electron = require('electron');
const url = require('url');
const path = require('path');

const {
  BrowserWindow,
} = electron;

function createBackgroundWindow() {
  let backgroundWindow = new BrowserWindow({
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
