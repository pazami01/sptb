context('Students', () => {
    const testStudentUsername = 'johndoe';
    const testStudentId = 4;
    let testStudent = {};

    // Fetch the student data that will be used for the tests
    before(() => {
        // login and then get test student data
        cy.logIn(testStudentUsername).should(() => {
            cy.request({
                url: `http://localhost:8000/api/accounts/${testStudentId}`,
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
            })
            .then(response => {
                testStudent = response.body;
            });
        });

        cy.get('[data-cy=account-button]').click();
        cy.get('[data-cy=logout-button]').click();  // logout
    });

    describe('All Students Page', () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit('/students');
        });

        it(`Can find a particular student in a list of all students`, () => {
            cy.get('[data-cy=students-container]');
            cy.get(`[data-cy=student-${testStudent.id}-name]`).should('have.text', `${testStudent.first_name} ${testStudent.last_name}`);
        });

        it(`Can click through to a particular student's profile page`, () => {
            cy.get(`[data-cy=student-${testStudent.id}-button]`).click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=full-name]').should('have.text', `${testStudent.first_name} ${testStudent.last_name}`);
        });
    });

    describe(`Student Profile Page`, () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit(`/students/${testStudent.id}`);
        });

        it(`Can see full name`, () => {
            cy.get('[data-cy=full-name]').should('have.text', `${testStudent.first_name} ${testStudent.last_name}`);
        });

        it(`Can see username`, () => {
            cy.get('[data-cy=username]').should('have.text', testStudent.username);
        });

        it(`Can see email`, () => {
            cy.get('[data-cy=email]').should('have.text', testStudent.email);
        });

        it(`Can see programme`, () => {
            cy.get('[data-cy=programme]').should('have.text', testStudent.profile.programme);
        });

        it(`Can see about`, () => {
            cy.get('[data-cy=about]').should('have.text', testStudent.profile.about);
        });

        it(`Can see roles`, () => {
            testStudent.profile.roles.map((role, index) => {
                cy.get(`[data-cy=role-${index}]`).should('include.text', role);
            });
        });
    });

    describe(`Student Profile Update Page`, () => {
        beforeEach(() => {
            cy.logIn(testStudent.username);
            cy.visit(`/students/${testStudent.id}/edit`);
        });

        it('Can view profile update page', () => {
            cy.get('[data-cy=update-profile-button]').should('exist');
        });
        
        it('Redirected to profile page after update', () => {
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
        });
        
        it('Redirected to profile page after cancelling update', () => {
            cy.get('[data-cy=cancel-update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
        });
        
        it('Cancelling update does not change profile', () => {
            const originalProgramme = testStudent.profile.programme;

            cy.get('[data-cy=programme] input[name="programme"]').clear().type(`this change should not go through`);
            cy.get('[data-cy=cancel-update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=programme]').should('have.text', originalProgramme);
        });

        it('Can update programme', () => {
            // list of programmes
            const programmes = ['MSc Mathematics', 'BSc Economics', 'BSc Statistics']
            const randomIndex = Math.floor(Math.random() * programmes.length);
            // select a random programme
            const programme = programmes[randomIndex];

            cy.get('[data-cy=programme] input[name="programme"]').clear().type(programme);
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=programme]').should('have.text', programme);
        });

        it('Can update about', () => {
            // list of bios
            const bios = [
                'Lorem ipsum dolor sit amet.',
                'Ut enim ad minim veniam.',
                'Duis aute irure dolor in reprehenderit in voluptate.'
            ]
            const randomIndex = Math.floor(Math.random() * bios.length);
            // select a random bio
            const bio = bios[randomIndex];

            cy.get('[data-cy=about] textarea[name="about"]').clear().type(bio);
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=about]').should('have.text', bio);
        });

        it('Can update role', () => {
            // list of roles
            const roles = ['Accountant', 'Data Analyst', 'Machine Learning Engineer']
            const randomIndex = Math.floor(Math.random() * roles.length);
            // select a random programme
            const role = roles[randomIndex];

            cy.get(`[data-cy=role-0] input[name="roles.0"]`).clear().type(role);
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=role-0]').should('contain.text', role);
        });

        it('Can add new role', () => {
            const newRole = 'Test Role';

            cy.get('[data-cy=add-role-button]').click();
            cy.get(`[data-cy=role-2] input[name="roles.2"]`).clear().type(newRole);
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=role-2]').should('contain.text', newRole);
        });

        it('Can remove role', () => {
            cy.get('[data-cy=remove-role-2-button]').click();
            cy.get('[data-cy=update-profile-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudent.id}`);
            cy.get('[data-cy=role-2]').should('not.exist');
        });
    });
});