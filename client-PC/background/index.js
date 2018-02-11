import scanPath from '../renderer/file-manager/scanner';

const electron = require('electron');
const { ipcRenderer } = electron;

ipcRenderer.send('bg:started', 'background started!');

ipcRenderer.on('book:scan', function (e, target_path) {
  scanPath(target_path,  (msgKey, payload) => {
    ipcRenderer.send(msgKey, payload);
  });
});
