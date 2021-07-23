import React from 'react';
import { useHistory } from 'react-router-dom';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    list: {
        overflow: "auto",
        minHeight: 400,
        maxHeight: 400,
        border: "1px solid #D5D5D5",
    },
    block: {
        display: "block",
    },
}));



/** Renders a List component of a given list of project messages */
const ProjectMessageList = (props) => {
    const classes = useStyles();
    const history = useHistory();

    /** Returns a list of messages */
    const getMessageList = () => {
        return (
            <List className={classes.list}>
                {
                    props.messages.map((message, index) => {
                        return (
                            <div key={index}>
                                <ListItem key={index}>
                                    <ListItemText
                                        primary={
                                            <Button onClick={() => history.push(`/students/${message.user}`)} color="primary">
                                                {`${message.user_first_name} ${message.user_last_name}`}
                                            </Button>
                                        }
                                        secondary={
                                            <>
                                                <Typography component="span" variant="body2" className={classes.block} gutterBottom>
                                                    {`${message.date_created.substring(0, 10)} ${message.date_created.substring(11, 16)}`}
                                                </Typography>
                                                <Typography component="span" variant="body1" color="textPrimary" gutterBottom>
                                                    {message.message}
                                                </Typography>
                                            </>
                                        }
                                    />
                                </ListItem>
                                <Divider variant="middle" light/>
                            </div>
                        )
                    })
                }
            </List>
        )
    };

    return (
        props.messages &&
        props.messages.length > 0 &&
        getMessageList()
    );
};

export default ProjectMessageList;