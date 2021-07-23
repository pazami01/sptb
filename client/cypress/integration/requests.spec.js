context('Projects', () => {
    // test user 1 (project owner)
    const testStudentOneUsername = 'johndoe';
    const testStudentOneId = 4;
    // test user 2
    const testStudentTwoUsername = 'richardroe';
    const testStudentTwoId = 6;
    
    let testStudentOne = {};
    let testStudentTwo = {};
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

    
    before(() => {
        cy.logIn(testStudentOneUsername)
            .then(() => {  // fetch the data for testStudentOne
                cy.request({
                    url: `http://localhost:8000/api/accounts/${testStudentOneId}`,
                    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
                })
                .then(response => {
                    testStudentOne = response.body;  // store data
                });
            })  
            .then(() => {  // fetch the data for testStudentTwo
                cy.request({
                    url: `http://localhost:8000/api/accounts/${testStudentTwoId}`,
                    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
                })
                .then(response => {
                    testStudentTwo = response.body;
                });
            })  
            .then(() => {  // create a test project owned by testStudentOne for all tests
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

            cy.get('[data-cy=account-button]').click();
            cy.get('[data-cy=logout-button]').click();  // log out
    });

    after(() => {
        // log in as the project owner and delete the project
        cy.logIn(testStudentOne.username).then(() => {
            cy.visit(`/projects/${testProject.id}`);
            // delete the project
            cy.get('[data-cy=open-delete-project-dialog-button]').click();
            cy.get('[data-cy=delete-project-button]').click();
        });
    });

    describe('requests', () => {
        it('Project owner can send another student an invitation to join as a member', () => {
            const invitationRole = 'Test Role';

            // log in as testStudentOne (project owner)
            cy.logIn(testStudentOne.username);

            // visit testStudentTwo's profile page
            cy.visit(`/students/${testStudentTwo.id}`);
            cy.get('[data-cy=request-join-project-button]').click();
            // enter the role you want them to take
            cy.get('[data-cy=project_role] input[name="project_role"]').type(invitationRole);
            // select the project you want them to join
            cy.get('[data-cy=project]').click()
                .get(`[data-cy=${testProject.id}]`).click();
            
            // spy on any requests to the server for creating join requests
            cy.intercept('POST', 'api/requests/').as('createRequest');
            
            // send the invitation to testStudentTwo
            cy.get('[data-cy=send-invitation-button').click();

            // wait for the server to respond
            cy.wait('@createRequest').then((interception) => {
                // store join request ID
                const requestId = interception.response.body.id;

                // log out as testStudentOne
                cy.get('[data-cy=account-button]').click();
                cy.get('[data-cy=logout-button]').click();
                // log in as testStudentTwo
                cy.logIn(testStudentTwo.username);
                cy.visit('/notifications');
                // accept the invitation to join project
                cy.get(`[data-cy=request-${requestId}-accept-button]`).click();

                // visit the project page
                cy.visit(`/projects/${testProject.id}`);
                // full name should show up as a member
                cy.get(`[data-cy=member-${testStudentTwo.id}-name] span`).should('have.text', `${testStudentTwo.first_name} ${testStudentTwo.last_name}`);
                // member role should match the role in the invitation
                cy.get(`[data-cy=member-${testStudentTwo.id}-role] span`).should('have.text', invitationRole);

                // log out
                cy.get('[data-cy=account-button]').click();
                cy.get('[data-cy=logout-button]').click();
            });
        });

        it('Student can leave a project where they are a member', () => {
            // log in as testStudentTwo (member)
            cy.logIn(testStudentTwo.username);

            cy.visit(`/projects/${testProject.id}`);
            // leave project
            cy.get('[data-cy=leave-project-button]').click();
            cy.visit(`/projects/${testProject.id}`);
            cy.get(`[data-cy=member-${testStudentTwo.id}-name]`).should('not.exist');

            // log out
            cy.get('[data-cy=account-button]').click();
            cy.get('[data-cy=logout-button]').click();
        });

        it('Student can request to join a project as a member', () => {
            const requestRole = "Test Role 2";

            // log in as testStudentTwo (member)
            cy.logIn(testStudentTwo.username);

            cy.visit(`/projects/${testProject.id}`);
            // open dialog window
            cy.get('[data-cy=join-project-button]').click();
            // enter role
            cy.get('[data-cy=requested-role] input[name="role"]').type(requestRole);
            
            // spy on any requests to the server for creating join requests
            cy.intercept('POST', 'api/requests/').as('sendRequest');
            
            // send request
            cy.get('[data-cy=send-request-button]').click();

            // wait for the server to respond
            cy.wait('@sendRequest').then((interception) => {
                const requestId = interception.response.body.id;

                // log out as testStudentTwo
                cy.get('[data-cy=account-button]').click();
                cy.get('[data-cy=logout-button]').click();
                // log in as testStudentOne
                cy.logIn(testStudentOne.username);
                cy.visit('/notifications');
                // accept the request to join project
                cy.get(`[data-cy=request-${requestId}-accept-button]`).click();
            });

            cy.get('[data-cy=account-button]').click();
            cy.get('[data-cy=logout-button]').click();
        });
    });
});