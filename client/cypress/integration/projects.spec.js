context('Projects', () => {
    const testStudentUsername = 'johndoe';
    const testStudentId = 4;
    
    let testStudent = {};
    let testProject = {};

    const testProjectPostData = {
        title: 'Test Project Title',
        description: 'Test description text.',
        category: 'ART',
        owner_role: 'Test Owner Role',
        desired_roles: [
            "Test Desired Role 1",
            "Test Desired Role 2"
        ]
    };

    // Fetch the student data that will be used for the tests
    before(() => {
        cy.logIn(testStudentUsername).should(() => {
            cy.request({
                url: `http://localhost:8000/api/accounts/${testStudentId}/`,
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
            })
            .then(response => {
                testStudent = response.body;
            });
        })  // create a test project for all tests
        .then(() => {
            cy.request({
                method: 'POST',
                url: `http://localhost:8000/api/projects/`,
                body: testProjectPostData,
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
            })
            .then(response => {
                testProject = response.body;
            });
        });
    });

    // Delete test project after all tests have run
    after(() => {
        cy.request({
            method: 'DELETE',
            url: `http://localhost:8000/api/projects/${testProject.id}/`,
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
        });
    });

    describe('Project Create Page', () => {
        const tempProject = {
            title: 'Temp Project Title',
            description: 'Temp description text.',
            category: 'SFW',
            owner_role: 'Temp Owner Role',
            desired_roles: [
                "Temp Desired Role 1",
                "Temp Desired Role 2"
            ]
        };

        it('Can view create project page', () => {
            // navigate to form for creating a new project
            cy.get('[data-cy=create-project-button]').should('exist').click();
            // check url
            cy.url().should('eq', `${Cypress.config().baseUrl}/projects/new`);
            cy.get('[data-cy=submit-create-project-button]').should('exist');
        });

        it('Can create and delete project', () => {
            // navigate to form for creating a new project
            cy.get('[data-cy=create-project-button]').click();
            // add title
            cy.get('[data-cy=title] input[name="title"]').should('exist')
                .type(tempProject.title);
            // add description
            cy.get('[data-cy=description] textarea[name="description"]')
                .should('exist').type(tempProject.description);
            // select category
            cy.get('[data-cy=category] #category').should('exist').click()
                .get(`[data-cy=${tempProject.category}`).click();
            // add owner role
            cy.get('[data-cy=owner_role] input[name="owner_role"]')
                .should('exist').type(tempProject.owner_role);
            // add input field for desired role
            cy.get('[data-cy=add-role-button]').should('exist').click();
            // add first desired role
            cy.get('[data-cy=desired_role-0] input[name="desired_roles.0"]')
                .should('exist').type(tempProject.desired_roles[0]);
            cy.get('[data-cy=add-role-button]').click();
            // add second desired role
            cy.get('[data-cy=desired_role-1] input[name="desired_roles.1"]')
                .should('exist').type(tempProject.desired_roles[1]);
            // submit
            cy.get('[data-cy=submit-create-project-button]').should('exist').click();

            // delete the project
            cy.get('[data-cy=open-delete-project-dialog-button]').should('exist').click();
            cy.get('[data-cy=delete-project-button]').should('exist').click();
        });
    });

    describe('All Projects Page', () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit('/projects');
        });

        it(`Can find a particular project in a list of all projects`, () => {
            cy.get('[data-cy=projects-container]');
            cy.get(`[data-cy=project-${testProject.id}-name]`).should('have.text', testProject.title);
        });

        it(`Can click through to a particular project page`, () => {
            cy.get(`[data-cy=project-${testProject.id}-button]`).should('exist').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/projects/${testProject.id}`);
            cy.get('[data-cy=title]').should('have.text', testProject.title);
        });
    });

    describe(`Project Page`, () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit(`/projects/${testProject.id}`);
        });

        it(`Can see title`, () => {
            cy.get('[data-cy=title]').should('have.text', testProject.title);
        });
    
        it(`Can see description`, () => {
            cy.get('[data-cy=description]').should('have.text', testProject.description);
        });
    
        it(`Can see category`, () => {
            const categoryName = 'Art';

            cy.get('[data-cy=category]').should('include.text', categoryName);
        });
    
        it(`Can see owner role`, () => {
            cy.get('[data-cy=owner-role]').should('include.text', testProject.owner_role);
        });
    
        it(`Can see desired roles`, () => {
            testProject.desired_roles.map((role, index) => {
                cy.get(`[data-cy=role-${index}]`).should('include.text', role);
            });
        });
    });

    describe(`Project Update Page`, () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit(`/projects/${testProject.id}`);
            // access edit form
            cy.get('[data-cy=edit-project-button]').click();
        });

        it('Can see update button', () => {
            cy.get('[data-cy=update-project-button]').should('exist');
        });

        it('Can see cancel button', () => {
            cy.get('[data-cy=cancel-update-project-button]').should('exist');
        });

        it('Cancelling update does not change project', () => {
            const originalTitle = testProject.title;
            const newTitle = 'this change should not go through';

            cy.get('[data-cy=title] input[name="title"]').clear().type(newTitle);
            cy.get('[data-cy=cancel-update-project-button]').click();
            // should be redirected to the project view page
            cy.url().should('eq', `${Cypress.config().baseUrl}/projects/${testProject.id}`);
            // title shouldn't have changed
            cy.get('[data-cy=title]').should('have.text', originalTitle);
        });

        it('Can update project', () => {
            const newProjectData = {
                title: 'New Test Project Title',
                description: 'New Test description text.',
                category: 'SFW',
                category_name: 'Software',
                owner_role: 'New Test Owner Role',
                desired_roles: [
                    "New Test Desired Role 1",
                    "New Test Desired Role 2"
                ]
            };

            // check each field exists, then clear and add new values
            cy.get('[data-cy=title] input[name="title"]').should('exist').clear().type(newProjectData.title);
            cy.get('[data-cy=description] textarea[name="description"]').should('exist').clear().type(newProjectData.description);
            cy.get('[data-cy=category] #category').should('exist').click()
                .get(`[data-cy=${newProjectData.category}`).click();
            cy.get('[data-cy=owner_role] input[name="owner_role"]').should('exist').clear().type(newProjectData.owner_role);
            cy.get('[data-cy=desired_role-0] input[name="desired_roles.0"]').should('exist').clear().type(newProjectData.desired_roles[0]);
            cy.get('[data-cy=desired_role-1] input[name="desired_roles.1"]').should('exist').clear().type(newProjectData.desired_roles[1]);

            // submit changes
            cy.get('[data-cy=update-project-button]').click();
            
            // should be redirected to the project view page
            cy.url().should('eq', `${Cypress.config().baseUrl}/projects/${testProject.id}`);
            
            // all project data should have changed
            cy.get('[data-cy=title]').should('have.text', newProjectData.title);
            cy.get('[data-cy=description]').should('have.text', newProjectData.description);
            cy.get('[data-cy=category]').should('include.text', newProjectData.category_name);
            cy.get('[data-cy=owner-role]').should('include.text', newProjectData.owner_role);
            cy.get('[data-cy=role-0]').should('include.text', newProjectData.desired_roles[0]);
            cy.get('[data-cy=role-1]').should('include.text', newProjectData.desired_roles[1]);
        });
    });
});