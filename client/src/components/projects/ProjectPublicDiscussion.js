import React, { useState, useEffect } from 'react';
import * as Yup from 'yup';
import { useHistory, useLocation } from 'react-router-dom';
/** my components */
import ProjectMessageList from './ProjectMessageList';
import ProjectMessageForm from './ProjectMessageForm';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';


/** Discussion form validation schema. */
const discussionFormValidationSchema = Yup.object().shape({
    message: Yup.string()
        .max(1000, 'This field must not contain more than 1000 characters'),
});


/** Renders the public discussion room for a given project ID */
const ProjectPublicDiscussion = (props) => {
    const [messages, setMessages] = useState([]);
    const [refreshMessages, setRefreshMessages] = useState(false);

    const location = useLocation();
    const history = useHistory();

    /**
     * Fetch and store the public messages for the given project id
     * Redirects to a 404 page if the project doesn't exist.
     */
     useEffect(() => {
        axiosInstance
            .get(`api/projects/${props.projectId}/public-messages/`)
            .then(response => {
                setMessages(response.data);
            })
            .catch(error => {
                console.log(error);

                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    }, [refreshMessages]);

    /** Activates flag for refreshing messages */
    const handleRefreshMessages = () => {
        setRefreshMessages(!refreshMessages);
    }

    /**
     * Handles the submission for a public message.
     * Updates error messages on fields if a 400 code is returned.
     */
     const handleMessageFormSubmit = async (values, actions) => {
        axiosInstance
            .post(`api/projects/${props.projectId}/public-messages/`, {
                message: values.message,
            })
            .then(response => {
                actions.resetForm();
                handleRefreshMessages();
            })
            .catch(error => {
                if (error.response.status === 400) {
                    actions.setFieldError('message', error.response.data.message);
                } else {
                    console.log(error.response);
                }
            });
    };

    return (
        <>
            <ProjectMessageList messages={messages} />
            <ProjectMessageForm
                discussionFormValidationSchema={discussionFormValidationSchema}
                handleMessageFormSubmit={handleMessageFormSubmit}
                handleRefreshMessages={handleRefreshMessages}
            />
        </>
    );
};

export default ProjectPublicDiscussion;