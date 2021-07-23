context('Navigation', () => {
    const testStudentUsername = 'johndoe';
    
    describe('Desktop Nav', () => {
        // run once before all tests in this block
        before(() => {
            cy.logIn(testStudentUsername);
        });
    
        it('Can navigate to home page', () => {
            cy.get('[data-cy=home-button]').click();
            cy.url().should('eq',`${Cypress.config().baseUrl}/`);
        });
    
        it('Can find project search field and enter text', () => {
            cy.get('[data-cy=project-search]').type('Search is visible');
        });

        it('Can find student search field and enter text', () => {
            cy.get('[data-cy=student-search]').type('Search is visible');
        });
    
        it('Can navigate to students page', () => {
            cy.get('[data-cy=students-button]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students`);
        });
    
        it('Can navigate to profile page', () => {
            cy.get('[data-cy=account-button]').click();
            cy.get('[data-cy=profile-button]').click();
            cy.get('[data-cy=username]').should('have.text', testStudentUsername);
        });
    });

    describe('Tablet & Mobile Nav', () => {
        // run once before all tests in this block
        before(() => {
            cy.logIn(testStudentUsername);
        });

        beforeEach(() => {
            cy.viewport('ipad-2');
        });
    
        it('Can navigate to home page', () => {
            cy.get('[data-cy=home-button]').click();
            cy.url().should('eq',`${Cypress.config().baseUrl}/`);
        });
    
        it('Can find project search field and enter text', () => {
            cy.get('[data-cy=project-search]').type('Search is visible');
        });

        it('Can find student search field and enter text', () => {
            cy.get('[data-cy=student-search]').type('Search is visible');
        });
    
        it('Can navigate to students page', () => {
            cy.get('[data-cy=mobile-more-button]').click();
            cy.get('[data-cy=students-button-mobile]').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/students`);
        });
    
        it('Can navigate to profile page', () => {
            cy.get('[data-cy=mobile-more-button]').click();
            cy.get('[data-cy=account-button-mobile]').click();
            cy.get('[data-cy=profile-button]').click();
            cy.get('[data-cy=username]').should('have.text', testStudentUsername);
        });
    });
});