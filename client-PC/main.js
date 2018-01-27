const electron = require('electron');
const url = require('url');
const path = require('path');

const { app, BrowserWindow, Menu, ipcMain } = electron;

let mainWindow;
let addBooksWindow;

// Listen for appp to be ready
app.on('ready', function () {
    mainWindow = new BrowserWindow({});

    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'mainWindow.html'),
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

// handle AddBooks Window
function craeteAddBooksWindows() {
    addBooksWindow = new BrowserWindow({
        width: 600,
        height: 400,
        title: 'Add Books to Repo'
    });

    addBooksWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'addBooksWindow.html'),
        protocol: 'file:',
        slashes: true,
    }));
    // Garbage collection handle
    addBooksWindow.on('close', function () {
        addBooksWindow = null;
    })
}

// catch folder scan
ipcMain.on('folder:to_scan', function (e, folder) {
    book_title = path.join(folder, 'hello-world.pdf'),
    addBooksWindow.webContents.send('book:found', book_title);
})

// Create menu template
const mainMenuTemplate = [
    {
        label: 'File',
        submenu: [
            {
                label: 'Add Books',
                click() {
                    craeteAddBooksWindows();
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
