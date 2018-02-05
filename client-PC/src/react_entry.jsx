import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router, Route } from 'react-router-dom';
import { createStore } from 'redux';

// import { HashRouter as Router, Route, Link } from 'react-router-dom';

import BookAdd from './containers/book-add/index';
import BookSearch from './containers/book-search/index';
import Preferences from './containers/preferences/index';
/* eslint-disable import/extensions */
import './common/reset.css?raw';
import styles from './entry.scss';

import rootReducer from './reducers';

const store = createStore(rootReducer);

const routes = [
  {
    path: '/',
    exact: true,
    sidebar: () => <div>图书搜索</div>,
    main: props => <BookSearch {...props} />,
  },
  {
    path: '/add-books',
    sidebar: () => <div>添加书籍</div>,
    main: props => <BookAdd {...props} />,
  },
  {
    path: '/preferences',
    sidebar: () => <div>设置</div>,
    main: props => <Preferences {...props} />,
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

function Index() {
  return (
    <Router>
      <div className={styles.wrap}>
        {routes.map(route =>
          <Route key={route.path} exact={route.exact} path={route.path} render={route.main} />)
        }
      </div>
    </Router>);
}

function render() {
  ReactDOM.render(
    <Index store={store} />,
    document.getElementById('app'),
  );
}

store.subscribe(render);

render();
