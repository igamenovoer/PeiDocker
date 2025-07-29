# How to Do Automatic Testing with Puppeteer

A comprehensive guide for automated testing with Puppeteer, including functionality testing, screenshot verification, and test reporting.

## Overview

Puppeteer is a Node.js library that provides a high-level API to control Chrome or Chromium browsers programmatically. It's ideal for automated testing, web scraping, and generating screenshots or PDFs of web pages.

## Setup and Installation

### Basic Installation

```bash
npm install puppeteer jest
# Optional: For visual regression testing
npm install jest-image-snapshot
```

### Project Structure

```
project/
├── tests/
│   ├── functional/
│   ├── visual/
│   └── __image_snapshots__/
├── reports/
├── screenshots/
├── jest.config.js
└── package.json
```

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-puppeteer',
  testMatch: ['**/tests/**/*.test.js'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testTimeout: 30000,
  reporters: [
    'default',
    ['jest-html-reporters', {
      publicPath: './reports',
      filename: 'test-report.html',
      expand: true
    }]
  ]
};
```

## Functionality Testing

### Basic Page Testing

```javascript
// tests/functional/login.test.js
describe('Login Functionality', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({ headless: false });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  test('should login successfully with valid credentials', async () => {
    await page.goto('https://example.com/login');
    
    // Fill form fields
    await page.type('#username', 'testuser');
    await page.type('#password', 'password123');
    
    // Click login button
    await page.click('#login-btn');
    
    // Wait for navigation
    await page.waitForNavigation();
    
    // Verify successful login
    const welcomeText = await page.$eval('.welcome', el => el.textContent);
    expect(welcomeText).toContain('Welcome');
  });
});
```

### Form Validation Testing

```javascript
test('should show validation errors for empty fields', async () => {
  await page.goto('https://example.com/contact');
  
  // Submit form without filling required fields
  await page.click('#submit-btn');
  
  // Check for validation messages
  const emailError = await page.$eval('#email-error', el => el.textContent);
  const nameError = await page.$eval('#name-error', el => el.textContent);
  
  expect(emailError).toBe('Email is required');
  expect(nameError).toBe('Name is required');
});
```

### API Response Testing

```javascript
test('should handle API responses correctly', async () => {
  // Intercept network requests
  await page.setRequestInterception(true);
  
  page.on('request', request => {
    if (request.url().includes('/api/users')) {
      request.respond({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ users: [{ id: 1, name: 'Test User' }] })
      });
    } else {
      request.continue();
    }
  });
  
  await page.goto('https://example.com/users');
  
  // Verify data is displayed
  await page.waitForSelector('.user-list');
  const userCount = await page.$$eval('.user-item', items => items.length);
  expect(userCount).toBe(1);
});
```

## Screenshot Testing and Visual Verification

### Basic Screenshot Capture

```javascript
// tests/visual/homepage.test.js
describe('Visual Testing', () => {
  test('should capture homepage screenshot', async () => {
    await page.goto('https://example.com');
    await page.waitForLoadState('networkidle');
    
    // Take full page screenshot
    await page.screenshot({
      path: 'screenshots/homepage-full.png',
      fullPage: true
    });
    
    // Take viewport screenshot
    await page.screenshot({
      path: 'screenshots/homepage-viewport.png',
      fullPage: false
    });
  });
});
```

### Element-Specific Screenshots

```javascript
test('should capture specific component screenshots', async () => {
  await page.goto('https://example.com');
  
  // Screenshot of specific element
  const header = await page.$('.header');
  await header.screenshot({ path: 'screenshots/header.png' });
  
  // Screenshot with custom viewport
  await page.setViewport({ width: 1920, height: 1080 });
  await page.screenshot({
    path: 'screenshots/desktop-view.png',
    clip: { x: 0, y: 0, width: 1920, height: 600 }
  });
});
```

### Visual Regression Testing

```javascript
// tests/visual/regression.test.js
import { toMatchImageSnapshot } from 'jest-image-snapshot';

expect.extend({ toMatchImageSnapshot });

describe('Visual Regression Tests', () => {
  test('homepage should match baseline', async () => {
    await page.goto('https://example.com');
    await page.waitForLoadState('networkidle');
    
    const screenshot = await page.screenshot();
    expect(screenshot).toMatchImageSnapshot({
      threshold: 0.2,
      customSnapshotIdentifier: 'homepage-baseline'
    });
  });
  
  test('mobile layout should match baseline', async () => {
    await page.setViewport({ width: 375, height: 667 });
    await page.goto('https://example.com');
    
    const screenshot = await page.screenshot({ fullPage: true });
    expect(screenshot).toMatchImageSnapshot({
      threshold: 0.1,
      customSnapshotIdentifier: 'mobile-homepage'
    });
  });
});
```

### Cross-Browser Visual Testing

```javascript
const devices = ['Desktop Chrome', 'iPhone 12', 'iPad'];

devices.forEach(device => {
  test(`should render correctly on ${device}`, async () => {
    if (device !== 'Desktop Chrome') {
      await page.emulate(puppeteer.devices[device]);
    }
    
    await page.goto('https://example.com');
    const screenshot = await page.screenshot();
    
    expect(screenshot).toMatchImageSnapshot({
      customSnapshotIdentifier: `${device.replace(/\s/g, '-')}-homepage`
    });
  });
});
```

## Advanced Testing Techniques

### Performance Testing

```javascript
test('should load page within performance budget', async () => {
  await page.goto('https://example.com');
  
  const metrics = await page.metrics();
  const loadTime = await page.evaluate(() => 
    performance.timing.loadEventEnd - performance.timing.navigationStart
  );
  
  expect(loadTime).toBeLessThan(3000); // 3 seconds
  expect(metrics.JSHeapUsedSize).toBeLessThan(50 * 1024 * 1024); // 50MB
});
```

### Accessibility Testing

```javascript
test('should pass accessibility checks', async () => {
  await page.goto('https://example.com');
  
  // Check for alt attributes on images
  const imagesWithoutAlt = await page.$$eval('img', imgs => 
    imgs.filter(img => !img.alt).length
  );
  expect(imagesWithoutAlt).toBe(0);
  
  // Check for proper heading hierarchy
  const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', 
    headings => headings.map(h => h.tagName)
  );
  expect(headings[0]).toBe('H1');
});
```

## Test Report Generation

### HTML Test Reports

```javascript
// package.json
{
  "scripts": {
    "test": "jest",
    "test:report": "jest --reporters=default --reporters=jest-html-reporters"
  },
  "jest-html-reporters": {
    "publicPath": "./reports",
    "filename": "test-report.html",
    "expand": true,
    "hideIcon": false,
    "pageTitle": "Puppeteer Test Report",
    "customInfos": [
      { "title": "Test Environment", "value": "QA" },
      { "title": "Browser", "value": "Chrome Headless" }
    ]
  }
}
```

### Allure Reports Integration

```javascript
// Install allure reporter
// npm install jest-allure

// jest.config.js
module.exports = {
  reporters: [
    'default',
    ['jest-allure', {
      outputDirectory: 'allure-results'
    }]
  ]
};

// In test files
describe('Login Tests', () => {
  test('successful login', async () => {
    // Add allure annotations
    await allure.feature('Authentication');
    await allure.story('User Login');
    await allure.severity('critical');
    
    // Test implementation
    await page.goto('https://example.com/login');
    // ... test steps
    
    // Attach screenshot to report
    const screenshot = await page.screenshot();
    await allure.attachment('Login Screenshot', screenshot, 'image/png');
  });
});
```

### Custom Report Generation

```javascript
// tests/utils/reporter.js
class CustomReporter {
  onRunComplete(contexts, results) {
    const report = {
      timestamp: new Date().toISOString(),
      totalTests: results.numTotalTests,
      passedTests: results.numPassedTests,
      failedTests: results.numFailedTests,
      duration: results.testResults.reduce((acc, result) => 
        acc + result.perfStats.runtime, 0
      ),
      screenshots: this.collectScreenshots(),
      failures: this.collectFailures(results)
    };
    
    fs.writeFileSync('reports/custom-report.json', JSON.stringify(report, null, 2));
    this.generateHTMLReport(report);
  }
  
  collectScreenshots() {
    return fs.readdirSync('screenshots').map(file => ({
      name: file,
      path: `screenshots/${file}`,
      timestamp: fs.statSync(`screenshots/${file}`).mtime
    }));
  }
}
```

## Test Report Contents

### Standard Test Report Elements

1. **Test Summary**
   - Total tests executed
   - Pass/fail counts
   - Test duration
   - Environment information

2. **Test Results**
   - Individual test status
   - Error messages and stack traces
   - Test execution time
   - Screenshots for failed tests

3. **Coverage Information**
   - Code coverage percentage
   - Uncovered lines
   - Coverage trends

4. **Performance Metrics**
   - Page load times
   - Memory usage
   - Network requests

5. **Visual Regression Results**
   - Baseline vs actual images
   - Difference highlights
   - Threshold violations

### Report Example Structure

```json
{
  "summary": {
    "total": 45,
    "passed": 42,
    "failed": 3,
    "duration": "2m 34s",
    "coverage": "87.3%"
  },
  "results": [
    {
      "suite": "Login Tests",
      "test": "should login with valid credentials",
      "status": "passed",
      "duration": "1.2s",
      "screenshots": ["login-success.png"]
    }
  ],
  "failures": [
    {
      "test": "should display error for invalid email",
      "error": "Expected error message not found",
      "screenshot": "error-state.png",
      "stackTrace": "..."
    }
  ],
  "visualRegression": {
    "totalComparisons": 12,
    "differences": 2,
    "newBaselines": 1
  }
}
```

## Best Practices

### Test Organization

```javascript
// tests/setup.js
global.testTimeout = 30000;
global.browser = null;
global.page = null;

beforeAll(async () => {
  global.browser = await puppeteer.launch({
    headless: process.env.CI === 'true',
    slowMo: process.env.CI ? 0 : 50,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
});

afterAll(async () => {
  if (global.browser) {
    await global.browser.close();
  }
});
```

### Error Handling and Debugging

```javascript
test('should handle errors gracefully', async () => {
  try {
    await page.goto('https://example.com');
    // Test implementation
  } catch (error) {
    // Capture screenshot on failure
    await page.screenshot({ 
      path: `screenshots/error-${Date.now()}.png` 
    });
    
    // Capture console logs
    const logs = await page.evaluate(() => console.getLog());
    console.log('Page logs:', logs);
    
    throw error;
  }
});
```

### Parallel Test Execution

```javascript
// jest.config.js
module.exports = {
  maxWorkers: 4,
  testTimeout: 30000,
  globalSetup: './tests/global-setup.js',
  globalTeardown: './tests/global-teardown.js'
};
```

## Common Testing Patterns

### Page Object Model

```javascript
// tests/pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = '#username';
    this.passwordInput = '#password';
    this.loginButton = '#login-btn';
  }
  
  async login(username, password) {
    await this.page.type(this.usernameInput, username);
    await this.page.type(this.passwordInput, password);
    await this.page.click(this.loginButton);
    await this.page.waitForNavigation();
  }
  
  async takeScreenshot(name) {
    await this.page.screenshot({ 
      path: `screenshots/${name}.png` 
    });
  }
}
```

### Data-Driven Testing

```javascript
const testData = [
  { username: 'user1', password: 'pass1', expected: 'success' },
  { username: 'user2', password: 'invalid', expected: 'error' },
  { username: '', password: 'pass', expected: 'validation' }
];

testData.forEach(({ username, password, expected }) => {
  test(`should handle login with ${username}`, async () => {
    await page.goto('https://example.com/login');
    // Test implementation using data
  });
});
```

## References and Resources

- [Puppeteer Official Documentation](https://pptr.dev/)
- [Jest Testing Framework](https://jestjs.io/)
- [Jest-Image-Snapshot for Visual Testing](https://github.com/americanexpress/jest-image-snapshot)
- [Jest-HTML-Reporters](https://github.com/Hazyzh/jest-html-reporters)
- [Allure Report Framework](https://allurereport.org/)
- [Puppeteer Visual Regression Testing Guide](https://www.browserstack.com/guide/visual-regression-testing-with-puppeteer)
- [End-to-End Testing with Jest and Puppeteer](https://www.loginradius.com/blog/engineering/e2e-testing-with-jest-puppeteer)

---

*This guide provides comprehensive coverage of Puppeteer testing capabilities, from basic functionality testing to advanced visual regression and reporting techniques.*
