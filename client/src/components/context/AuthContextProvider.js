import React, { useState, useEffect } from 'react';
import { axiosInstance, getstudentId } from '../../utilities/axios';


/** Create a context with initial values */
export const AuthContext = React.createContext({
    isAuthenticated: false,
    studentId: 0,
    logIn: () => {},
    logOut: () => {},
});


/** Provides authentication services for the entire site. */
const AuthContextProvider = props => {
    const [isAuthenticated, setIsAuthenticated] = useState(
        localStorage.getItem('access_token') !== null
    );
    const [studentId, setstudentId] = useState(getstudentId());

    /** if there is a saved access token on the first load, it will be validated by the server */
    useEffect(() => {
        const accessToken = localStorage.getItem('access_token');

        if (accessToken) {
            // 401 errors are handled by axios.js
            axiosInstance.post('auth/token/verify/', {'token': accessToken})
                .catch(error => {
                    console.log(error.response);
                });
        }
    }, []);

    /**
     * Event handler for logging the user in.
     * Stores provided access and refresh tokens in local storage,
     * updates authorization header, and updates authentication status and id.
     */
    const handleLogin = (accessToken, refreshToken) => {
        // save the access and request tokens in local storage
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        // update authorization header with the new access token
        axiosInstance.defaults.headers['Authorization'] = `Bearer ${accessToken}`;
        setstudentId(getstudentId());
        setIsAuthenticated(true);
    };

    /**
     * Event handler for logging the user out.
     * Removes tokens from local storage and Authorization header and updates user authentication status and id.
     */
    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        axiosInstance.defaults.headers['Authorization'] = null;
        setstudentId(0);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated: isAuthenticated,
                studentId: studentId,
                logIn: handleLogin,
                logOut: handleLogout,
            }}
        >
            {props.children}
        </AuthContext.Provider>
    );
};

export default AuthContextProvider;