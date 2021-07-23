import React, { useContext, useState, useEffect } from 'react';
import { useParams, useHistory, useLocation } from 'react-router-dom';
import { Formik } from 'formik';
import * as Yup from 'yup';
/** my components */
import { AuthContext } from '../context/AuthContextProvider';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Images */
import defaultProfileImage from '../../assets/images/default-profile-image.png';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import { MenuItem } from '@material-ui/core';
import Avatar from '@material-ui/core/Avatar';
import Backdrop from '@material-ui/core/Backdrop';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import CircularProgress from '@material-ui/core/CircularProgress';
import Chip from '@material-ui/core/Chip';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import CardActions from '@material-ui/core/CardActions';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
    card: {
        padding: 20,
    },
    profileImage: {
        maxWidth: 300,
        maxHeight: 300,
    },
    profileItem: {
        marginBottom: 15,
    },
    cardAction: {
        paddingTop: 26,
        paddingBottom: 16,
    },
    fieldErrorAlert: {
        textAlign: "center",
        marginTop: 10,
        color: '#f44336',
    },
}));


/** Project invitation validation schema. */
const projectInvitationValidationSchema = Yup.object().shape({
    project: Yup.string()
        .required('You must select a project'),
    project_role: Yup.string()
        .max(40, 'This field must not contain more than 40 characters'),
});


/** Renders a detailed view of a student profile with a given ID. */
const StudentView = (props) => {
    const [isLoading, setIsLoading] = useState(false);
    const [student, setStudent] = useState({});
    const [isAuthenticatedStudent, setIsAuthenticatedStudent] = useState(false);

    const [projectInvitationDialogIsOpen, setProjectInvitationDialogIsOpen] = useState(false);
    const [authStudentProjects, setAuthStudentProjects] = useState([]);

    const authContext = useContext(AuthContext);
    const { id } = useParams();  // we don't know if a student with this ID exists in the database
    const history = useHistory();
    const location = useLocation();
    const classes = useStyles();

    /**
     * Fetch and store a student's profile.
     * Redirects to a 404 page if the user doesn't exist.
     */
    useEffect(() => {
        setIsLoading(true);
        axiosInstance
            .get(`api/accounts/${id}/`)
            .then(response => {
                setIsLoading(false);
                setStudent(response.data);

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

    /** handle edit profile button click */
    const handleEditProfile = () => history.push(`/students/${authContext.studentId}/edit`);

    /** Opens invitation dialog and fetches the auth student's owned projects. */
    const handleOpenProjectInvitationDialog = () => {
        setProjectInvitationDialogIsOpen(true);

        // get the authenticated student's owned projects
        axiosInstance
            .get('api/projects?relation=owned')
            .then(response => {
                setAuthStudentProjects(response.data);
            })
            .catch(error => {
                console.log(error);
            });
    };

    const handleCloseProjectInvitationDialog = () => {
        setProjectInvitationDialogIsOpen(false);
    };

    /**
     * Handles invitation submission.
     * Updates error messages when a code 400 is returned by the server.
     */
    const handleSendInvitation = async (values, actions) => {
        axiosInstance
        .post(`api/requests/`, {
            "requestee": student.id,
            "project": values.project,
            "role": values.project_role
        })
        .then(response => {
            handleCloseProjectInvitationDialog();
        })
        .catch(error => {
            if (error.response.status === 400) {
                actions.setFieldError('project', error.response.data.project);
                actions.setFieldError('project_role', error.response.data.role);
                actions.setFieldError('all', error.response.data.non_field_errors);
            } else {
                console.log(error);
            }
        });
    };

    /** Returns a dialog with a form to send the student an invitation to join a project. */
    const getProjectInvitationDialog = () => {
        return (
            <Dialog open={projectInvitationDialogIsOpen} onClose={handleCloseProjectInvitationDialog} fullWidth>
                <Formik
                    initialValues={{
                        project_role: '',
                        project: '',
                    }}
                    validationSchema={projectInvitationValidationSchema}
                    onSubmit={handleSendInvitation}
                >
                    {({values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors}) => (
                        <form noValidate>
                            <DialogContent>
                                <DialogContentText>
                                    Send the student an invitation to join your project team.
                                </DialogContentText>
                                <TextField
                                    required
                                    label="Their Role"
                                    name="project_role"
                                    data-cy="project_role"
                                    variant="outlined"
                                    margin="dense"
                                    fullWidth
                                    value={values.project_role}
                                    onBlur={handleBlur}
                                    onChange={handleChange}
                                    error={touched.project_role && Boolean(errors.project_role)}
                                    helperText={touched.project_role && errors.project_role}
                                />
                                <TextField
                                    select
                                    required
                                    label="Project"
                                    name="project"
                                    data-cy="project"
                                    variant="outlined"
                                    margin="dense"
                                    fullWidth
                                    value={values.project}
                                    onChange={handleChange}
                                    onBlur={handleBlur}
                                    error={touched.project && Boolean(errors.project)}
                                    helperText={touched.project && errors.project}
                                >
                                    {authStudentProjects.map(project => (
                                        <MenuItem key={project.id} value={project.id} data-cy={project.id}>
                                            {project.title}
                                        </MenuItem>
                                    ))}
                                </TextField>
                                <div>
                                    {
                                        errors['all'] &&
                                        (<Typography component="p" variant="body2" className={classes.fieldErrorAlert}>
                                            {errors['all']}
                                        </Typography>)
                                    }
                                </div>
                            </DialogContent>
                            <DialogActions>
                                <Button onClick={handleCloseProjectInvitationDialog} data-cy="cancel-invitation-button">
                                    Cancel
                                </Button>
                                <Button onClick={handleSubmit} color="primary" type="submit" data-cy="send-invitation-button" disabled={isSubmitting}>
                                    Send
                                </Button>
                            </DialogActions>
                        </form>
                    )}
                </Formik>
            </Dialog>
        )
    };

    /** Returns a student profile as a card element if there is one stored. */
    const getStudentProfile = () => {
        if (Object.keys(student).length > 0) {
            return (
                <Card className={classes.card}>
                    <CardContent>
                    <Grid container direction="row" spacing={2} justify="flex-start" alignItems="flex-start">
                        <Grid item>
                            <CardMedia
                                component="img"
                                alt="Default Profile"
                                image={defaultProfileImage}
                                title="Default Profile"
                                className={classes.profileImage}
                            />
                        </Grid>
                        <Grid item>
                            <Typography variant="h3" component="h1" data-cy="full-name" gutterBottom>
                                {student.first_name && student.last_name && `${student.first_name} ${student.last_name}`}
                            </Typography>
                            <div className={classes.profileItem}>
                                <Typography variant="h6" component="h3" color="primary" data-cy="username-label">
                                    Username
                                </Typography>
                                <Typography variant="body1" component="p" data-cy="username">
                                    {student.username}
                                </Typography>
                            </div>
                            <div className={classes.profileItem}>
                                <Typography variant="h6" component="h3" color="primary">
                                    Email
                                </Typography>
                                <Typography variant="body1" component="p" data-cy="email">
                                    {student.email}
                                </Typography>
                            </div>
                            <div className={classes.profileItem}>
                                <Typography variant="h6" component="h3" color="primary">
                                    Programme
                                </Typography>
                                <Typography variant="body1" component="p" data-cy="programme">
                                    {student.profile.programme}
                                </Typography>
                            </div>
                        </Grid>
                    </Grid>
                    </CardContent>
                    <CardContent>
                        <Typography variant="h5" component="h2" gutterBottom>
                            About
                        </Typography>
                        <Typography variant="body1" component="p" data-cy="about">
                            {student.profile.about}
                        </Typography>
                    </CardContent>
                    <CardContent>
                        <Typography variant="h5" component="h2" gutterBottom>
                            Roles
                        </Typography>
                        <Grid container direction="row" spacing={2}>
                            {student.profile.roles.map((role, index) => {
                                return (
                                    <Grid item key={index}>
                                        <Chip
                                            size="medium"
                                            label={role}
                                            data-cy={`role-${index}`}
                                            color="primary"
                                            variant="outlined"
                                            avatar={<Avatar>R</Avatar>}
                                        />
                                    </Grid>
                                )
                            })}
                        </Grid>
                    </CardContent>
                    <CardActions className={classes.cardAction}>
                        {
                            isAuthenticatedStudent &&
                            <Button size="medium" variant="contained" color="primary" data-cy="edit-profile-button" onClick={handleEditProfile}>Edit Profile</Button>
                        }
                        {
                            isAuthenticatedStudent === false &&
                            <>
                                <Button size="medium" variant="contained" color="primary" data-cy="request-join-project-button" onClick={handleOpenProjectInvitationDialog}>Send Project Invitation</Button>
                                {getProjectInvitationDialog()}
                            </>
                        }
                    </CardActions>
                </Card>
            );
        }
        return null;
    };

    return (
        <>
            {getStudentProfile()}
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </>
    );
};

export default StudentView;