import scanPath from '../renderer/file-manager/scanner'

const electron = require('electron');
const url = require('url');
const path = require('path');

const {
  app,
  BrowserWindow,
  Menu,
  ipcMain,
} = electron;

let mainWindow;

let addWindow;
let preferencesWindow;
let mainMenuTemplate;

// Listen for app to be ready
app.on('ready', () => {
  const electronScreen = electron.screen;
  const size = electronScreen.getPrimaryDisplay().workAreaSize;

  // Create main window
  mainWindow = new BrowserWindow({
    width: size.width,
    height: size.height,
  });

  // Load html into window
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    slashes: true,
  }));
  // Quit app when closed
  mainWindow.on('closed', () => {
    app.quit();
  });

  // build menu from template
  const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
  Menu.setApplicationMenu(mainMenu);
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
  scanPath(path_name,  (msgKey, payload) => {
    addWindow.webContents.send(msgKey, payload);
  });
})

mainMenuTemplate = [
  {
    label: 'File',
    submenu: [
      {
        label: 'Add Books',
        accelerator: process.platform === 'darwin' ? 'Command+N' : 'Ctrl+N',
        click() {
          createAddWindows();
        },
      },
      {
        label: 'Preferences',
        accelerator: process.platform === 'darwin' ? 'Command+,' : 'Ctrl+,',
        click() {
          createPreferencesWindows();
        },
      },
      {
        label: 'Close Current Window',
        accelerator: process.platform === 'darwin' ? 'Command+W' : 'Ctrl+W',
        click(item, focusedWindow) {
          focusedWindow.close();
        },
      },
      {
        label: 'Quit',
        accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
        click() {
          app.quit();
        },
      },
    ],
  },
];

// if Mac, add empty object to menu
if (process.platform === 'darwin') {
  mainMenuTemplate.unshift({});
}

// Add developer tools if not in prod
if (process.env.NODE_ENV !== 'production') {
  mainMenuTemplate.push({
    label: 'Developer Tools',
    submenu: [
      {
        label: 'Toggle DevTools',
        accelerator: process.platform === 'darwin' ? 'Command+I' : 'Ctrl+I',
        click(item, focusedWindow) {
          focusedWindow.toggleDevTools();
        },
      },
      {
        role: 'reload',
      },
    ],
  });
}
