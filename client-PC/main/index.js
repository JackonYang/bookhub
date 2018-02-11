import createMainWindow from './main_window';
import createMainMenu from './main_menu';

import createBackgroundWindow from '../background/background_window';

const electron = require('electron');
const url = require('url');
const path = require('path');


const {
  app,
  Menu,
  ipcMain,
} = electron;

let mainWindow;
let backgroundWindow;

function switchToAddBooks() {
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/add-books',
    slashes: false,
  }));
}

function switchToPreferences() {
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/preferences',
    slashes: false,
  }));
}

// Listen for app to be ready
app.on('ready', () => {
  mainWindow = createMainWindow();

  // Quit app when closed
  mainWindow.on('closed', () => {
    app.quit();
  });

  backgroundWindow = createBackgroundWindow();

  // build menu from template
  Menu.setApplicationMenu(createMainMenu(switchToAddBooks, switchToPreferences));
});

ipcMain.on('scan:path:change', (e, pathName) => {
  backgroundWindow.webContents.send('book:scan', pathName);
});

ipcMain.on('bg:started', (e, msg) => {
  console.log(msg);
});

ipcMain.on('scan:book:found', (e, msg) => {
  mainWindow.webContents.send('scan:book:found', msg);
});
