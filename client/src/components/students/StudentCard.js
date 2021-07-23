import React from 'react';
/** Images */
import defaultProfileImage from '../../assets/images/default-profile-image.png';
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
    studentCard: {
        maxWidth: 300,
    },
    studentInfo: {
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


/** Renders a student profile in a card element. */
const StudentCard = (props) => {
    const classes = useStyles();

    return (
        <Card className={classes.studentCard} data-cy={`student-${props.student.id}-card`}>
            <CardActionArea
                data-cy={`student-${props.student.id}-button`}
                onClick={() => props.handleCardClick(props.student.id)}
            >
                <CardMedia
                    component="img"
                    alt="Default Profile"
                    height="300"
                    image={defaultProfileImage}
                    title="Default Profile"
                />
                <CardContent className={classes.studentInfo}>
                    <Typography variant="h6" component="h3" data-cy={`student-${props.student.id}-name`} gutterBottom>
                        {`${props.student.first_name} ${props.student.last_name}`}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" component="p">
                        {`${getExcerpt(props.student.profile.about)}`}
                    </Typography>
                    <Grid
                        container
                        direction="column"
                        justify="space-between"
                        className={classes.roleContainer}
                        spacing={1}
                    >
                        {props.student.profile.roles.map((role, index) => {
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

export default StudentCard;