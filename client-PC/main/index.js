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

ipcMain.on('scan:path:change', (e, pathName) => {
  backgroundWindow.webContents.send('book:scan', pathName);
});

ipcMain.on('bg:started', (e, msg) => {
  console.log(msg);
});

ipcMain.on('scan:book:found', (e, msg) => {
  mainWindow.webContents.send('scan:book:found', msg);
});
