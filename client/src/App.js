import React, { useContext } from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
/** my components */
import { AuthContext } from './components/context/AuthContextProvider';
import Home from './components/Home';
import StudentsList from './components/students/StudentsList';
import StudentView from './components/students/StudentView';
import Footer from './components/Footer';
import Header from './components/Header';
import Login from './components/Login';
import NotFound404 from './components/errors/NotFound404';
import ProtectedRoute from './components/routes/ProtectedRoute';
import StudentEdit from './components/students/StudentEdit';
import ProjectsList from './components/projects/ProjectsList';
import Project from './components/projects/Project';
import ProjectCreate from './components/projects/ProjectCreate';
import ProjectRequestsList from './components/notifications/ProjectRequestsList';
/** Material UI Imports */
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import CssBaseline from '@material-ui/core/CssBaseline';

/** Custom styles for this component */
const useStyles = makeStyles({
  app: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    minHeight: '100vh',
    backgroundColor: '#f2f2f2',
  },
  mainContainer: {
    marginTop: 64,
    paddingTop: 24,
    paddingBottom: 24,
    flex: 1,
  },
});


/**
 * Main component of the application.
 * Contains the header, footer and the routing for the entire website.
 */
const App = (props) => {
  const authContext = useContext(AuthContext);
  const classes = useStyles();

  return (
    <>
      <Header />
      <div className={classes.app}>
        <CssBaseline />  {/** remove unnecessary browser default styles */}
        <Container className={classes.mainContainer}>
          <Switch>
            <Route exact path="/login">
              { authContext.isAuthenticated ? <Redirect to="/" /> : <Login /> }
            </Route>
            <ProtectedRoute exact path="/">
              <Home />
            </ProtectedRoute>
            <ProtectedRoute exact path="/students">
              <StudentsList />
            </ProtectedRoute>
            <ProtectedRoute exact path="/students/:id">
              <StudentView />
            </ProtectedRoute>
            <ProtectedRoute exact path="/students/:id/edit">
              <StudentEdit />
            </ProtectedRoute>
            <ProtectedRoute exact path="/projects/new">
              <ProjectCreate />
            </ProtectedRoute>
            <ProtectedRoute exact path="/projects">
              <ProjectsList addHeading={true} heading="Projects" apiEndpoint="api/projects?order=descending"/>
            </ProtectedRoute>
            <ProtectedRoute exact path="/projects/active">
              <ProjectsList addHeading={true} heading="Your Active Projects" apiEndpoint="api/projects?relation=active"/>
            </ProtectedRoute>
            <ProtectedRoute exact path="/projects/followed">
              <ProjectsList addHeading={true} heading="Projects You Follow" apiEndpoint="api/projects?relation=followed"/>
            </ProtectedRoute>
            <ProtectedRoute exact path="/projects/:id">
              <Project />
            </ProtectedRoute>
            <ProtectedRoute exact path="/notifications">
              <ProjectRequestsList />
            </ProtectedRoute>
            <Route path="*">
              <NotFound404 />
            </Route>
          </Switch>
        </Container>
        <Footer />
      </div>
    </>
  ); 
};

export default App;
