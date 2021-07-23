import React, { useContext } from 'react';
import { useHistory } from 'react-router-dom';
/** Images */
import defaultRequestImage from '../../assets/images/default-invitation-image-small.png';
/** my components */
import { AuthContext } from '../context/AuthContextProvider';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Avatar from '@material-ui/core/Avatar';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';


/** Custome styles for this component */
const useStyles = makeStyles((theme) => ({
    requestCard: {
        maxWidth: 300,
    },
    requestInfo: {
        minHeight: 230,
    },
}));


/** Renders a project request in a card element. */
const ProjectRequestCard = (props) => {
    const classes = useStyles();
    const history = useHistory();
    const authContext = useContext(AuthContext);

    return (
        <Card className={classes.requestCard} data-cy={`request-${props.requestId}-card`}>
            <CardMedia
                component="img"
                alt="Default Request"
                height="150"
                image={defaultRequestImage}
                title="Default Request"
            />
            <CardContent className={classes.requestInfo}>
                <Typography variant="subtitle1" component="h3" color="primary" align="center" data-cy={`request-${props.requestId}-desc`} gutterBottom>
                    {
                        authContext.studentId === props.requester ?
                        `You sent ${props.requestee_first_name} ${props.requestee_last_name} a request` :
                        `${props.requester_first_name} ${props.requester_last_name} sent you a request`
                    }
                </Typography>
                <Grid container alignItems="center">
                    <Grid item>
                        <Typography variant="subtitle1" component="h3" gutterBottom>
                            Sender:
                        </Typography>
                    </Grid>
                    <Grid item>
                        {
                            <Button color="primary" onClick={() => history.push(`/students/${props.requester}`)}>
                                {
                                    authContext.studentId === props.requester ?
                                    'You' :
                                    `${props.requester_first_name} ${props.requester_last_name}`
                                }
                            </Button>
                        }
                    </Grid>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item>
                        <Typography variant="subtitle1" component="h3" gutterBottom>
                            Receiver:
                        </Typography>
                    </Grid>
                    <Grid item>
                        {
                            <Button color="primary" onClick={() => history.push(`/students/${props.requestee}`)}>
                                {
                                    authContext.studentId === props.requestee ?
                                    'You' :
                                    `${props.requestee_first_name} ${props.requestee_last_name}`
                                }
                            </Button>
                        }
                    </Grid>
                </Grid>
                <Grid container alignItems="center">
                    <Grid item>
                        <Typography variant="subtitle1" component="h3" gutterBottom>
                            Project:
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Button color="primary" onClick={() => history.push(`/projects/${props.project}`)}>
                            {`${props.projectTitle}`}
                        </Button>
                    </Grid>
                </Grid>
                <Grid container spacing={1} alignItems="center">
                    <Grid item>
                        <Typography variant="subtitle1" component="h3" gutterBottom>
                            Role:
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Chip
                            color="primary"
                            variant="outlined"
                            size="small"
                            label={props.role}
                            avatar={<Avatar>R</Avatar>}
                        />
                    </Grid>
                </Grid>
            </CardContent>
            <CardContent>
                <Grid container spacing={2} justify="center">
                    {
                        authContext.studentId === props.requester ?
                        <Grid item>
                            <Button variant="contained" size="small" data-cy={`request-${props.requestId}-cancel-button`} onClick={() => props.handleCancelRequest(props.requestId)}>
                                Cancel
                            </Button>
                        </Grid> :
                        <>
                            <Grid item>
                                <Button variant="contained" color="secondary" size="small" data-cy={`request-${props.requestId}-decline-button`} onClick={() => props.handleDeclineRequest(props.requestId)}>
                                    Decline
                                </Button>
                            </Grid>
                            <Grid item>
                                <Button variant="contained" color="primary" size="small" data-cy={`request-${props.requestId}-accept-button`} onClick={() => props.handleAcceptRequest(props.requestId)}>
                                    Accept
                                </Button>
                            </Grid>
                        </>
                    }
                </Grid>
            </CardContent>
        </Card>
    );
};

export default ProjectRequestCard;