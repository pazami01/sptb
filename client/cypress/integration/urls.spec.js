describe('Urls', () => {
    const testStudentUsername = 'johndoe';
    const testStudentId = 4;
    const otherStudentId = 6;
    const projectId = 7;

    beforeEach(() => {
        cy.logIn(testStudentUsername);
    });

    it(`Can access home page @ ${Cypress.config().baseUrl}/`, () => {
        const pageHeading = 'Welcome to the project team builder application!';

        cy.visit('/');
        cy.url().should('eq', `${Cypress.config().baseUrl}/`);
        cy.get('h1').should('have.text', pageHeading);
    });

    it(`Can access students page @ ${Cypress.config().baseUrl}/students`, () => {
        const pageHeading = 'Students';

        cy.visit('/students');
        cy.url().should('eq', `${Cypress.config().baseUrl}/students`);
        cy.get('h1').should('have.text', pageHeading);
    });

    it(`Can access another student\'s profile page @ ${Cypress.config().baseUrl}/students/${otherStudentId}`, () => {
        cy.visit(`/students/${otherStudentId}`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/students/${otherStudentId}`);
        cy.get('[data-cy=username-label]').should('have.text', 'Username');
    });

    it(`Can access profile edit form @ ${Cypress.config().baseUrl}/students/${testStudentId}/edit`, () => {
        cy.visit(`/students/${testStudentId}/edit`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/students/${testStudentId}/edit`);
        cy.get('[data-cy=update-profile-button]').should('exist');
    });

    it(`Display custom 404 page when accessing an invalid url e.g. ${Cypress.config().baseUrl}/shop`, () => {
        cy.visit('/shop');
        cy.get('h1').should('have.text', 'Page Not Found');
    });

    it(`Can access projects page @ ${Cypress.config().baseUrl}/projects`, () => {
        const pageHeading = 'Projects';

        cy.visit('/projects');
        cy.url().should('eq', `${Cypress.config().baseUrl}/projects`);
        cy.get('h1').should('have.text', pageHeading);
    });

    it(`Can access specific project page @ ${Cypress.config().baseUrl}/projects/${projectId}`, () => {
        const projectHeading = 'Location Sensor';

        cy.visit(`/projects/${projectId}`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/projects/${projectId}`);
        cy.get('h1').should('have.text', projectHeading);
    });

    it(`Can access active projects page @ ${Cypress.config().baseUrl}/projects/active`, () => {
        const pageHeading = 'Your Active Projects';

        cy.visit(`/projects/active`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/projects/active`);
        cy.get('h1').should('have.text', pageHeading);
    });

    it(`Can access followed projects page @ ${Cypress.config().baseUrl}/projects/followed`, () => {
        const pageHeading = 'Projects You Follow';

        cy.visit(`/projects/followed`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/projects/followed`);
        cy.get('h1').should('have.text', pageHeading);
    });

    it(`Can access notifications page @ ${Cypress.config().baseUrl}/notifications`, () => {
        const pageHeading = 'Your Project Requests';

        cy.visit(`/notifications`);
        cy.url().should('eq', `${Cypress.config().baseUrl}/notifications`);
        cy.get('h1').should('have.text', pageHeading);
    });
});