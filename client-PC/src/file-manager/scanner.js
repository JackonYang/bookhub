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

function scanPath(rootPath, dispatchMsg) {
  if (!fs.existsSync(rootPath)) {
    return 0;
  }

  const stat = fs.lstatSync(rootPath);

  if (stat.isDirectory()) {
    let cntAdded = 0;
    const tarPath = fs.readdirSync(rootPath).filter(ele => !isIgnoreDir(ele));

    // count scaned files and log

    tarPath.forEach(ele => {
      // ignore hidden if configured
      cntAdded += scanPath(path.join(rootPath, ele), dispatchMsg); // recurse
    });
    return cntAdded;
  }

  // else -> file
  const ext = path.extname(rootPath);
  if (!targetPtn.includes(ext)) {
    return 0;
  }

  const basename = path.basename(rootPath, ext);

  const metaInfo = {
    rawname: basename,
    path: path.dirname(rootPath),
    ext,
    sizeBytes: stat.size,
    sizeReadable: filesize(stat.size),
    md5: md5File.sync(rootPath),
  };
  dispatchMsg('scan:book:found', metaInfo);
  return 1;
}

// scanPath('/Users/');

export default scanPath;
