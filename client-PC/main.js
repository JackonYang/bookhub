const electron = require('electron');
const url = require('url');
const path = require('path');

const { app, BrowserWindow, Menu, ipcMain } = electron;

let mainWindow;

let addWindow;
let preferencesWindow;

// Listen for app to be ready
app.on('ready', function () {

  var electronScreen = electron.screen;
  var size = electronScreen.getPrimaryDisplay().workAreaSize;

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
  mainWindow.on('closed', function () {
    app.quit();
  })

  // build menu from template
  const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
  Menu.setApplicationMenu(mainMenu);
});

// handle create addWindow
function createAddWindows() {
  var electronScreen = electron.screen;
  var size = electronScreen.getPrimaryDisplay().workAreaSize;

  addWindow = new BrowserWindow({
    // width: size.width,
    // height: size.height,
    width: 500,
    height: 400,
    title: 'Add Books'
  });

  addWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/add-books',
    slashes: false,
  }));
  // Garbage collection handle
  addWindow.on('close', function () {
    addWindow = null;
  })
}

// handle create settingsWindow
function createPreferencesWindows() {
  var electronScreen = electron.screen;
  var size = electronScreen.getPrimaryDisplay().workAreaSize;

  addWindow = new BrowserWindow({
    width: size.width,
    height: size.height,
    title: 'Preferences'
  });

  addWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'public/index.html'),
    protocol: 'file:',
    hash: '#/preferences',
    slashes: false,
  }));
  // Garbage collection handle
  addWindow.on('close', function () {
    addWindow = null;
  })
}

const mainMenuTemplate = [
  {
    label: 'File',
    submenu: [
      {
        label: 'Add Books',
        accelerator: process.platform == 'darwin' ? 'Command+N' : 'Ctrl+N',
        click(){
          createAddWindows();
        }
      },
      {
        label: 'Preferences',
        accelerator: process.platform == 'darwin' ? 'Command+,' : 'Ctrl+,',
        click(){
          createPreferencesWindows();
        }
      },
      {
        label: 'Close Current Window',
        accelerator: process.platform == 'darwin' ? 'Command+W' : 'Ctrl+W',
        click(item, focusedWindow) {
          focusedWindow.close();
        }
      },
      {
        label: 'Quit',
        accelerator: process.platform == 'darwin' ? 'Command+Q' : 'Ctrl+Q',
        click() {
          app.quit();
        }
      }
    ]
  }
]

// if Mac, add empty object to menu
if (process.platform == 'darwin') {
  mainMenuTemplate.unshift({})
}

// Add developer tools if not in prod
if (process.env.NODE_ENV !== 'production') {
  mainMenuTemplate.push({
    label: 'Developer Tools',
    submenu: [
      {
        label: 'Toggle DevTools',
        accelerator: process.platform == 'darwin' ? 'Command+I' : 'Ctrl+I',
        click(item, focusedWindow) {
          focusedWindow.toggleDevTools();
        }
      },
      {
        role: 'reload'
      }
    ]
  })
}
