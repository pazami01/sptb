import React, { useContext, useState } from 'react';
import { Formik } from 'formik';
import * as Yup from 'yup';
/** my components */
import { AuthContext } from './context/AuthContextProvider';
/** my utilities */
import { axiosInstance } from '../utilities/axios';
/** Material UI Imports */
import Backdrop from '@material-ui/core/Backdrop';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
	form: {
		marginTop: theme.spacing(1.5),
    },
    textInputField: {
        margin: theme.spacing(1.5, 0),
        width: '100%',
    },
    fieldErrorAlert: {
        color: '#f44336',
    },
	submitButton: {
        margin: theme.spacing(1.5, 0),
        width: '100%',
    },
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
    card: {
        padding: 20,
    },
}));


/** Login form validation schema. */
const loginValidationSchema = Yup.object().shape({
    username: Yup.string()
    .required('This field is required'),
    password: Yup.string()
    .required('This field is required'),
});


/**
 * Renders a login form that logs the user in on successful submission.
 */
const Login = (props) => {
    const classes = useStyles();
    const authContext = useContext(AuthContext);
    const [isLoading, setIsLoading] = useState(false);

    /**
     * Event handler for the login form submission.
     * On successful authentication, the user is logged in.
     * Otherwise, field errors are updated.
     */
    const handleSubmit = async (values, actions) => {
        setIsLoading(true);

        axiosInstance
          .post('auth/token/', { username: values.username, password: values.password })
          .then((response) => {
            setIsLoading(false);
            authContext.logIn(response.data.access, response.data.refresh);
          })
          .catch((error) => {
            setIsLoading(false);
            
            actions.setFieldError('all', error.response.data.detail);
          });
    };

    return (
        <Card className={classes.card}>
            <CardContent>
                <Grid container direction="column" justify="center" alignItems="center" spacing={6}>
                    <Grid item>
                        <Typography component="h1" variant="h3" align="center" gutterBottom>Student Project Team Builder</Typography>
                        <Typography component="p" variant="h6" align="center">
                            Please enter your student credentials to access the application
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography component="h2" variant="h4" align="center" color="primary">Sign In</Typography>

                        <Formik
                            initialValues={{ username: '', password: '' }}
                            validationSchema={loginValidationSchema}
                            onSubmit={handleSubmit}
                        >
                            {({ values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors }) => (
                                <form className={classes.form} noValidate>
                                    <TextField
                                        required
                                        label="Username"
                                        type="text"
                                        variant="outlined"
                                        className={classes.textInputField}
                                        name="username"
                                        id="username"
                                        data-cy="username"
                                        value={values.username}
                                        onChange={handleChange}
                                        onBlur={handleBlur}
                                        error={touched.username && Boolean(errors.username)}
                                        helperText={touched.username && errors.username}
                                    />
                                    <TextField
                                        required
                                        label="Password"
                                        type="password"
                                        variant="outlined"
                                        className={classes.textInputField}
                                        name="password"
                                        id="password"
                                        data-cy="password"
                                        value={values.password}
                                        onChange={handleChange}
                                        onBlur={handleBlur}
                                        error={touched.password && Boolean(errors.password)}
                                        helperText={touched.password && errors.password}
                                    />

                                    <div>
                                        {errors['all'] &&
                                        <Typography component="p" variant="body2" className={classes.fieldErrorAlert}>
                                            {errors['all']}
                                        </Typography>}
                                    </div>
                                    

                                    <Button
                                        variant="contained"
                                        className={classes.submitButton}
                                        data-cy="sign-in"
                                        color="primary"
                                        type="submit"
                                        onClick={handleSubmit}
                                        disabled={isSubmitting}
                                    >
                                        Sign In
                                    </Button>
                                </form>
                            )}
                        </Formik>
                    </Grid>
                </Grid>
            </CardContent>
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </Card>
    );
};

export default Login;
