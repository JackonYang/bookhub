import React from "react";
import ReactDOM from 'react-dom';

import { HashRouter as Router, Route, Link } from 'react-router-dom'


const routes = [
    {
        path: '/',
        exact: true,
        sidebar: () => <div>图书搜索</div>,
        main: () => <h2>A List Of Books</h2>
    },
    {
        path: '/add-books',
        sidebar: () => <div>添加书籍</div>,
        main: () => <h2>Adding New Books</h2>
    },
    {
        path: '/settings',
        sidebar: () => <div>设置</div>,
        main: () => <h2>a bunch of settings</h2>
    }
]

class Sidebar extends React.Component {
    render() {
        return (
            <ul>
                {routes.map((route, index) => {
                    return <li key={index}>
                        <Link to={route.path}> {route.sidebar()} </Link>
                    </li>
                })}

            </ul>
        );
    }
}


class Index extends React.Component {
    render() {
        return (
            <Router>
                <div>
                    <Sidebar />

                    {routes.map((route, index) => {
                        return <Route key={index} exact={route.exact} path={route.path} render={() => route.main()} />
                    })}

                </div>
            </Router>
        );
    }
}

ReactDOM.render(
    <Index />,
    document.getElementById('content')
);
