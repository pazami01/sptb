import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Formik, FieldArray, Field, getIn } from 'formik';
import * as Yup from 'yup';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import Backdrop from '@material-ui/core/Backdrop';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';
import { MenuItem } from '@material-ui/core';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
    card: {
        padding: 20,
    },
    errorText: {
        fontSize: '0.75rem',
        lineHeight: '1.66',
        color: '#f44336',
    },
    miniButton: {
        marginTop: 5,
        marginBottom: 10,
    },
    submitButton: {
        marginTop: 10,
        marginRight: 10,
    },
    cancelButton: {
        marginTop: 10,
    },
}));

/** Project validation schema. */
const projectValidationSchema = Yup.object().shape({
    title: Yup.string()
        .max(150, 'This field must not contain more than 150 characters'),
    description: Yup.string()
        .max(3000, 'This field must not contain more than 3000 characters'),
    owner_role: Yup.string()
        .max(40, 'This field must not contain more than 40 characters'),
    desired_roles: Yup.array()
        .of(Yup.string().max(40, 'This field must not contain more than 40 characters')),
});


/** Renders a form for creating a project. */
const ProjectCreate = (props) => {
    const [isLoading, setIsLoading] = useState(false);
    const classes = useStyles();
    const history = useHistory();

    /**
     * Handles the submission for creating a project.
     * Updates error messages on fields if a 400 code is returned.
     */
    const handleProjectCreate = async (values, actions) => {
        setIsLoading(true);

        axiosInstance
            .post(`api/projects/`, {
                title: values.title,
                description: values.description,
                category: values.category,
                owner_role: values.owner_role,
                desired_roles: values.desired_roles
            })
            .then(response => {
                setIsLoading(false);
                const project_id = response.data.id

                history.push(`/projects/${project_id}`);
            })
            .catch(error => {
                if (error.response.status === 400) {
                    setIsLoading(false);

                    actions.setFieldError('title', error.response.data.title);
                    actions.setFieldError('description', error.response.data.description);
                    actions.setFieldError('category', error.response.data.category);
                    actions.setFieldError('owner_role', error.response.data.owner_role);
                    actions.setFieldError('title', error.response.data.title);

                    if (error.response.data.desired_roles) {
                        for (const [key, value] of Object.entries(error.response.data.desired_roles)) {
                            actions.setFieldError(`desired_roles.${key}`, value);
                        }
                    }
                } else {
                    console.log(error.response);
                }
            });
    };

    const handleCancelCreateProject = () => {
        history.push('/projects');
    }

    /**
     * Custom error message for fields for use in array fields
     * This code is taken from https://formik.org/docs/api/fieldarray#fieldarray-validation-gotchas
     */
    const ErrorMessage = ({ name }) => (
        <Field name={name}>
            {({ form }) => {
                const error = getIn(form.errors, name);
                const touch = getIn(form.touched, name);

                return touch && error ? <p className={classes.errorText}>{error}</p> : null;
            }}
        </Field>
    );

    /** all possible categories */
    const categories = [
        {code: "ART", name: "Arts"},
        {code: "EDN", name: "Education"},
        {code: "FSN", name: "Fashion"},
        {code: "FLM", name: "Film"},
        {code: "FNC", name: "Finance"},
        {code: "MCN", name: "Medicine"},
        {code: "SFW", name: "Software"},
        {code: "SPT", name: "Sport"},
        {code: "TEC", name: "Technology"},
    ]

    /**
     * Returns form for creating a project.
     * Code for FieldArray is based on https://formik.org/docs/examples/field-arrays
     */
    const getProjectForm = () => {
        return (
            <Formik
                initialValues={{
                    title: '',
                    description: '',
                    category: categories[0].code,
                    owner_role: '',
                    desired_roles: [],
                }}
                validationSchema={projectValidationSchema}
                onSubmit={handleProjectCreate}
            >
                {({ values, handleBlur, handleChange, isSubmitting, handleSubmit, touched, errors }) => (
                    <form className={classes.form} noValidate>
                        <TextField
                            label="Title"
                            type="text"
                            variant="outlined"
                            className={classes.textInputField}
                            data-cy="title"
                            fullWidth
                            margin="normal"
                            name="title"
                            id="title"
                            value={values.title}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            error={touched.title && Boolean(errors.title)}
                            helperText={touched.title && errors.title}
                        />
                        <TextField
                            multiline
                            rows={21}
                            label="Description"
                            type="text"
                            variant="outlined"
                            className={classes.textAreaField}
                            data-cy="description"
                            fullWidth
                            margin="normal"
                            name="description"
                            id="description"
                            value={values.description}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            error={touched.description && Boolean(errors.description)}
                            helperText={touched.description && errors.description}
                        />
                        <TextField
                            select
                            label="Category"
                            variant="outlined"
                            data-cy="category"
                            fullWidth
                            margin="normal"
                            name="category"
                            id="category"
                            value={values.category}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            error={touched.category && Boolean(errors.category)}
                            helperText={touched.category && errors.category}
                        >
                            {categories.map(category => (
                                <MenuItem key={category.code} value={category.code} data-cy={category.code}>
                                    {category.name}
                                </MenuItem>
                            ))}
                        </TextField>
                        <TextField
                            label="Your Role"
                            type="text"
                            variant="outlined"
                            className={classes.textInputField}
                            data-cy="owner_role"
                            fullWidth
                            margin="normal"
                            name="owner_role"
                            id="owner-role"
                            value={values.owner_role}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            error={touched.owner_role && Boolean(errors.owner_role)}
                            helperText={touched.owner_role && errors.owner_role}
                        />
                        <FieldArray name="desired_roles">
                            {({ form, remove, push }) => (
                                <div>
                                    {
                                        values.desired_roles.length > 0 &&
                                        values.desired_roles.map((role, index) => (
                                            <div key={index}>
                                                <div>
                                                    <TextField
                                                        type="text"
                                                        label={`Desired Role ${index + 1}`}
                                                        data-cy={`desired_role-${index}`}
                                                        name={`desired_roles.${index}`}
                                                        fullWidth
                                                        margin="normal"
                                                        value={role}
                                                        onChange={form.handleChange}
                                                        onBlur={form.handleBlur}
                                                    />
                                                </div>
                                                <div>
                                                    <ErrorMessage
                                                        name={`desired_roles.${index}`}
                                                    />
                                                </div>
                                                <div>
                                                    <Button
                                                        variant="outlined"
                                                        className={classes.miniButton}
                                                        data-cy={`remove-role-${index}-button`}
                                                        color="secondary"
                                                        type="button"
                                                        size="small"
                                                        onClick={() => remove(index)}
                                                    >
                                                        Remove
                                                    </Button>
                                                </div>
                                            </div>
                                        ))
                                    }
                                    {
                                        values.desired_roles.length < 10 &&
                                        <Button
                                            variant="outlined"
                                            className={classes.miniButton}
                                            data-cy="add-role-button"
                                            color="secondary"
                                            type="button"
                                            size="small"
                                            onClick={() => push('')}
                                        >
                                            Add New Desired Role
                                        </Button>
                                    }
                                </div>
                            )}
                        </FieldArray>
                        <Button
                            variant="contained"
                            className={classes.submitButton}
                            data-cy="submit-create-project-button"
                            color="primary"
                            type="submit"
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                        >
                            Create
                        </Button>
                        <Button
                            variant="contained"
                            className={classes.cancelButton}
                            data-cy="cancel-create-project-button"
                            type="button"
                            onClick={handleCancelCreateProject}
                        >
                            Cancel
                        </Button>
                    </form>
                )}
            </Formik>
        );
    };

    return (
        <>
            <Card className={classes.card}>
                <CardContent>
                    <Typography variant="h3" component="h1" gutterBottom>
                        Create New Project
                    </Typography>
                    {getProjectForm()}
                </CardContent>
            </Card>
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </>
    );
};

export default ProjectCreate;