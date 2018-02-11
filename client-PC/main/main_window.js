const electron = require('electron');
const url = require('url');
const path = require('path');

const {
  BrowserWindow,
} = electron;

function createMainWindow() {
  const electronScreen = electron.screen;
  const size = electronScreen.getPrimaryDisplay().workAreaSize;

  let mainWindow = new BrowserWindow({
    width: size.width,
    height: size.height,
  });

  // Load html into window
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    slashes: true,
  }));

  return mainWindow;
}

export default createMainWindow;
