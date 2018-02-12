import { ipcRenderer } from 'electron';

import scanPath from './file-scanner';

// ipcRenderer.send('bg:started', 'background started!');

ipcRenderer.on('bg:scan:task:new', (e, targetPath) => {
  scanPath(targetPath, (msgKey, payload) => {
    // msgKey may be:
    // - scan:file:found
    // - path not exists
    // etc
    ipcRenderer.send(msgKey, payload);
  });
});
