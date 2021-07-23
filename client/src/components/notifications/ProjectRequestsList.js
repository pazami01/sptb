import React, { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
/** my components */
import ProjectRequestCard from './ProjectRequestCard';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
    card: {
        padding: 20,
        marginBottom: 25,
    }
}));


/** Renders a list of project requests. */
const ProjectRequestsList = (props) => {
    const [isLoading, setIsLoading] = useState(false);
    const classes = useStyles();
    const [requests, setRequests] = useState([]);

    const history = useHistory();
    const location = useLocation();

    /** Fetches and stores the authenticated student's active project requests. */
    useEffect(() => {
        setIsLoading(true);

        axiosInstance
            .get(`api/requests/`)
            .then( response => {
                setIsLoading(false);
                setRequests(response.data);
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error.response);
            });
    }, []);

    /** Sets a new list of requests excluding the request with the given ID. */
    const removeRequest = (requestId) => {
        const new_requests_list = [];

        requests.map(request => {
            if (request.id != requestId) {
                new_requests_list.push(request);
            }
        });

        setRequests(new_requests_list);
    };

    /** Cancels a request with the given ID. */
    const handleCancelRequest = (requestId) => {
        axiosInstance
            .put(`api/requests/${requestId}/`, {status: "CNL"})
            .then(response => {
                removeRequest(requestId);
            })
            .catch(error => {
                console.log(error);

                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    };

    /** Declines a request with the given ID. */
    const handleDeclineRequest = (requestId) => {
        axiosInstance
            .put(`api/requests/${requestId}/`, {status: "DCN"})
            .then(response => {
                removeRequest(requestId);
            })
            .catch(error => {
                console.log(error);

                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    };

    /** Accepts a request with the given ID. */
    const handleAcceptRequest = (requestId) => {
        axiosInstance
            .put(`api/requests/${requestId}/`, {status: "ACP"})
            .then(response => {
                removeRequest(requestId);
            })
            .catch(error => {
                console.log(error);

                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    };

    return (
        <>
            {
                <Card className={classes.card}>
                    <CardContent>
                        <Typography component="h1" variant="h3" gutterBottom>Your Project Requests</Typography>
                    </CardContent>
                </Card>
            }
            <Grid container spacing={1} justify="flex-start" data-cy="requests-container">
                {
                    requests.map(request => {
                        return (
                            <Grid item key={request.id}>
                                <ProjectRequestCard
                                    requestId={request.id}
                                    requester={request.requester}
                                    requester_first_name={request.requester_first_name}
                                    requester_last_name={request.requester_last_name}
                                    requestee={request.requestee}
                                    requestee_first_name={request.requestee_first_name}
                                    requestee_last_name={request.requestee_last_name}
                                    project={request.project}
                                    projectTitle={request.project_title}
                                    role={request.role}
                                    handleCancelRequest={handleCancelRequest}
                                    handleDeclineRequest={handleDeclineRequest}
                                    handleAcceptRequest={handleAcceptRequest}
                                />
                            </Grid>
                        )
                    })
                }
            </Grid>
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </>
    );
};

export default ProjectRequestsList;