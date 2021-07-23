context('Authentication & Authorization', () => {
    const testStudentUsername = 'johndoe';
    const otherStudentId = 6;

    describe('Login & Logout', () => {
        it('Redirected to home page after logging in', () => {
            cy.logIn(testStudentUsername);
            cy.url().should('eq', `${Cypress.config().baseUrl}/`);
        });
    
        it('Has access and refresh tokens in local storage after logging in', () => {
            cy.logIn(testStudentUsername).should(() => {
                // need to run non-cy commands inside cy commands for correct execution order
                expect(localStorage.getItem('access_token'), 'access token in local storage').to.not.equal(null);
                expect(localStorage.getItem('refresh_token'), 'refresh token in local storage').to.not.equal(null);
            });
        });
    
        it('Cannot authenticate with incorrect credentials', () => {
            cy.logIn('thisusernamedoesnotexit').should(() => {
                expect(localStorage.getItem('access_token'), 'access token in local storage').to.equal(null);
                expect(localStorage.getItem('refresh_token'), 'refresh token in local storage').to.equal(null);
            });
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });
    
        it('Cannot access and submit login form after logging in', () => {
            cy.logIn(testStudentUsername);

            cy.visit(`/login`);
            cy.get('[data-cy=sign-in]').should('not.exist');
            cy.url().should('not.eq', `${Cypress.config().baseUrl}/login`);
        });
        
        it('Cannot log out via main navigation when not authenticated', () => {
            cy.visit('/');
            cy.get('[data-cy=account-button]').should('not.exist');
            cy.get('[data-cy=logout-button]').should('not.exist');
        });
        
        it('Can log out via desktop navigation', () => {
            cy.logIn(testStudentUsername);
            cy.get('[data-cy=account-button]').click();
            cy.get('[data-cy=logout-button]').click().should(() => {
                expect(localStorage.getItem('access_token'), 'access token in local storage').to.equal(null);
                expect(localStorage.getItem('refresh_token'), 'refresh token in local storage').to.equal(null);
            })
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });
    
        it('Can log out via tablet & mobile navigation', () => {
            cy.viewport('ipad-2');  // restrict viewport to ipad view
            cy.logIn(testStudentUsername);
            cy.get('[data-cy=mobile-more-button]').click();
            cy.get('[data-cy=account-button-mobile]').click();
            cy.get('[data-cy=logout-button]').click().should(() => {
                expect(localStorage.getItem('access_token'), 'access token in local storage').to.equal(null);
                expect(localStorage.getItem('refresh_token'), 'refresh token in local storage').to.equal(null);
            })
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });
    });

    describe('Unauthenticated Access Restrictions', () => {
        it('Redirected to login page when visiting home page', () => {
            cy.visit('/');
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });

        it('Redirected to login page when visiting students page', () => {
            cy.visit('/students');
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });

        it('Redirected to login page when visiting a student profile page', () => {
            cy.visit(`/students/${otherStudentId}`);
            cy.url().should('eq', `${Cypress.config().baseUrl}/login`);
        });
    });

    describe('Unauthorized Access Restrictions', () => {
        it('Unable to see the edit button on another student\'s profile', () => {
            cy.logIn(testStudentUsername);

            cy.visit(`/students/${otherStudentId}`);
            cy.get('[data-cy=edit-profile-button]').should('not.exist');
        });

        it('Unable to access another student\'s profile edit form', () => {
            cy.logIn(testStudentUsername);

            cy.visit(`/students/${otherStudentId}/edit`);
            cy.get('h1').should('have.text', 'Access Denied');
            cy.get('[data-cy=update-profile-button]').should('not.exist');
        });
    });
});