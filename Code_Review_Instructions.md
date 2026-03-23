# Automation Code Review Checklist
### Selenium + Java + Cucumber

> **Purpose:** This document serves as an exhaustive code review guide for automation engineers. Use it during Pull Request reviews, peer code reviews, or self-assessments to ensure scripts adhere to best practices.

---

## 1. Project Structure & Organization

- [ ] Feature files are organized under `src/test/resources` with a logical folder hierarchy (by module/feature)
- [ ] Step definitions are in `src/test/java` and mapped to the correct package structure
- [ ] Page Object classes are separated from step definitions
- [ ] Utilities, constants, and config readers are in dedicated packages (e.g., `utils`, `config`, `constants`)
- [ ] No business logic exists inside step definition classes

---

## 2. Cucumber / BDD Best Practices

- [ ] Feature files follow proper **Gherkin syntax** (Given / When / Then / And / But)
- [ ] Scenarios describe **business behavior**, not technical implementation
  - ❌ `Click the login button`
  - ✅ `User logs into the application`
- [ ] No UI-level implementation details are leaked into feature files
- [ ] `Background` is used for common preconditions instead of repeating steps across scenarios
- [ ] `Scenario Outline` + `Examples` is used for data-driven scenarios instead of duplicating scenarios
- [ ] Tags (`@smoke`, `@regression`, `@sanity`, `@wip`) are applied correctly and consistently
- [ ] Each scenario is **independent** and does not rely on state from a previous scenario
- [ ] Scenarios are **atomic** — one behavior tested per scenario
- [ ] No hardcoded test data directly in feature files (use `Examples` table or external data sources)
- [ ] Feature files have meaningful `Feature` and `Scenario` titles

---

## 3. Page Object Model (POM)

- [ ] Every page or component has its own dedicated Page Object class
- [ ] No `driver.findElement()` calls exist inside step definitions — all locators are in Page Objects
- [ ] Page Object methods return meaningful types (`void`, `String`, or another Page Object for fluent chaining)
- [ ] Page Object classes do **not** contain assertions — assertions belong in step definitions or a dedicated assertion layer
- [ ] Page Object constructors use `PageFactory.initElements()` or explicit element initialization
- [ ] No business logic is mixed with UI interaction logic inside Page Object classes

---

## 4. Locator Strategy

- [ ] Locators follow the **priority order**: ID → Name → CSS Selector → XPath
- [ ] **Absolute XPaths are avoided** (e.g., `/html/body/div[1]/div[2]/...`) — relative XPaths are used instead
- [ ] CSS selectors are preferred over XPath wherever possible (better performance)
- [ ] Locators are stored as `@FindBy` annotations or `By` constants — **not hardcoded inline**
- [ ] Locator variable names are **descriptive** (e.g., `loginButton`, `usernameField`, `errorMessageLabel`)
- [ ] Dynamic locators use `String.format()` or dedicated builder methods cleanly

---

## 5. Synchronization & Waits

- [ ] **No `Thread.sleep()` exists anywhere in the codebase**
- [ ] `WebDriverWait` with `ExpectedConditions` is used consistently
- [ ] A **centralized wait utility** exists (e.g., `WaitUtils.java`) — waits are not duplicated across classes
- [ ] Implicit waits and explicit waits are **not mixed** (causes unpredictable behavior)
- [ ] Fluent waits are used for polling scenarios where element presence is intermittent
- [ ] Wait timeouts use **named constants**, not magic numbers (e.g., `WAIT_TIMEOUT_SECONDS = 30`)

---

## 6. Java Code Quality

- [ ] Classes and methods follow the **Single Responsibility Principle (SRP)**
- [ ] Method names are **verb-based** and clearly describe their action (e.g., `clickLoginButton()`, `enterUsername()`)
- [ ] No methods are longer than ~30 lines — large methods are refactored into smaller helpers
- [ ] No **magic numbers or hardcoded strings** — constants or enums are used instead
- [ ] Proper **access modifiers** are used (`private`, `protected`, `public`) appropriately
- [ ] No unused imports, variables, or dead code exists
- [ ] `static` is not overused — WebDriver is not made static unless using a thread-safe `ThreadLocal` approach
- [ ] **Exception handling** is proper — no empty `catch` blocks, no silently swallowed exceptions
- [ ] Custom exceptions are used where appropriate (e.g., `ElementNotFoundException`)
- [ ] Code follows standard **Java naming conventions**:
  - `camelCase` for methods and variables
  - `PascalCase` for class names
  - `UPPER_SNAKE_CASE` for constants

---

## 7. WebDriver Management

- [ ] `WebDriver` is **not static** unless using a thread-safe `ThreadLocal<WebDriver>` approach
- [ ] Driver initialization and teardown are handled in **Cucumber hooks** (`@Before` / `@After`), not in test classes
- [ ] `driver.quit()` is called in the `@After` hook to prevent browser/session leaks
- [ ] A **Driver Factory pattern** is implemented to support multiple browsers
- [ ] Browser type is driven by **configuration** (e.g., `config.properties` or environment variable), not hardcoded

---

## 8. Cucumber Hooks

- [ ] `@Before` and `@After` hooks are in a dedicated `Hooks.java` class
- [ ] Hooks use **tag filters** where needed (e.g., `@Before("@ui")`) to avoid unnecessary setup/teardown
- [ ] Screenshots on failure are captured in the `@After` hook and attached to the Cucumber report
- [ ] No business logic exists inside hook methods

---

## 9. Configuration Management

- [ ] All environment-specific values (URLs, credentials, timeouts) are in **external config files** (`.properties`, `.yml`)
- [ ] A `ConfigReader` utility class reads all config properties — no scattered `System.getProperty()` calls
- [ ] No **hardcoded URLs, credentials, or environment-specific data** exist anywhere in the code
- [ ] Sensitive data (passwords, API tokens) are passed via **environment variables or CI/CD secrets** and never committed to the repository

---

## 10. Test Data Management

- [ ] Test data is **externalized** (Excel, JSON, CSV, or database) — not hardcoded in step definitions
- [ ] A `TestDataProvider` or equivalent utility handles test data loading
- [ ] Test data is **cleaned up** after each test run (especially for data-creating tests)
- [ ] Unique data strategies (timestamps, UUIDs) are used to avoid conflicts during parallel runs

---

## 11. Reporting & Logging

- [ ] A reporting framework is integrated: **Extent Reports**, **Allure**, or **Cucumber HTML Reports**
- [ ] Logging uses a proper framework (**Log4j** / **SLF4J**) — no `System.out.println()` in production code
- [ ] Screenshots are captured on **test failure** and embedded into the report
- [ ] Step-level logging is present for traceability and debugging

---

## 12. Parallel Execution

- [ ] Tests are designed to be **thread-safe** — no shared mutable state between threads
- [ ] `ThreadLocal<WebDriver>` is used to isolate WebDriver instances per thread
- [ ] The **TestNG / JUnit runner** or Cucumber's parallel plugin is configured correctly
- [ ] No hardcoded file paths or shared resources that would cause race conditions during parallel runs

---

## 13. Test Runner Configuration

- [ ] Runner class uses correct `@CucumberOptions` with proper `features`, `glue`, `plugin`, and `tags` values
- [ ] `dryRun` is set to `false` in committed code (used only locally to verify step bindings)
- [ ] `monochrome: true` is set for clean, readable console output
- [ ] Tag expressions correctly filter scenarios for different suites (e.g., `@smoke and not @wip`)

---

## 14. Reusability & DRY Principle

- [ ] Common actions (login, navigation, setup) are in **shared step definitions or utility methods** — not duplicated
- [ ] Repeated locator logic is extracted into helper methods
- [ ] Utility classes exist for repeated low-level Selenium operations:
  - `AlertUtils`
  - `JavaScriptUtils`
  - `DropdownUtils`
  - `WaitUtils`

---

## 15. Assertions

- [ ] Assertions use a proper library: **AssertJ**, **Hamcrest**, or JUnit/TestNG's built-in assertions
- [ ] **Soft assertions** (e.g., `SoftAssert`, `SoftAssertions`) are used when multiple checks must run without stopping on first failure
- [ ] Assertion failure messages are **descriptive** (e.g., `"Expected login success banner to be visible after valid credentials"`)
- [ ] No assertions exist inside Page Object classes — they belong in step definitions or an assertion layer

---

## 16. Version Control Hygiene

- [ ] No **credentials, API keys, or tokens** are committed to the repository
- [ ] `.gitignore` correctly excludes `target/`, `*.class`, driver binaries, IDE config files, and generated reports
- [ ] No large binary files (screenshots, test data dumps) are tracked in Git unless intentional
- [ ] Commit messages are meaningful and follow a consistent convention (e.g., Conventional Commits)

---

## Review Sign-off

| Reviewer | Date | Status |
|----------|------|--------|
| | | ⬜ Approved / ⬜ Changes Requested |

> **Legend:**
> - ✅ Pass — Meets the standard
> - ❌ Fail — Needs correction
> - ⚠️ Warning — Minor issue or suggestion
> - N/A — Not applicable to this script
