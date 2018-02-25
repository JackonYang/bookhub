import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router, Route } from 'react-router-dom';

import { createStore } from 'redux';
import { Provider } from 'react-redux';
// import PropTypes from 'prop-types';

import jsonfile from 'jsonfile';

import BookAdd from 'containers/book-add/index';
import BookSearch from 'containers/book-search/index';
import Preferences from 'containers/preferences/index';
import RecentlyRead from 'containers/recently-read/index';

/* eslint-disable import/extensions */
import 'common/reset.css?raw';
import styles from 'entry.scss';

import rootReducer from 'reducers';

const { ipcRenderer } = window.require('electron');

const dbFile = 'bookhub-metainfo.db';

const store = createStore(rootReducer);

const routes = [
  {
    path: '/',
    exact: true,
    sidebar: () => <div>Search Books</div>,
    main: BookSearch,
  },
  {
    path: '/add-books',
    sidebar: () => <div>Add Books</div>,
    main: BookAdd,
  },
  {
    path: '/preferences',
    sidebar: () => <div>Preferences</div>,
    main: Preferences,
  },
  {
    path: '/recently-read',
    sidebar: () => <div>Recently Read</div>,
    main: RecentlyRead,
  },
];

// class Navbar extends React.Component {
//   render() {
//     return (
//       <ul>
//         {routes.map((route, index) => {
//           return <li key={index}>
//             <Link to={route.path}> {route.sidebar()} </Link>
//           </li>
//         })}
//       </ul>
//     );
//   }
// }

class Index extends React.Component {
  componentDidMount() {
    ipcRenderer.on('windown:location:change', (e, newLocation) => {
      window.location.assign(newLocation);
    });
    ipcRenderer.on('windown:close:dump', () => {
      jsonfile.writeFileSync(dbFile, store.getState());
    });
  }
  render() {
    return (
      <Router>
        <div className={styles.wrap}>
          {routes.map(route => (
            <Route
              key={route.path}
              exact={route.exact}
              path={route.path}
              render={() => <route.main />}
            />))}
        </div>
      </Router>
    );
  }
}

function render() {
  ReactDOM.render(
    <Provider store={store}>
      <Index />
    </Provider>,
    document.getElementById('app'),
  );
}

store.subscribe(render);

render();
