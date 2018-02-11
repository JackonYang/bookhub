const electron = require('electron');
const url = require('url');
const path = require('path');

import createMainWindow from './main_window'
import createMainMenu from './main_menu'

import createBackgroundWindow from '../background/background_window'

const {
  app,
  BrowserWindow,
  Menu,
  ipcMain,
} = electron;

let mainWindow;
let backgroundWindow;

let addWindow;
let preferencesWindow;

// Listen for app to be ready
app.on('ready', () => {
  mainWindow = createMainWindow();

  // Quit app when closed
  mainWindow.on('closed', () => {
    app.quit();
  });

  backgroundWindow = createBackgroundWindow();

  // build menu from template
  Menu.setApplicationMenu(createMainMenu(createAddWindows, createPreferencesWindows));
});

// handle create addWindow
function createAddWindows() {
  // const electronScreen = electron.screen;
  // const size = electronScreen.getPrimaryDisplay().workAreaSize;

  addWindow = new BrowserWindow({
    width: 1600,
    height: 900,
    title: 'Add Books',
  });

  addWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/add-books',
    slashes: false,
  }));
  // Garbage collection handle
  addWindow.on('close', () => {
    addWindow = null;
  });
}

// handle create settingsWindow
function createPreferencesWindows() {
  // const electronScreen = electron.screen;
  // const size = electronScreen.getPrimaryDisplay().workAreaSize;

  preferencesWindow = new BrowserWindow({
    width: 1600,
    height: 900,
    title: 'Preferences',
  });

  preferencesWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/preferences',
    slashes: false,
  }));
  // Garbage collection handle
  preferencesWindow.on('close', () => {
    preferencesWindow = null;
  });
}

ipcMain.on('scan:path:change', function (e, path_name) {
  backgroundWindow.webContents.send('book:scan', path_name);
})

ipcMain.on('bg:started', function (e, msg) {
  console.log(msg);
})

ipcMain.on('scan:book:found', function (e, msg) {
  addWindow.webContents.send('scan:book:found', msg);
})
