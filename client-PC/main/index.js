import {
  app,
  Menu,
  ipcMain,
} from 'electron';
import url from 'url';
import path from 'path';

import createMainWindow from './main_window';
import createMainMenu from './main_menu';

import createBackgroundWindow from '../background/background_window';


let mainWindow;
let backgroundWindow;

function switchToSearchBooks() {
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/',
    slashes: false,
  }));
}

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
  switchToSearchBooks();

  // Quit app when closed
  mainWindow.on('closed', () => {
    app.quit();
  });

  backgroundWindow = createBackgroundWindow();

  // build menu from template
  Menu.setApplicationMenu(createMainMenu(
    switchToAddBooks,
    switchToPreferences,
    switchToSearchBooks,
  ));
});

// ipcMain.on('bg:started', (e, msg) => {
//   console.log(msg);
// });

ipcMain.on('scan:task:new', (e, targetPath) => {
  backgroundWindow.webContents.send('bg:scan:task:new', targetPath);
});

ipcMain.on('scan:heartbeat', (e, msg) => {
  console.log(msg);
});

ipcMain.on('scan:error', (e, msg) => {
  console.log(msg);
});

ipcMain.on('scan:file:found', (e, fileInfo) => {
  mainWindow.webContents.send('scan:file:found', fileInfo);
});
