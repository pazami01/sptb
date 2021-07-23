import React, { useContext } from 'react';
import { Route, Redirect } from 'react-router-dom';
/** my components */
import { AuthContext } from '../context/AuthContextProvider';



/**
 * A wrapper for the standard 'Route' component that redirects
 * to the login page if the user is not authenticated.
 * This code is taken from: https://reactrouter.com/web/example/auth-workflow
 */
const ProtectedRoute = ({ children, ...rest }) => {
    const authContext = useContext(AuthContext);

    return (
        <Route
            {...rest}

            render={() =>
                authContext.isAuthenticated ? (
                    children
                ) : (
                    <Redirect to='/login' />
                )
            }
        />
    );
};

export default ProtectedRoute;