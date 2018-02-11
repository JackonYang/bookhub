import { ipcRenderer } from 'electron';

import scanPath from './file-scanner';

// ipcRenderer.send('bg:started', 'background started!');

ipcRenderer.on('book:scan', (e, targetPath) => {
  scanPath(targetPath, (msgKey, payload) => {
    ipcRenderer.send(msgKey, payload);
  });
});
