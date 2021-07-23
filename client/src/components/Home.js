import React from 'react';
import ProjectsList from './projects/ProjectsList';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    card: {
        padding: 20,
        marginBottom: 25,
    },
}));


const Home = (props) => {
    const classes = useStyles();

    return (
        <>
            <Card className={classes.card}>
                <CardContent>
                    <Typography component="h1" variant="h3" gutterBottom>Welcome to the project team builder application!</Typography>
                    <Typography component="p" variant="body1">
                        Create project proposals and build teams to see the projects through to completion.
                        Browse through the list of student profiles to find the right person to fill the roles within your project.
                        Alternatively, browse existing projects and request to join their team with a role that interests you.
                    </Typography>
                </CardContent>
                <CardContent>
                    <Typography component="h2" variant="h4" gutterBottom>Popular Projects</Typography>
                </CardContent>
            </Card>
            <ProjectsList addHeading={false} apiEndpoint="api/projects?order=popularity&limit=6"/>
        </>
    );
};

export default Home;