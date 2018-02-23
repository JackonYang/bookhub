import {
  Menu,
  app,
} from 'electron';

function createMainMenu(
  switchToAddBooks,
  switchToPreferences,
  switchToSearchBooks,
) {
  const mainMenuTemplate = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Add Books',
          accelerator: process.platform === 'darwin' ? 'Command+N' : 'Ctrl+N',
          click() {
            switchToAddBooks();
          },
        },
        {
          label: 'Search Books',
          accelerator: process.platform === 'darwin' ? 'Command+H' : 'Ctrl+H',
          click() {
            switchToSearchBooks();
          },
        },
        {
          label: 'Preferences',
          accelerator: process.platform === 'darwin' ? 'Command+,' : 'Ctrl+,',
          click() {
            switchToPreferences();
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

  return Menu.buildFromTemplate(mainMenuTemplate);
}

export default createMainMenu;
