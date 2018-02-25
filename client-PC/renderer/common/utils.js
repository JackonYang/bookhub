import { execFile } from 'child_process';

function openFile(srcPath) {
  const platformCmd = {
    win32: 'start', // win7 32bit, win7 64bit
    cygwin: 'start', // cygwin
    linux2: 'xdg-open', // ubuntu 12.04 64bit
    darwin: 'open', // Mac
  };
  return () => {
    execFile(platformCmd[process.platform], [srcPath[0]]);
  };
}

export default {
  openFile,
};
