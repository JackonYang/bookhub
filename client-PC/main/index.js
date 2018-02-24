import {
  app,
  Menu,
  ipcMain,
} from 'electron';
import url from 'url';
import path from 'path';

import createBackgroundWindow from 'background_window';

import createMainWindow from './main_window';
import createMainMenu from './main_menu';


let mainWindow;
let backgroundWindow;

function switchToSearchBooks() {
  mainWindow.webContents.send('windown:location:change', '#/');
}

function switchToAddBooks() {
  mainWindow.webContents.send('windown:location:change', '#/add-books');
}

function switchToPreferences() {
  mainWindow.webContents.send('windown:location:change', '#/preferences');
}

function switchToRecentlyReads() {
  mainWindow.webContents.send('windown:location:change', '#/recently-read');
}

// Listen for app to be ready
app.on('ready', () => {
  mainWindow = createMainWindow();

  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/recently-read',
    slashes: false,
  }));

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
    switchToRecentlyReads,
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

ipcMain.on('scan:file:found', (e, fileMetaInfo) => {
  mainWindow.webContents.send('scan:file:found', fileMetaInfo);
});
