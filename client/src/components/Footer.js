import React from 'react';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    footer: {
        backgroundColor: '#3F51B5',
        padding: '22px 0',
    },
    footerContainer: {
        color: '#ffffff',
    }
}));


const Footer = (props) => {
    const classes = useStyles();

    return (
        <div className={classes.footer}>
            <Container className={classes.footerContainer}>
                <Typography component="p" variant="body2" align="center">
                    &#169; 2021 Peyman Azami
                </Typography>
            </Container>
        </div>
    );
};

export default Footer;