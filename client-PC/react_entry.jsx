import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter as Router, Route } from 'react-router-dom';
// import { HashRouter as Router, Route, Link } from 'react-router-dom';

import BookAdd from './src/containers/book-add/index';
import BookSearch from './src/containers/book-search/index';
import Preferences from './src/containers/preferences/index';

const routes = [
  {
    path: '/',
    exact: true,
    sidebar: () => <div>图书搜索</div>,
    main: BookSearch,
  },
  {
    path: '/add-books',
    sidebar: () => <div>添加书籍</div>,
    main: BookAdd,
  },
  {
    path: '/preferences',
    sidebar: () => <div>设置</div>,
    main: Preferences,
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
      <div>
        {routes.map(route =>
          <Route key={route.path} exact={route.exact} path={route.path} component={route.main} />)
        }
      </div>
    </Router>);
}

ReactDOM.render(
  <Index />,
  document.getElementById('content'),
);

