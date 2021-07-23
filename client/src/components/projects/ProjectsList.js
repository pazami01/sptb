import { useHistory, useLocation } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
/** my components */
import ProjectCard from './ProjectCard';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
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


/** Renders a list of projects. */
const ProjectsList = (props) => {
    const [projects, setProjects] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const classes = useStyles();
    const history = useHistory();
    const location = useLocation();

    // check for query params
    const searchQuery = location.search;

    /** Fetches and stores projects. */
    useEffect(() => {
        setIsLoading(true);

        // filter according to query params if provided
        const url = searchQuery ? `api/projects${searchQuery}` : props.apiEndpoint;

        axiosInstance
            .get(`${url}`)
            .then( response => {
                setIsLoading(false);
                setProjects(response.data);
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error.response);
            });
    }, [props.apiEndpoint, searchQuery]);

    /** redirects to the project page for the given project ID. */
    const handleCardClick = (projectId) => history.push(`/projects/${projectId}`);

    return (
        <>
            {
                props.addHeading &&
                <Card className={classes.card}>
                    <CardContent>
                        <Typography component="h1" variant="h3" gutterBottom>{`${props.heading}`}</Typography>
                    </CardContent>
                </Card>
            }
            <Grid container spacing={1} justify="flex-start" data-cy="projects-container">
                {
                    projects.map(project => {
                        return (
                            <Grid item key={project.id}>
                                <ProjectCard
                                    handleCardClick={handleCardClick}
                                    projectId={project.id}
                                    projectTitle={project.title}
                                    projectDescription={project.description}
                                    categoryName={project.category_name}
                                    desiredRoles={project.desired_roles}
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

export default ProjectsList;