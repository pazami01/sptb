import React from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { Formik, FieldArray, Field, getIn } from 'formik';
import * as Yup from 'yup';
/** my components */
import Forbidden403 from '../errors/Forbidden403';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
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


/** Renders a form for creating and updating a project. */
const ProjectUpdate = (props) => {
    const classes = useStyles();
    const history = useHistory();
    const location = useLocation();

    /**
     * Handles the submission for updating a project.
     * Updates error messages on fields if a 400 code is returned.
     * Redirects to 404 component if 404 code is returned.
     */
    const handleProjectUpdate = async (values, actions) => {
        axiosInstance
            .put(`api/projects/${props.currentProjectData.id}/`, {
                title: values.title,
                description: values.description,
                category: values.category,
                owner_role: values.owner_role,
                desired_roles: values.desired_roles
            })
            .then(response => {
                props.handleUpdateProject(response.data);
            })
            .catch(error => {
                if (error.response.status === 400) {
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
                } else if (error.response.status === 403) {
                    actions.setFieldError('all', 'You do not have permission to modify this project');
                } else if (error.response.status === 404) {
                    console.log(error.response);
                    history.push(`${location.pathname}/page-not-found`);
                } else {
                    console.log(error.response);
                }
            });
    };

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
     * Returns form for editing a project.
     * Code for FieldArray is based on https://formik.org/docs/examples/field-arrays
     */
    const getProjectForm = () => {
        if (Object.keys(props.currentProjectData).length > 0) {
            return (
                <Formik
                    initialValues={{
                        title: props.currentProjectData.title,
                        description: props.currentProjectData.description,
                        category: props.currentProjectData.category,
                        owner_role: props.currentProjectData.owner_role,
                        desired_roles: [...props.currentProjectData.desired_roles],
                    }}
                    validationSchema={projectValidationSchema}
                    onSubmit={handleProjectUpdate}
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
                                data-cy="update-project-button"
                                color="primary"
                                type="submit"
                                onClick={handleSubmit}
                                disabled={isSubmitting}
                            >
                                Update
                            </Button>
                            <Button
                                variant="contained"
                                className={classes.cancelButton}
                                data-cy="cancel-update-project-button"
                                type="button"
                                onClick={props.handleCancelUpdateProject}
                            >
                                Cancel
                            </Button>
                        </form>
                    )}
                </Formik>
            );
        }
        return null;
    };

    return (
        <>
            {
                props.isOwner ? (
                    <Card className={classes.card}>
                        <CardContent>
                            <Typography variant="h3" component="h1" gutterBottom>
                                Edit Project
                            </Typography>
                            {getProjectForm()}
                        </CardContent>
                    </Card>
                ) : <Forbidden403 />
            }
        </>
    );
};

export default ProjectUpdate;