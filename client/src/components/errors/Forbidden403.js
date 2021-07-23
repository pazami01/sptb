import React from 'react';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';


/** Custom styles for this component */
const useStyles = makeStyles({
    card: {
        padding: 20,
    },
});

/** A component to render when there is a 404 error. */
const Forbidden403 = (props) => {
    const classes = useStyles();

    return (
        <Card className={classes.card}>
            <CardContent>
                <Typography component="h1" variant="h3" gutterBottom>
                    Access Denied
                </Typography>
                <Typography component="p" variant="h6">
                    You do not have permission to access this page.
                </Typography>
            </CardContent>
        </Card>
    );
};

export default Forbidden403;