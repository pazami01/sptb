import React from 'react';
/** Images */
import defaultProjectImage from '../../assets/images/default-project-image-small.png';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Avatar from '@material-ui/core/Avatar';
import Chip from '@material-ui/core/Chip';


/** Custome styles for this component */
const useStyles = makeStyles((theme) => ({
    projectCard: {
        maxWidth: 405,
    },
    projectInfo: {
        minHeight: 270,
    },
    roleContainer: {
        marginTop: 10,
    },
}));


/** takes an input string and returns the first 150 characters. */
const getExcerpt = (input) => {
    const LIMIT = 150;

    if (!input) {
        return '';
    }

    if (input.length > LIMIT) {
        return `${input.substring(0, LIMIT)}...`;
    }
    
    return input;
}


/** Renders a project in a card element. */
const ProjectCard = (props) => {
    const classes = useStyles();

    return (
        <Card className={classes.projectCard} data-cy={`project-${props.projectId}-card`}>
            <CardActionArea
                data-cy={`project-${props.projectId}-button`}
                onClick={() => props.handleCardClick(props.projectId)}
            >
                <CardMedia
                    component="img"
                    alt="Default Project"
                    height="300"
                    image={defaultProjectImage}
                    title="Default Project"
                />
                <CardContent className={classes.projectInfo}>
                    <Typography variant="h6" component="h3" data-cy={`project-${props.projectId}-name`} gutterBottom>
                        {`${props.projectTitle}`}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" component="p" gutterBottom>
                        {`${getExcerpt(props.projectDescription)}`}
                    </Typography>
                    <Chip
                        size="small"
                        clickable
                        label={props.categoryName}
                        color="secondary"
                        avatar={<Avatar>C</Avatar>}
                    />
                    <Grid
                        container
                        direction="column"
                        justify="space-between"
                        className={classes.roleContainer}
                        spacing={1}
                    >
                        {props.desiredRoles.slice(0, 3).map((role, index) => {
                            return (
                                <Grid key={index} item>
                                    <Chip
                                        size="small"
                                        variant="outlined"
                                        clickable
                                        label={role}
                                        color="primary"
                                        avatar={<Avatar>R</Avatar>}
                                    />
                                </Grid>
                            )
                        })}
                    </Grid>
                </CardContent>
            </CardActionArea>
        </Card>
    );
};

export default ProjectCard;