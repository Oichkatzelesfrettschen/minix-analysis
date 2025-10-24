/**
 * Example Gemini Visual Regression Test
 *
 * This is a sample test demonstrating how to write Gemini tests
 * for visual regression testing.
 *
 * @see https://github.com/gemini-testing/gemini
 */

const gemini = require('gemini');

/**
 * Example Test Suite
 *
 * This suite demonstrates basic visual regression testing patterns
 */
gemini.suite('Example Page', (suite) => {
  suite
    .setUrl('https://example.com')
    .setCaptureElements('body')
    .ignoreElements('.dynamic-content')
    .capture('plain', function(actions, find) {
      // Capture the page in its default state
      // No actions needed - just capture
    })
    .capture('scrolled', function(actions, find) {
      // Capture after scrolling
      actions.executeJS(function(window) {
        window.scrollTo(0, 500);
      });
    });
});

/**
 * Homepage Test Suite
 *
 * Tests for homepage elements and interactions
 */
gemini.suite('Homepage', (suite) => {
  suite
    .setUrl('/')
    .setCaptureElements('.main-content')
    .before(function(actions) {
      // Wait for page to be fully loaded
      actions.wait(1000);
    })
    .capture('default state')
    .capture('hover state', function(actions, find) {
      // Test hover interaction
      const button = find('.cta-button');
      actions.mouseMove(button);
    })
    .capture('active state', function(actions, find) {
      // Test active/click state
      const button = find('.cta-button');
      actions.click(button);
      actions.wait(500);
    });
});

/**
 * Responsive Design Test
 *
 * Tests different viewport sizes
 */
gemini.suite('Responsive Homepage', (suite) => {
  suite
    .setUrl('/')
    .setCaptureElements('body')
    .capture('desktop', function(actions) {
      // Desktop size already set in .gemini.yml
    })
    .capture('tablet', function(actions) {
      actions.setWindowSize(768, 1024);
      actions.wait(300);
    })
    .capture('mobile', function(actions) {
      actions.setWindowSize(375, 667);
      actions.wait(300);
    });
});

/**
 * Form Interaction Test
 *
 * Tests form states and validation
 */
gemini.suite('Contact Form', (suite) => {
  suite
    .setUrl('/contact')
    .setCaptureElements('.contact-form')
    .capture('empty form')
    .capture('filled form', function(actions, find) {
      const nameInput = find('input[name="name"]');
      const emailInput = find('input[name="email"]');
      const messageInput = find('textarea[name="message"]');

      actions
        .sendKeys(nameInput, 'John Doe')
        .sendKeys(emailInput, 'john@example.com')
        .sendKeys(messageInput, 'This is a test message');
    })
    .capture('validation errors', function(actions, find) {
      const submitButton = find('button[type="submit"]');
      actions.click(submitButton);
      actions.wait(500);
    });
});
