import axios from 'axios';


/** return the user id from the access token stored in local storage; otherwise 0 */
export const getstudentId = () => {
    let id = 0;

    const token = localStorage.getItem('access_token');
    
    if (token) {
        // get the payload
        const [,payload,] = token.split('.');
        // decode base64 encoded string
        const decodedPayload = window.atob(payload);
        // convert from JSON
        const payloadData = JSON.parse(decodedPayload);

        id = payloadData['user_id']; 
    }

    return id;
}


/** Check for an existing token on first load. */
const token = localStorage.getItem('access_token')
    ? `Bearer ${localStorage.getItem('access_token')}`
    : null;


/** Creates a new instance of axios and sets config defaults. */
export const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/',
    timeout: 5000,
    headers: {
        Authorization: token,
        'Content-Type': 'application/json',
        accept: 'application/json',
    },
});

/**
 * Intercept each response from the server to check if the access token has expired.
 * On expiry, it attempts to fetch a new access token if a valid refresh token exists; otherwise, redirects to login page.
 * The new access token will be stored and the original request will be re-sent with the new access token in the auth header.
 * All invalid tokens will be removed from local storage and auth header.
 * 
 * All other errors will be passed onto the original requester.
 */
axiosInstance.interceptors.response.use(
    (response) => {
        // status code 2xx; pass the response to the requester
        return response;
    },
    (error) => {
        // no response from the server
        if (error.response === 'undefined') {
            return Promise.reject(error);
        }
        const originalRequestConfig = error.config;

        // tried but failed to authenticate
        if (error.response.status === 401 && originalRequestConfig.url === 'auth/token/') {
            return Promise.reject(error);
        }
        // tried but failed to retrieve a new access token with a refresh token
        if (error.response.status === 401 && originalRequestConfig.url === 'auth/token/refresh/') {
            return Promise.reject(error);
        }
        // on failure to authenticate, attempt to get a new access token with a refresh token or redirect to login
        if (error.response.status === 401) {
            // remove invalid access token
            localStorage.removeItem('access_token');
            axiosInstance.defaults.headers['Authorization'] = null;
            originalRequestConfig.headers['Authorization'] = null;

            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                return axiosInstance
                    .post('auth/token/refresh/', { refresh: refreshToken })
                    .then((res) => {
                        // retrieve new access token
                        const newAccessToken = res.data.access;

                        // store new access token
                        localStorage.setItem('access_token', newAccessToken);
                        axiosInstance.defaults.headers['Authorization'] = `Bearer ${newAccessToken}`;
                        originalRequestConfig.headers['Authorization'] = `Bearer ${newAccessToken}`;

                        // no need to re-post the original request if it was regarding token verification
                        if (originalRequestConfig.url === 'auth/token/verify/') {
                            return res;
                        }
                        // make the original request with the updated access token in the Authorization header
                        return axiosInstance(originalRequestConfig);
                    })
                    .catch((err) => {
                        // remove invalid refresh token
                        localStorage.removeItem('refresh_token');

                        // redirect as the refresh token was not valid
                        window.location.href = '/login/';
                    });
            }
            // redirect as there is no valid refresh token
            window.location.href = '/login/';
        }
        // pass all other errors to be handled by the requester
        return Promise.reject(error);
    }
);