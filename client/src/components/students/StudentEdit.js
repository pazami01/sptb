import React, { useContext, useState, useEffect } from 'react';
import { useParams, useHistory, useLocation } from 'react-router-dom';
import { Formik, FieldArray, Field, getIn } from 'formik';
import * as Yup from 'yup';
/** my components */
import { AuthContext } from '../context/AuthContextProvider';
import Forbidden403 from '../errors/Forbidden403';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import Backdrop from '@material-ui/core/Backdrop';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
    card: {
        padding: 20,
    },
    errorText: {
        fontSize: '0.75rem',
        lineHeight: '1.66',
        color: '#f44336',
    },
    miniButton: {
        marginTop: 5,
        marginBottom: 10,
    },
    submitButton: {
        marginTop: 10,
        marginRight: 10,
    },
    cancelButton: {
        marginTop: 10,
    },
}));

/** Profile validation schema. */
const profileValidationSchema = Yup.object().shape({
    programme: Yup.string()
        .max(150, 'This field must not contain more than 150 characters'),
    about: Yup.string()
        .max(1000, 'This field must not contain more than 1000 characters'),
    roles: Yup.array()
        .of(Yup.string().max(40, 'This field must not contain more than 40 characters')),
});


/** Renders a form for editing a student's profile with a given ID. */
const StudentEdit = (props) => {
    const [isLoading, setIsLoading] = useState(false);
    const [studentProfile, setStudentProfile] = useState({});
    const [isAuthenticatedStudent, setIsAuthenticatedStudent] = useState(false);

    const authContext = useContext(AuthContext);
    const classes = useStyles();
    const { id } = useParams();  // we don't know if a student with this ID exists in the database
    const history = useHistory();
    const location = useLocation();

    /**
     * Fetch and store a student's modifiable profile elements.
     * In addition, it stores whether the student profile belongs to the authenticated user.
     * Redirects to a 404 page if the user doesn't exist.
     */
    useEffect(() => {
        setIsLoading(true);
        axiosInstance
            .get(`api/accounts/${id}/`)
            .then(response => {
                setIsLoading(false);
                setStudentProfile(response.data.profile);  // only save the editable elements

                // the authenticated student is looking at their own profile
                if (response.data.id === authContext.studentId) {
                    setIsAuthenticatedStudent(true);
                }
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error);
                
                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    }, []);

    /**
     * Handles the submission for updating a student's profile.
     * Redirects to the student profile view page on success.
     * Updates error messages on fields if a 400 code is returned.
     */
    const handleProfileUpdate = async (values, actions) => {
        axiosInstance
            .patch(`api/accounts/${id}/`, {
                profile: {
                    programme: values.programme,
                    about: values.about,
                    roles: values.roles
                }
            })
            .then(response => {
                console.log('Profile updated');
                console.log(response.data);
                history.push(`/students/${id}`);  // go back to the profile view page
            })
            .catch(error => {
                if (error.response.status === 400) {
                    const profile = error.response.data.profile;
                    actions.setFieldError('programme', profile.programme);
                    actions.setFieldError('about', profile.about);

                    if (profile.roles) {
                        for (const [key, value] of Object.entries(profile.roles)) {
                            actions.setFieldError(`roles.${key}`, value);
                        }
                    }
                }
            });
    };

    /** Redirects to the student profile view page  */
    const handleCancelProfileUpdate = () => history.push(`/students/${id}`);

    /**
     * Custom error message for fields for use in array fields
     * This code is taken from https://formik.org/docs/api/fieldarray#fieldarray-validation-gotchas
     */
    const ErrorMessage = ({ name }) => (
        <Field name={name}>
            {({ form }) => {
                const error = getIn(form.errors, name);
                const touch = getIn(form.touched, name);

                return touch && error ? <p className={classes.errorText}>{error}</p> : null;
            }}
        </Field>
    )

    /**
     * Returns form for editing a student's profile.
     * Code for FieldArray is based on https://formik.org/docs/examples/field-arrays
     */
    const getStudentProfileForm = () => {
        if (Object.keys(studentProfile).length > 0) {
            return (
                <Formik
                    initialValues={{
                        programme: studentProfile.programme,
                        about: studentProfile.about,
                        roles: [...studentProfile.roles],
                    }}
                    validationSchema={profileValidationSchema}
                    onSubmit={handleProfileUpdate}
                >
                    {({ values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors }) => (
                        <form className={classes.form} noValidate>
                            <TextField
                                label="Programme"
                                type="text"
                                variant="outlined"
                                className={classes.textInputField}
                                data-cy="programme"
                                fullWidth
                                margin="normal"
                                name="programme"
                                id="programme"
                                value={values.programme}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                error={touched.programme && Boolean(errors.programme)}
                                helperText={touched.programme && errors.programme}
                            />
                            <TextField
                                multiline
                                rows={7}
                                label="About"
                                type="text"
                                variant="outlined"
                                className={classes.textAreaField}
                                data-cy="about"
                                fullWidth
                                margin="normal"
                                name="about"
                                id="about"
                                value={values.about}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                error={touched.about && Boolean(errors.about)}
                                helperText={touched.about && errors.about}
                            />
                            <FieldArray name="roles">
                                {({ form, remove, push }) => (
                                    <div>
                                        {
                                            values.roles.length > 0 &&
                                            values.roles.map((role, index) => (
                                                <div key={index}>
                                                    <div>
                                                        <TextField
                                                            type="text"
                                                            label={`Role ${index + 1}`}
                                                            data-cy={`role-${index}`}
                                                            name={`roles.${index}`}
                                                            fullWidth
                                                            margin="normal"
                                                            value={role}
                                                            onChange={ form.handleChange }
                                                            onBlur={form.handleBlur}
                                                        />
                                                    </div>
                                                    <div>
                                                        <ErrorMessage
                                                            name={`roles.${index}`}
                                                        />
                                                    </div>
                                                    <div>
                                                        <Button
                                                            variant="outlined"
                                                            className={classes.miniButton}
                                                            data-cy={`remove-role-${index}-button`}
                                                            color="secondary"
                                                            type="button"
                                                            size="small"
                                                            onClick={() => remove(index)}
                                                        >
                                                            Remove
                                                        </Button>
                                                    </div>
                                                </div>
                                            ))
                                        }
                                        {
                                            values.roles.length < 3 &&
                                            <Button
                                                variant="outlined"
                                                className={classes.miniButton}
                                                data-cy="add-role-button"
                                                color="secondary"
                                                type="button"
                                                size="small"
                                                onClick={() => push('')}
                                            >
                                                Add New Role
                                            </Button>
                                        }
                                    </div>
                                )}
                            </FieldArray>
                            <div>
                                {errors['all'] &&
                                (<Typography component="p" variant="body2" className={classes.fieldErrorAlert}>
                                    {errors['all']}
                                </Typography>)}
                            </div>

                            <Button
                                variant="contained"
                                className={classes.submitButton}
                                data-cy="update-profile-button"
                                color="primary"
                                type="submit"
                                onClick={handleSubmit}
                                disabled={isSubmitting}
                            >
                                Update
                            </Button>
                            <Button
                                variant="contained"
                                className={classes.cancelButton}
                                data-cy="cancel-update-profile-button"
                                type="button"
                                onClick={handleCancelProfileUpdate}
                            >
                                Cancel
                            </Button>
                        </form>
                    )}
                </Formik>
            );
        }
        return null;
    };

    return (
        <>
            {
                isLoading ? null : 
                isAuthenticatedStudent ? (
                    <Card className={classes.card}>
                        <CardContent>
                            <Typography variant="h3" component="h1" gutterBottom>
                                Edit Profile
                            </Typography>
                            {getStudentProfileForm()}
                        </CardContent>
                    </Card>
                ) : <Forbidden403 />
            }
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </>
    );
};

export default StudentEdit;