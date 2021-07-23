import React from 'react';
import { Formik } from 'formik';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    submitButton: {
        marginRight: 10,
    },
}));


/** Renders a form for sending project messages */
const ProjectMessageForm = (props) => {
    const classes = useStyles();

    /** Returns a form for submission of project messages */
    const getMessageForm = () => {
        return (
            <Formik
                initialValues={{
                    message: '',
                }}
                validationSchema={props.discussionFormValidationSchema}
                onSubmit={props.handleMessageFormSubmit}
            >
                {({ values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors }) => (
                    <form className={classes.form} noValidate>
                        <TextField
                            multiline
                            rows={4}
                            label="Message"
                            type="text"
                            variant="outlined"
                            className={classes.textAreaField}
                            fullWidth
                            margin="normal"
                            name="message"
                            value={values.message}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            error={touched.message && Boolean(errors.message)}
                            helperText={touched.message && errors.message}
                        />
                        <Button
                            variant="contained"
                            className={classes.submitButton}
                            color="primary"
                            type="submit"
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                        >
                            Send
                        </Button>
                        <Button
                            variant="contained"
                            className={classes.refreshButton}
                            type="button"
                            onClick={props.handleRefreshMessages}
                        >
                            Refresh
                        </Button>
                    </form>
                )}
            </Formik>
        )
    };

    return (
        getMessageForm()
    );
};

export default ProjectMessageForm;