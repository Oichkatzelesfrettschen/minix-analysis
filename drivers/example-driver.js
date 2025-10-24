/**
 * Example Driver Implementation
 *
 * This is a reference implementation showing how to create
 * custom Gemini browser drivers or helper utilities.
 *
 * @module drivers/example-driver
 */

'use strict';

const { URL } = require('url');

/**
 * Custom browser driver example
 *
 * This class demonstrates how to create custom functionality
 * that can be used with Gemini tests.
 */
class ExampleDriver {
  /**
   * Creates a new ExampleDriver instance
   * @param {Object} options - Configuration options
   * @param {string} options.baseUrl - Base URL for the application
   * @param {number} options.timeout - Default timeout in milliseconds
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || 'http://localhost:3000';
    this.timeout = options.timeout || 5000;
    this.initialized = false;
  }

  /**
   * Initialize the driver
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }

    console.log('[ExampleDriver] Initializing...');
    // Initialization logic here
    this.initialized = true;
    console.log('[ExampleDriver] Initialized successfully');
  }

  /**
   * Build a full URL from a path
   * @param {string} path - The path to append to base URL
   * @returns {string} Full URL
   */
  buildUrl(path) {
    const url = new URL(path, this.baseUrl);
    return url.href;
  }

  /**
   * Wait for a condition to be true
   * @param {Function} condition - Condition function to check
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<boolean>}
   */
  async waitFor(condition, timeout = this.timeout) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (await condition()) {
        return true;
      }
      await this.sleep(100);
    }

    throw new Error(`Timeout after ${timeout}ms waiting for condition`);
  }

  /**
   * Sleep for specified milliseconds
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise<void>}
   */
  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Clean up and destroy the driver
   * @returns {Promise<void>}
   */
  async destroy() {
    console.log('[ExampleDriver] Cleaning up...');
    this.initialized = false;
    // Cleanup logic here
  }
}

/**
 * Helper function to create page-specific helpers
 *
 * @param {Object} browser - Gemini browser instance
 * @returns {Object} Page helpers
 */
function createPageHelpers(browser) {
  return {
    /**
     * Wait for element to be visible
     * @param {string} selector - CSS selector
     * @param {number} timeout - Timeout in milliseconds
     */
    async waitForVisible(selector, timeout = 5000) {
      const startTime = Date.now();

      while (Date.now() - startTime < timeout) {
        try {
          const element = await browser.findElement(selector);
          if (element && (await element.isDisplayed())) {
            return element;
          }
        } catch (e) {
          // Element not found yet
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      throw new Error(`Element ${selector} not visible after ${timeout}ms`);
    },

    /**
     * Wait for element to be hidden
     * @param {string} selector - CSS selector
     * @param {number} timeout - Timeout in milliseconds
     */
    async waitForHidden(selector, timeout = 5000) {
      const startTime = Date.now();

      while (Date.now() - startTime < timeout) {
        try {
          const element = await browser.findElement(selector);
          if (!element || !(await element.isDisplayed())) {
            return true;
          }
        } catch (e) {
          // Element not found - that's what we want
          return true;
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
      }

      throw new Error(`Element ${selector} still visible after ${timeout}ms`);
    },

    /**
     * Scroll element into view
     * @param {string} selector - CSS selector
     */
    async scrollIntoView(selector) {
      await browser.executeScript(
        `document.querySelector('${selector}').scrollIntoView({ behavior: 'smooth', block: 'center' })`
      );
      await new Promise((resolve) => setTimeout(resolve, 300));
    },

    /**
     * Fill form fields
     * @param {Object} fields - Map of selector to value
     */
    async fillForm(fields) {
      for (const [selector, value] of Object.entries(fields)) {
        const element = await browser.findElement(selector);
        await element.clear();
        await element.sendKeys(value);
      }
    },

    /**
     * Take full page screenshot (scrolling)
     * @returns {Promise<Buffer>} Screenshot buffer
     */
    async takeFullPageScreenshot() {
      // Get page height
      const pageHeight = await browser.executeScript('return document.body.scrollHeight');
      const viewportHeight = await browser.executeScript('return window.innerHeight');

      const screenshots = [];
      let scrollTop = 0;

      // Capture screenshots while scrolling
      while (scrollTop < pageHeight) {
        await browser.executeScript(`window.scrollTo(0, ${scrollTop})`);
        await new Promise((resolve) => setTimeout(resolve, 200));

        const screenshot = await browser.takeScreenshot();
        screenshots.push(screenshot);

        scrollTop += viewportHeight;
      }

      // In a real implementation, you'd stitch these together
      // For this example, just return the first one
      return screenshots[0];
    },
  };
}

/**
 * Authentication helper
 *
 * @param {Object} browser - Gemini browser instance
 * @param {Object} credentials - User credentials
 * @returns {Promise<void>}
 */
async function login(browser, credentials) {
  const { username, password } = credentials;

  // Navigate to login page
  await browser.url('/login');

  // Fill login form
  await browser.findElement('#username').sendKeys(username);
  await browser.findElement('#password').sendKeys(password);

  // Submit form
  await browser.findElement('button[type="submit"]').click();

  // Wait for redirect
  await new Promise((resolve) => setTimeout(resolve, 1000));

  console.log('[Auth] Logged in successfully');
}

/**
 * Logout helper
 *
 * @param {Object} browser - Gemini browser instance
 * @returns {Promise<void>}
 */
async function logout(browser) {
  await browser.url('/logout');
  await new Promise((resolve) => setTimeout(resolve, 500));
  console.log('[Auth] Logged out successfully');
}

/**
 * Mock API response helper
 *
 * @param {Object} browser - Gemini browser instance
 * @param {string} endpoint - API endpoint to mock
 * @param {Object} response - Mock response data
 * @returns {Promise<void>}
 */
async function mockApiResponse(browser, endpoint, response) {
  await browser.executeScript(
    `
    window.fetch = new Proxy(window.fetch, {
      apply: function(target, thisArg, args) {
        const url = args[0];
        if (url.includes('${endpoint}')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(${JSON.stringify(response)})
          });
        }
        return Reflect.apply(target, thisArg, args);
      }
    });
  `
  );
}

// Export everything
module.exports = {
  ExampleDriver,
  createPageHelpers,
  login,
  logout,
  mockApiResponse,
};

/**
 * Usage Examples:
 *
 * // In your test file:
 * const { ExampleDriver, createPageHelpers } = require('../drivers/example-driver');
 *
 * gemini.suite('My Tests', (suite) => {
 *   const driver = new ExampleDriver({ baseUrl: 'http://localhost:3000' });
 *   const helpers = createPageHelpers(browser);
 *
 *   suite
 *     .before(async (actions) => {
 *       await driver.initialize();
 *     })
 *     .after(async (actions) => {
 *       await driver.destroy();
 *     })
 *     .capture('test', async (actions, find) => {
 *       await helpers.waitForVisible('.main-content');
 *       await helpers.scrollIntoView('.footer');
 *     });
 * });
 */
