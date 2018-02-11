const electron = require('electron');
const { ipcRenderer } = electron;

ipcRenderer.send('bg:started', 'background started!');
