import React, { useState, useContext } from 'react';
import { Link, useHistory } from 'react-router-dom';
/** my components */
import { AuthContext } from './context/AuthContextProvider';
/** Material UI Imports */
import { fade, makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import InputBase from '@material-ui/core/InputBase';
import Badge from '@material-ui/core/Badge';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import SearchIcon from '@material-ui/icons/Search';
import AccountCircle from '@material-ui/icons/AccountCircle';
import PeopleIcon from '@material-ui/icons/People';
import NotificationsIcon from '@material-ui/icons/Notifications';
import AssignmentIcon from '@material-ui/icons/Assignment';
import MoreIcon from '@material-ui/icons/MoreVert';
import HomeIcon from '@material-ui/icons/Home';
import PostAddIcon from '@material-ui/icons/PostAdd';
import Container from '@material-ui/core/Container';


/**
 * 
 * These styles are a modification of https://material-ui.com/components/app-bar/#app-bar-with-a-primary-search-field last accessed 06/05/21
 */
const useStyles = makeStyles((theme) => ({
  grow: {
    flexGrow: 1,
  },
  homeButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    display: 'none',
    [theme.breakpoints.up('sm')]: {
      display: 'block',
    },
  },
  search: {
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: fade(theme.palette.common.white, 0.15),
    '&:hover': {
      backgroundColor: fade(theme.palette.common.white, 0.25),
    },
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(3),
      width: 'auto',
    },
  },
  searchIcon: {
    padding: theme.spacing(0, 2),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inputRoot: {
    color: 'inherit',
  },
  inputInput: {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
    },
  },
  sectionDesktop: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'flex',
    },
  },
  sectionMobile: {
    display: 'flex',
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
  headerToolbar: {
      paddingLeft: 0,
      paddingRight: 0,
  },
}));

/**
 * 
 * The Header component is a modification of https://material-ui.com/components/app-bar/#app-bar-with-a-primary-search-field last accessed 06/05/21
 */
const Header = (props) => {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMoreAnchorEl, setMobileMoreAnchorEl] = useState(null);

  const isMenuOpen = Boolean(anchorEl);
  const isMobileMenuOpen = Boolean(mobileMoreAnchorEl);

  const authContext = useContext(AuthContext);
  const history = useHistory();

  const [projectSearchValue, setProjectSearchValue] = useState('');
  const [studentSearchValue, setStudentSearchValue] = useState('');

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMoreAnchorEl(null);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    handleMobileMenuClose();
  };

  const handleMobileMenuOpen = (event) => {
    setMobileMoreAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClick = (url) => {
    handleMobileMenuClose();
    history.push(url);
  };

  const handleMenuClick = (url) => {
    handleMenuClose();
    history.push(url);
  };

  const handleLogOut = () => {
    handleMenuClose();
    authContext.logOut();
  };

  const menuId = 'primary-search-account-menu';
  // profile menu
  const renderMenu = (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      id={menuId}
      keepMounted
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      open={isMenuOpen}
      onClose={handleMenuClose}
    >
      <MenuItem data-cy="profile-button" onClick={() => handleMenuClick(`/students/${authContext.studentId}`)}>Profile</MenuItem>
      <MenuItem data-cy="active-projects-button" onClick={() => handleMenuClick(`/projects/active`)}>Active Projects</MenuItem>
      <MenuItem data-cy="followed-projects-button" onClick={() => handleMenuClick(`/projects/followed`)}>Followed Projects</MenuItem>
      <MenuItem data-cy="logout-button" onClick={handleLogOut}>Logout</MenuItem>
    </Menu>
  );

  const mobileMenuId = 'primary-search-account-menu-mobile';
  const renderMobileMenu = (
    <Menu
      anchorEl={mobileMoreAnchorEl}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      id={mobileMenuId}
      keepMounted
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      open={isMobileMenuOpen}
      onClose={handleMobileMenuClose}
    >
      <MenuItem onClick={() => handleMobileMenuClick('/projects/new')}>
        <IconButton
          aria-label="create project"
          data-cy="create-project-button-mobile"
          color="inherit"
        >
          <PostAddIcon />
        </IconButton>
        <p>Create Project</p>
      </MenuItem>
      <MenuItem onClick={() => handleMobileMenuClick('/projects')}>
        <IconButton
          aria-label="all projects"
          data-cy="projects-button-mobile"
          color="inherit"
        >
          <AssignmentIcon />
        </IconButton>
        <p>Projects</p>
      </MenuItem>
      <MenuItem onClick={() => handleMobileMenuClick('/students')}>
        <IconButton
            aria-label="find students"
            color="inherit"
            data-cy="students-button-mobile"
        >
            <PeopleIcon />
        </IconButton>
        <p>Students</p>
      </MenuItem>
      <MenuItem onClick={() => handleMobileMenuClick('/notifications')}>
        <IconButton aria-label="show 0 new notifications" color="inherit">
          <Badge badgeContent={0} color="secondary">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <p>Notifications</p>
      </MenuItem>
      <MenuItem onClick={handleProfileMenuOpen}>
        <IconButton
          aria-label="account of current student"
          aria-controls="primary-search-account-menu"
          aria-haspopup="true"
          data-cy="account-button-mobile"
          color="inherit"
        >
          <AccountCircle />
        </IconButton>
        <p>Account</p>
      </MenuItem>
    </Menu>
  );

  /** handles input field change for project search */
  const handleProjectSearchOnChange = (event) => {
    setProjectSearchValue(event.target.value);
  }

  /** handles submission of project search input field */
  const handleProjectSearchSubmission = (event) => {
    event.preventDefault();
    document.getElementById('project-search').reset();

    history.push({
      pathname: `/projects`,
      search: `?search=${projectSearchValue}`,
    });
  }

  /** handles input field change for student search */
  const handleStudentSearchOnChange = (event) => {
    setStudentSearchValue(event.target.value);
  }

  /** handles submission of student search input field */
  const handleStudentSearchSubmission = (event) => {
    event.preventDefault();
    document.getElementById('student-search').reset();

    history.push({
      pathname: `/students`,
      search: `?search=${studentSearchValue}`,
    });
  }

  return (
    <div className={classes.grow}>
      <AppBar position="fixed">
          <Container>
            <Toolbar className={classes.headerToolbar}>
                <IconButton
                    edge="start"
                    className={classes.homeButton}
                    color="inherit"
                    aria-label="go to home page"
                    data-cy="home-button"
                    onClick={() => history.push('/')}
                >
                    <HomeIcon />
                </IconButton>
                <Typography className={classes.title} variant="h6" noWrap>
                    SPTB
                </Typography>
                {authContext.isAuthenticated && (
                  <>
                    <form id="project-search" onSubmit={handleProjectSearchSubmission}>
                      <div className={classes.search}>
                          <div className={classes.searchIcon}>
                            <SearchIcon />
                          </div>
                          <InputBase
                            placeholder="Projects by role"
                            classes={{
                                root: classes.inputRoot,
                                input: classes.inputInput,
                            }}
                            onChange={handleProjectSearchOnChange}
                            data-cy="project-search"
                          />
                      </div>
                    </form>
                    <form id="student-search" onSubmit={handleStudentSearchSubmission}>
                      <div className={classes.search}>
                          <div className={classes.searchIcon}>
                            <SearchIcon />
                          </div>
                          <InputBase
                            placeholder="Students by role"
                            classes={{
                                root: classes.inputRoot,
                                input: classes.inputInput,
                            }}
                            onChange={handleStudentSearchOnChange}
                            data-cy="student-search"
                          />
                      </div>
                    </form>
                    <div className={classes.grow} />
                    <div className={classes.sectionDesktop}>
                      <IconButton
                        aria-label="create project"
                        data-cy="create-project-button"
                        color="inherit"
                        onClick={() => history.push('/projects/new')}
                      >
                        <PostAddIcon />
                      </IconButton>
                      <IconButton
                        aria-label="all projects"
                        data-cy="projects-button"
                        color="inherit"
                        onClick={() => history.push('/projects')}
                      >
                        <AssignmentIcon />
                      </IconButton>
                      <IconButton
                          aria-label="find students"
                          data-cy="students-button"
                          color="inherit"
                          onClick={() => history.push('/students')}
                      >
                        <PeopleIcon />
                      </IconButton>
                      <IconButton
                        aria-label="show 0 new notifications"
                        data-cy="notifications-button"
                        color="inherit"
                        onClick={() => history.push('/notifications')}
                      >
                        <Badge badgeContent={0} color="secondary">
                          <NotificationsIcon />
                        </Badge>
                      </IconButton>
                      <IconButton
                        edge="end"
                        aria-label="account of current student"
                        aria-controls={menuId}
                        aria-haspopup="true"
                        data-cy="account-button"
                        onClick={handleProfileMenuOpen}
                        color="inherit"
                      >
                        <AccountCircle />
                      </IconButton>
                    </div>
                    <div className={classes.sectionMobile}>
                      <IconButton
                        aria-label="show more"
                        aria-controls={mobileMenuId}
                        aria-haspopup="true"
                        data-cy="mobile-more-button"
                        onClick={handleMobileMenuOpen}
                        color="inherit"
                      >
                        <MoreIcon />
                      </IconButton>
                    </div>
                  </>
                )}
            </Toolbar>
        </Container>
      </AppBar>
      {authContext.isAuthenticated && (
          <>
            {renderMobileMenu}
            {renderMenu}
          </>
      )}
    </div>
  );
}

export default Header;