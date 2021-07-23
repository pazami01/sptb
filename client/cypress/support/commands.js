/** Log in the student with the given username */
const logIn = (username) => {
    const testPassword = 'password123!';
    // spy on POST requests that include the substring in the url
    cy.intercept('POST', 'auth/token').as('logIn');

    cy.visit('/login');
    cy.get('[data-cy=username]').type(username);
    cy.get('[data-cy=password]').type(testPassword, { log: false });  // don't show the testPassword
    cy.get('[data-cy=sign-in]').click();

    // wait until the request with this alias finishes
    cy.wait('@logIn');
}

/** Custom commands */
Cypress.Commands.add('logIn', logIn);