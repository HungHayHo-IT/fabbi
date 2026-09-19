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