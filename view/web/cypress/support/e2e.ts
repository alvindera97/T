// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "./commands";

// Alternatively you can use CommonJS syntax:
// require('./commands')

if (!crypto.randomUUID) {
  crypto.randomUUID = () => {
    return ([1e7].toString() + "-1e3-4e3-8e3-1e11").replace(/[018]/g, (c) => {
      const random = crypto.getRandomValues(new Uint8Array(1))[0];
      return (
        parseInt(c, 16) ^
        (random & (15 >> (parseInt(c, 16) / 4)))
      ).toString(16);
    }) as `${string}-${string}-${string}-${string}-${string}`;
  };
}

export const chatUUID = crypto.randomUUID();
