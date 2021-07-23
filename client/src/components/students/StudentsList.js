import React, { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
/** my components */
import StudentCard from './StudentCard';
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


/** Renders a list of student profiles. */
const StudentsList = (props) => {
    const [students, setStudents] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const classes = useStyles();
    const history = useHistory();
    const location = useLocation();

    // check for query params
    const searchQuery = location.search;

    /** Fetches and stores all student profiles. */
    useEffect(() => {
        setIsLoading(true);

        // filter according to query params if provided
        const url = searchQuery ? `api/accounts${searchQuery}` : 'api/accounts/';

        axiosInstance
            .get(url)
            .then( response => {
                setIsLoading(false);
                setStudents(response.data);
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error.response);
            });
    }, [searchQuery]);

    /** redirects to the student profile page for the given student ID. */
    const handleCardClick = (studentId) => history.push(`/students/${studentId}`);

    return (
        <>
            <Card className={classes.card}>
                <CardContent>
                    <Typography component="h1" variant="h3" gutterBottom>Students</Typography>
                </CardContent>
            </Card>
            <Grid container spacing={1} justify="flex-start" data-cy="students-container">
                {
                    students.map(student => {
                        return (
                            <Grid item key={student.id}>
                                <StudentCard
                                    handleCardClick={handleCardClick}
                                    student={student}
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

export default StudentsList;