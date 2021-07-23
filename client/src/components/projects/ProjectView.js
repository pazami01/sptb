import React, { useState } from 'react';
import { Formik } from 'formik';
import * as Yup from 'yup';
/** my components */
import ProjectMemberDiscussion from './ProjectMemberDiscussion';
import ProjectPublicDiscussion from './ProjectPublicDiscussion';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Images */
import defaultProjectImage from '../../assets/images/default-project-image-medium.png';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
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
    card: {
        padding: 20,
        marginBottom: 20,
    },
    projectImage: {
        maxWidth: 1280,
        maxHeight: "auto",
    },
    projectItem: {
        marginBottom: 15,
    },
    cardAction: {
        paddingTop: 26,
        paddingBottom: 16,
    },
    owner: {
        width: theme.spacing(3),
        height: theme.spacing(3),
        color: "#ffffff",
        backgroundColor: "#F51564",
    },
    member: {
        width: theme.spacing(3),
        height: theme.spacing(3),
        color: "#ffffff",
        backgroundColor: "#303F9F",
    },
    fieldErrorAlert: {
        textAlign: "center",
        marginTop: 10,
        color: '#f44336',
    },
    discussionGrid: {
        minHeight: 500,
    },
    discussionGridItem: {
        flexGrow: 1,
    },
}));


/** Request validation schema. */
const requestValidationSchema = Yup.object().shape({
    role: Yup.string()
        .max(40, 'This field must not contain more than 40 characters'),
});



/** Renders a detailed view of a project with a given ID. */
const ProjectView = (props) => {
    const classes = useStyles();

    const [deleteDialogIsOpen, setDeleteDialogIsOpen] = useState(false);
    const [requestDialogIsOpen, setRequestDialogIsOpen] = useState(false);

    const handleOpenDeleteDialog = () => {
      setDeleteDialogIsOpen(true);
    };
  
    const handleCloseDeleteDialog = () => {
      setDeleteDialogIsOpen(false);
    };

    const handleDelete = () => {
        handleCloseDeleteDialog();
        props.handleDeleteProject();
    };

    const handleOpenRequestDialog = () => {
        setRequestDialogIsOpen(true);
    };

    const handleCloseRequestDialog = () => {
        setRequestDialogIsOpen(false);
    };

    /**
     * Handles submission of a new request
     * Updates error messages on fields if a 400 code is returned. 
     */
    const handleSendRequest = async (values, actions) => {
        axiosInstance
        .post(`api/requests/`, {
            "requestee": props.project.owner,
            "project": props.project.id,
            "role": values.role
        })
        .then(response => {
            handleCloseRequestDialog();
            props.handleRequestSent();
        })
        .catch(error => {
            if (error.response.status === 400) {
                actions.setFieldError('role', error.response.data.role);
                actions.setFieldError('all', error.response.data.non_field_errors);
            } else {
                console.log(error);
            }
        });
    };

    /** Returns a dialog with a form to send a project join request */
    const getRequestDialog = () => {
        return (
            <Dialog open={requestDialogIsOpen} onClose={handleCloseRequestDialog}>
                <Formik
                    initialValues={{role: ''}}
                    validationSchema={requestValidationSchema}
                    onSubmit={handleSendRequest}
                >
                    {({values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors}) => (
                        <form noValidate>
                            <DialogContent>
                                <DialogContentText>
                                    Send a request to join the project team.
                                </DialogContentText>
                                <TextField
                                    required
                                    label="Your Role"
                                    margin="dense"
                                    variant="outlined"
                                    data-cy="requested-role"
                                    name="role"
                                    value={values.role}
                                    onBlur={handleBlur}
                                    onChange={handleChange}
                                    error={touched.role && Boolean(errors.role)}
                                    helperText={touched.role && errors.role}
                                />
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
                                <Button onClick={handleCloseRequestDialog} data-cy="cancel-send-request-button">
                                    Cancel
                                </Button>
                                <Button onClick={handleSubmit} color="primary" type="submit" data-cy="send-request-button" disabled={isSubmitting}>
                                    Send
                                </Button>
                            </DialogActions>
                        </form>
                    )}
                </Formik>
            </Dialog>
        )
    };

    /** Returns a dialog asking for confirmation to delete the project */
    const getDeleteDialog = () => {
        return (
            <Dialog open={deleteDialogIsOpen} onClose={handleCloseDeleteDialog}>
                <DialogContent>
                    Are you sure you want to delete this project?
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDeleteDialog} data-cy="cancel-delete-project-button">
                        Cancel
                    </Button>
                    <Button onClick={handleDelete} color="secondary" data-cy="delete-project-button">
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        )
    };

    return (
        <>
            {
                props.project &&
                (
                    <>
                        <Card className={classes.card}>
                            <CardContent>
                                <CardMedia
                                    component="img"
                                    alt="Default Project"
                                    image={defaultProjectImage}
                                    title="Default Project"
                                    className={classes.projectImage}
                                />
                            </CardContent>
                            <CardContent>
                                <Typography variant="h3" component="h1" data-cy="title">
                                    {props.project.title}
                                </Typography>
                            </CardContent>
                            <CardContent>
                                <Typography variant="h5" component="h2" data-cy="category-label" gutterBottom>
                                    Category
                                </Typography>
                                <Chip
                                    size="small"
                                    label={props.project.category_name}
                                    data-cy="category"
                                    color="secondary"
                                    avatar={<Avatar>C</Avatar>}
                                />
                            </CardContent>
                            <CardContent>
                                <Typography variant="h5" component="h2" data-cy="description-label" gutterBottom>
                                    Description
                                </Typography>
                                <Typography variant="body1" component="p" data-cy="description">
                                    {props.project.description}
                                </Typography>
                            </CardContent>
                            <CardContent>
                                <Typography variant="h5" component="h2" gutterBottom>
                                    Desired Roles
                                </Typography>
                                <Grid container direction="row" spacing={2}>
                                    {props.project.desired_roles.map((role, index) => {
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
                                    <>
                                        {
                                            props.isOwner &&
                                            <>
                                                <Button size="medium" variant="contained" color="primary" data-cy="edit-project-button" onClick={props.handleEditProject}>Edit Project</Button>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="open-delete-project-dialog-button" onClick={handleOpenDeleteDialog}>Delete Project</Button>
                                                {getDeleteDialog()}
                                            </>
                                        }
                                        {
                                            props.isMember && props.isFollower &&
                                            <>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="leave-project-button" onClick={props.handleLeaveProject}>Leave Project</Button>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="unfollow-project-button" onClick={props.handleUnfollowProject}>Unfollow Project</Button>
                                            </>
                                        }
                                        {
                                            props.isMember && props.isFollower === false &&
                                            <>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="leave-project-button" onClick={props.handleLeaveProject}>Leave Project</Button>
                                                <Button size="medium" variant="contained" color="primary" data-cy="follow-project-button" onClick={props.handleFollowProject}>Follow Project</Button>
                                            </>
                                        }
                                        {
                                            props.isOwner === false && props.isMember === false &&
                                            props.isFollower && props.hasActiveJoinRequest &&
                                            <>
                                                <Button size="medium" variant="contained" disabled data-cy="disabled-join-project-button">Join Project</Button>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="unfollow-project-button" onClick={props.handleUnfollowProject}>Unfollow Project</Button>
                                            </>
                                        }
                                        {
                                            props.isOwner === false && props.isMember === false &&
                                            props.isFollower === false && props.hasActiveJoinRequest &&
                                            <>
                                                <Button size="medium" variant="contained" disabled data-cy="disabled-join-project-button">Join Project</Button>
                                                <Button size="medium" variant="contained" color="primary" data-cy="follow-project-button" onClick={props.handleFollowProject}>Follow Project</Button>
                                            </>
                                        }
                                        {
                                            props.isOwner === false && props.isMember === false &&
                                            props.isFollower && props.hasActiveJoinRequest === false &&
                                            <>
                                                <Button size="medium" variant="contained" color="primary" data-cy="join-project-button" onClick={handleOpenRequestDialog}>Join Project</Button>
                                                <Button size="medium" variant="contained" color="secondary" data-cy="unfollow-project-button" onClick={props.handleUnfollowProject}>Unfollow Project</Button>
                                                {getRequestDialog()}
                                            </>
                                        }
                                        {
                                            props.isOwner === false && props.isMember === false &&
                                            props.isFollower === false && props.hasActiveJoinRequest === false &&
                                            <>
                                                <Button size="medium" variant="contained" color="primary" data-cy="join-project-button" onClick={handleOpenRequestDialog}>Join Project</Button>
                                                <Button size="medium" variant="contained" color="primary" data-cy="follow-project-button" onClick={props.handleFollowProject}>Follow Project</Button>
                                                {getRequestDialog()}
                                            </>
                                        }
                                    </>
                                }
                            </CardActions>
                        </Card>
                        <Card className={classes.card}>
                            <CardContent>
                                <Grid className={classes.discussionGrid} container>
                                    <Grid className={classes.discussionGridItem} item>
                                        <Typography variant="h5" component="h2" gutterBottom>
                                            Team Members
                                        </Typography>
                                        <Grid container direction="row" spacing={1} alignItems="center">
                                            <Grid item>
                                                <Avatar color="secondary" size="small" className={classes.owner}>O</Avatar>
                                            </Grid>
                                            <Grid item>
                                            <Button href={`/students/${props.project.owner}`} size="large">
                                                {`${props.project.owner_first_name} ${props.project.owner_last_name}`}
                                            </Button>
                                            </Grid>
                                            <Grid item>
                                                <Chip
                                                    size="small"
                                                    label={props.project.owner_role}
                                                    data-cy={`owner-role`}
                                                    color="primary"
                                                    variant="outlined"
                                                    avatar={<Avatar>R</Avatar>}
                                                />
                                            </Grid>
                                        </Grid>
                                        {props.members.map((member, index) => {
                                            return (
                                                <Grid key={index} container direction="row" spacing={1} alignItems="center">
                                                    <Grid item>
                                                        <Avatar color="secondary" size="small" className={classes.member}>M</Avatar>
                                                    </Grid>
                                                    <Grid item>
                                                        <Button href={`/students/${member.user}`} size="large" data-cy={`member-${member.user}-name`}>
                                                            {`${member.user_first_name} ${member.user_last_name}`}
                                                        </Button>
                                                    </Grid>
                                                    <Grid item>
                                                        <Chip
                                                            size="small"
                                                            label={member.role}
                                                            data-cy={`member-${member.user}-role`}
                                                            color="primary"
                                                            variant="outlined"
                                                            avatar={<Avatar>R</Avatar>}
                                                        />
                                                    </Grid>
                                                    {
                                                        props.isOwner &&
                                                        <Grid item>
                                                            <Button
                                                                size="small"
                                                                color="secondary"
                                                                data-cy={`remove-member-${member.user}-button`}
                                                                onClick={() => props.handleRemoveMember(member.id)}
                                                            >
                                                                Remove Member
                                                            </Button>
                                                        </Grid>
                                                    }
                                                </Grid>
                                            )
                                        })}
                                    </Grid>
                                    <Grid className={classes.discussionGridItem} item>
                                        {
                                            (props.isOwner || props.isMember) &&
                                            <>
                                                <Typography variant="h5" component="h2" gutterBottom>
                                                    Member Discussion
                                                </Typography>
                                                <ProjectMemberDiscussion
                                                    projectId={props.project.id}
                                                />
                                            </>
                                        }
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                        <Card className={classes.card}>
                            <CardContent>
                                <Grid className={classes.discussionGrid} container>
                                    <Grid className={classes.discussionGridItem} item>
                                        <Typography variant="h5" component="h2" gutterBottom>
                                            Public Discussion
                                        </Typography>
                                        <ProjectPublicDiscussion
                                            projectId={props.project.id}
                                        />
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </>
                )
            }
        </>
    );
};

export default ProjectView;