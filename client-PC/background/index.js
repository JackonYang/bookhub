import scanPath from '../renderer/file-manager/scanner';

const electron = require('electron');

const { ipcRenderer } = electron;

ipcRenderer.send('bg:started', 'background started!');

ipcRenderer.on('book:scan', (e, targetPath) => {
  scanPath(targetPath, (msgKey, payload) => {
    ipcRenderer.send(msgKey, payload);
  });
});
