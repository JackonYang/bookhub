const path = require('path');
const fs = require('fs');
const wildcard = require('wildcard');
// const filesize = require('filesize');
const md5File = require('md5-file');


const ignorePaths = [
  '.*',
  'node_modules',
  'Library', // Mac
  'log',
  'logs',
  'video-course',
  'interview',
];

const targetPtn = [
  '.pdf',
];

// let STOP_FLAG = false;

function isIgnoreDir(filePath) {
  return ignorePaths.some(ptn => wildcard(ptn, filePath));
}

function scanPath(targetPath, dispatchMsg) {
  if (!fs.existsSync(targetPath)) {
    dispatchMsg('scan:error', `path not exists. path=${targetPath}`);
    return 0;
  }

  const stat = fs.lstatSync(targetPath);

  if (stat.isDirectory()) {
    dispatchMsg('scan:heartbeat', `scanning ${targetPath}`);

    let cntAdded = 0;
    const subPaths = fs.readdirSync(targetPath).filter(ele => !isIgnoreDir(ele));
    subPaths.forEach(ele => {
      cntAdded += scanPath(path.join(targetPath, ele), dispatchMsg); // recurse
    });
    return cntAdded;
  }

  // else -> file
  // match target rule
  const extname = path.extname(targetPath);
  if (!targetPtn.includes(extname)) {
    return 0;
  }

  const fileInfo = {
    md5: md5File.sync(targetPath),
    srcFullPath: targetPath,
    extname,
    sizeBytes: stat.size,
  };
  dispatchMsg('scan:file:found', fileInfo);
  return 1;
}

// scanPath('/Users/');

export default scanPath;
