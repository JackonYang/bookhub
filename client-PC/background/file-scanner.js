const path = require('path');
const fs = require('fs');
const wildcard = require('wildcard');
const filesize = require('filesize');
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
  const ext = path.extname(targetPath);
  if (!targetPtn.includes(ext)) {
    return 0;
  }

  const basename = path.basename(targetPath, ext);

  const metaInfo = {
    rawname: basename,
    path: path.dirname(targetPath),
    ext,
    sizeBytes: stat.size,
    sizeReadable: filesize(stat.size),
    md5: md5File.sync(targetPath),
  };
  dispatchMsg('scan:book:found', metaInfo);
  return 1;
}

// scanPath('/Users/');

export default scanPath;
