import React, { useContext, useState, useEffect } from 'react';
import { useParams, useHistory, useLocation } from 'react-router-dom';
/** my components */
import { AuthContext } from '../context/AuthContextProvider';
import ProjectView from './ProjectView';
import ProjectUpdate from './ProjectUpdate';
/** my utilities */
import { axiosInstance } from '../../utilities/axios';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';


/** custom styles for this component */
const useStyles = makeStyles((theme) => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
    },
}));


/** Base component for projects. Renders the project and the project edit form. */
const Project = (props) => {
    const [isLoading, setIsLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    const [project, setProject] = useState(null);
    const [members, setMembers] = useState([]);
    const [followId, setFollowId] = useState();

    // auth user relations with project
    const [isOwner, setIsOwner] = useState(false);
    const [isMember, setIsMember] = useState(false);
    const [isFollower, setIsFollower] = useState(false);
    const [hasActiveJoinRequest, setHasActiveJoinRequest] = useState(false);

    // this is a string type
    const { id } = useParams();  // we don't know if a project with this ID exists in the database
    
    const history = useHistory();
    const location = useLocation();
    const classes = useStyles();
    const authContext = useContext(AuthContext);

    /**
     * Fetch and store project information.
     * Redirects to a 404 page if the project doesn't exist.
     */
    useEffect(() => {
        setIsLoading(true);
        axiosInstance
            .get(`api/projects/${id}/`)
            .then(response => {
                setIsLoading(false);
                setProject(response.data);

                const members_list = [];

                response.data.team_members.map((member, index) => {
                    members_list[index] = {...member};
                });
                // store team members separately
                setMembers(members_list);

                // the authenticated student is the owner of this project
                if (response.data.owner === authContext.studentId) {
                    setIsOwner(true);
                }

                response.data.team_members.map(team_member => {
                    if (team_member.user === authContext.studentId) {
                        setIsMember(true);
                    }
                });
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error);
                
                if (error.response.status === 404) {
                    history.push(`${location.pathname}/page-not-found`);
                }
            });
    }, []);

    /**
     * Fetch the authenticated student's active requests and update HasActiveJoinRequest
     * if a request for this project exists
     */
     useEffect(() => {
        setIsLoading(true);
        axiosInstance
            .get(`api/requests/`)
            .then(response => {
                setIsLoading(false);

                response.data.map(request => {
                    if (request.project == id) {
                        setHasActiveJoinRequest(true);
                    }
                });
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error);
            });
    }, []);

    /** Gets the authenticated student's follows and stores the follow id associated with this project */
     useEffect(() => {
        setIsLoading(true);
        axiosInstance
            .get(`api/follows/`)
            .then(response => {
                setIsLoading(false);
                // check if the authenticated student is following this project
                response.data.map(follow => {
                    if (follow.project == id) {
                        setFollowId(follow.id);
                        setIsFollower(true);
                    }
                });
            })
            .catch(error => {
                setIsLoading(false);
                console.log(error);
            });
    }, []);

    /** Sets editing state for this project */
    const handleEditProject = () => {
        setIsEditing(true);
    }

    /** Take a membership id and deletes that membership associated with this project */
    const handleRemoveMember = (membership_id) => {
        if (isOwner) {
            axiosInstance
                .delete(`api/memberships/${membership_id}/`)
                .then(response => {
                    const new_members_list = []

                    members.map(member => {
                        if (member.id != membership_id) {
                            new_members_list.push({...member});
                        }
                    });

                    setMembers(new_members_list);
                })
                .catch(error => {
                    console.log(error);
                });
        }
    }

    /** Deletes this project */
    const handleDeleteProject = () => {
        // delete project and redirect
        if (isOwner) {
            axiosInstance
                .delete(`api/projects/${id}/`)
                .then(response => {
                    history.push('/projects/active');
                })
                .catch(error => {
                    console.log(error);
                });
        }
    }

    /** Deletes authenticated student's membership to this project. */
    const handleLeaveProject = () => {
        if (isMember) {
            setIsLoading(true);

            let memberId = 0;

            project.team_members.map(member => {
                if (member.user === authContext.studentId) {
                    memberId = member.id;
                }
            });
            axiosInstance
                .delete(`api/memberships/${memberId}/`)
                .then(response => {
                    setIsLoading(false);
                    setIsMember(false);

                    const new_members_list = []

                    members.map(member => {
                        if (member.user != authContext.studentId) {
                            new_members_list.push({...member});
                        }
                    });

                    setMembers(new_members_list);
                })
                .catch(error => {
                    setIsLoading(false);
                    console.log(error);
                });
        }
    }

    /** Sets request status for the authenticate student to true */
    const handleRequestSent = () => {
        setHasActiveJoinRequest(true);
    }

    /** Adds authenticated student as the follower of this project */
    const handleFollowProject = () => {
        // add to student's followed projects and update state
        if (isFollower === false) {
            setIsLoading(true);

            axiosInstance
                .post(`api/follows/`, {"project": id})
                .then(response => {
                    setIsLoading(false);
                    setFollowId(response.data.id);
                    setIsFollower(true);
                })
                .catch(error => {
                    setIsLoading(false);
                    console.log(error);
                });
        }
    }

    /** Removes authenticated student as the follower of this project */
    const handleUnfollowProject = () => {
        // remove from student's followed projects and update state
        if (isFollower) {
            setIsLoading(true);

            axiosInstance
                .delete(`api/follows/${followId}/`)
                .then(response => {
                    setIsLoading(false);
                    setFollowId(-1);
                    setIsFollower(false);
                })
                .catch(error => {
                    setIsLoading(false);
                    console.log(error);
                });
        }
    }

    /** Updates project data and disables editing state */
    const handleUpdateProject = (new_project_data) => {
        setProject(new_project_data);
        setIsEditing(false);
    }

    /** Sets project edit state to false */
    const handleCancelUpdateProject = () => {
        setIsEditing(false);
    }

    return (
        <>
            {
                isEditing ?
                <ProjectUpdate
                    isOwner={isOwner}
                    currentProjectData={project}
                    handleUpdateProject={handleUpdateProject}
                    handleCancelUpdateProject={handleCancelUpdateProject}
                /> :
                <ProjectView
                    project={project}
                    members={members}
                    isOwner={isOwner}
                    isMember={isMember}
                    isFollower={isFollower}
                    hasActiveJoinRequest={hasActiveJoinRequest}
                    handleEditProject={handleEditProject}
                    handleDeleteProject={handleDeleteProject}
                    handleLeaveProject={handleLeaveProject}
                    handleRequestSent={handleRequestSent}
                    handleFollowProject={handleFollowProject}
                    handleUnfollowProject={handleUnfollowProject}
                    handleRemoveMember={handleRemoveMember}
                /> 
            }
            
            <Backdrop className={classes.backdrop} open={isLoading}>
                <CircularProgress color="secondary" />
            </Backdrop>
        </>
    );
};

export default Project;