# BookHub PC Client

- [UI Design Preview](http://jackon.me/bookhub/)
- [Release Plan](../doc/release-plan)

## Development

the client is built using Electron + React + Redux.

I am new to these stacks, too.
here are tutorial projects that help me learn them:
[https://github.com/JackonYang/tutorial](https://github.com/JackonYang/tutorial)

```bash
npm install
npm start  # you might need to wait several seconds before the page is loaded
```

## Installing and Rebuilding SQLite3

SQLite3 is a native Node.js module so it can't be used directly with Electron without rebuilding it to target Electron.

There are many ways to do that. You can find them from Electron documentation.

First install electron-rebuild:

```bash
npm install --save-dev electron-rebuild
```

Then install sqlite3 module:

```bash
npm install sqlite3 --save
```

Next rebuild sqlite3 for Electron with:

```bash
./node_modules/.bin/electron-rebuild  -f -w sqlite3
```
