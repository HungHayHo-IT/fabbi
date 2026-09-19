import { test, expect } from "@playwright/test";

test("full user journey: register, create, toggle and logout", async ({
  page,
}) => {
  const email = `e2e-${Date.now()}@example.com`;
  const password = "E2eTest@123";

  // Register
  await page.goto("/register");

  await page.getByLabel("Email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByLabel("Confirm Password").fill(password);

  await page.getByRole("button", { name: "Create Account" }).click();

  // Registration should navigate to dashboard
  await expect(page).toHaveURL("/");

  // Create todo
  await page.getByRole("button", { name: "Add Todo" }).click();

  const todoTitle = `E2E Todo ${Date.now()}`;

  await page.getByLabel("Title").fill(todoTitle);

  await page
    .getByLabel("Description (optional)")
    .fill("Created by Playwright");

  await page.getByRole("button", { name: "Create" }).click();

  // Verify todo appears
  await expect(page.getByText(todoTitle, { exact: true })).toBeVisible();

  // Toggle completed
  const todoTitleElement = page.getByText(todoTitle, {
    exact: true,
  });

  const todoContainer = todoTitleElement
    .locator("..")
    .locator("..");

  await todoContainer.getByRole("checkbox").click();

  // Verify completed state
  await expect(todoTitleElement).toHaveClass(/line-through/);

  // Logout
  await page.getByRole("button", { name: "Logout" }).click();

  await expect(page).toHaveURL("/login");
});


test("cross-user data isolation: user B cannot see user A's todo", async ({
    browser,
  }) => {
    const userA = {
      email: `user-a-${Date.now()}@example.com`,
      password: "E2eTest@123",
    };
  
    const userB = {
      email: `user-b-${Date.now()}@example.com`,
      password: "E2eTest@123",
    };
  
    const todoTitle = `Private Todo ${Date.now()}`;
  
    // User A - separate browser session
    const contextA = await browser.newContext();
    const pageA = await contextA.newPage();
  
    await pageA.goto("/register");
  
    await pageA.getByLabel("Email").fill(userA.email);
    await pageA.locator("#password").fill(userA.password);
    await pageA.getByLabel("Confirm Password").fill(userA.password);
  
    await pageA.getByRole("button", { name: "Create Account" }).click();
  
    await expect(pageA).toHaveURL("/");
  
    // User A creates a private todo
    await pageA.getByRole("button", { name: "Add Todo" }).click();
  
    await pageA.getByLabel("Title").fill(todoTitle);
  
    await pageA
      .getByLabel("Description (optional)")
      .fill("Private todo owned by User A");
  
    await pageA.getByRole("button", { name: "Create" }).click();
  
    // User A can see the todo
    await expect(
      pageA.getByText(todoTitle, { exact: true })
    ).toBeVisible();
  
    // User B - completely separate browser session
    const contextB = await browser.newContext();
    const pageB = await contextB.newPage();
  
    await pageB.goto("/register");
  
    await pageB.getByLabel("Email").fill(userB.email);
    await pageB.locator("#password").fill(userB.password);
    await pageB.getByLabel("Confirm Password").fill(userB.password);
  
    await pageB.getByRole("button", { name: "Create Account" }).click();
  
    await expect(pageB).toHaveURL("/");
  
    // User B must NOT see User A's private todo
    await expect(
      pageB.getByText(todoTitle, { exact: true })
    ).not.toBeVisible();
  
    await contextA.close();
    await contextB.close();
  });