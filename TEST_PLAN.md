# Manual Test Plan: Authentication, Todo & Regression Scope

## 1. Scope & Objective

- Mục tiêu kiểm thử: Xác thực các tính năng chính và kiểm tra hồi quy (regression) các bug đã được sửa.
- Phạm vi kiểm tra: Authentication, Todo CRUD, Authorization, JWT, Caching và Frontend state management.

## 2. Test Environment & Prerequisites

- Base URL Backend: `http://localhost:8000`
- Base URL Frontend: `http://localhost:3000`
- Database: PostgreSQL
- Cache: Redis
- Browser: Chromium
- Pre-seeded Test Accounts:
  - Account 1 (User A): `user_a@test.com` / `Password@123`
  - Account 2 (User B): `user_b@test.com` / `Password@123`

## 3. Test Cases Matrix

| TC ID | Module / Feature       | Test Scenario                           | Preconditions                               | Test Steps                                                               | Expected Result                                              | Priority / Severity | Status (Pass/Fail) |
| ----- | ---------------------- | --------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- | ------------------ |
| TC-01 | Authentication         | Login thành công với password đúng      | User đã đăng ký                             | 1. Nhập đúng email/password<br>2. Bấm Login                              | Trả về access token và chuyển hướng đến Todo page            | High / Blocker      | Pass               |
| TC-02 | Authentication         | Login thất bại với password sai         | User đã đăng ký                             | 1. Nhập email đúng, password sai<br>2. Bấm Login                         | Login bị từ chối và hiển thị authentication error            | Medium / Security   | Pass               |
| TC-03 | Authorization          | User A không thể đọc Todo của User B    | User A & B đã login, User B sở hữu Todo     | 1. User B tạo Todo X<br>2. User A gọi `GET /todos/X`                     | Trả về `404 Not Found`, User A không thể đọc Todo của User B | High / Critical     | Pass               |
| TC-04 | Authorization          | User A không thể update Todo của User B | User A & B đã login, User B sở hữu Todo     | 1. User B tạo Todo X<br>2. User A gọi `PUT /todos/X`                     | Request bị từ chối, Todo của User B không bị thay đổi        | High / Critical     | Pass               |
| TC-05 | Authorization          | User A không thể delete Todo của User B | User A & B đã login, User B sở hữu Todo     | 1. User B tạo Todo X<br>2. User A gọi `DELETE /todos/X`                  | Request bị từ chối, Todo của User B vẫn tồn tại              | High / Critical     | Pass               |
| TC-06 | JWT / Authentication   | Expired JWT bị reject                   | Có thể tạo JWT với expiration trong quá khứ | 1. Tạo expired JWT<br>2. Gửi request bằng token                          | Expired JWT bị reject và không được authenticate             | High / Critical     | Pass               |
| TC-07 | Todo Logic             | Toggle `completed` từ `true` về `false` | Todo đang `completed = true`                | 1. Bỏ chọn checkbox<br>2. Refresh page                                   | Todo vẫn có `completed = false` sau khi refresh              | Medium / Major      | Pass               |
| TC-08 | Todo Logic             | Update title không làm mất description  | Todo có title và description                | 1. Tạo Todo có title + description<br>2. Chỉ update title<br>3. GET Todo | Title được update, description vẫn giữ nguyên                | Medium / Major      | Pass               |
| TC-09 | Cache                  | Todo list cache được scope theo User    | User A & B đều có Todo                      | 1. User A gọi `GET /todos`<br>2. User B gọi `GET /todos`                 | User B chỉ nhận Todo của User B                              | High / Critical     | Pass               |
| TC-10 | Cache                  | Create Todo invalidate cache            | Todo list đã được cache                     | 1. Gọi `GET /todos`<br>2. Create Todo mới<br>3. Gọi `GET /todos` lại     | Todo mới xuất hiện, không trả stale cache                    | Medium / Major      | Pass               |
| TC-11 | Cache                  | Update Todo invalidate cache            | Todo list đã được cache                     | 1. Gọi `GET /todos`<br>2. Update Todo<br>3. Gọi `GET /todos` lại         | Dữ liệu mới được trả về, không trả stale cache               | Medium / Major      | Pass               |
| TC-12 | Cache                  | Delete Todo invalidate cache            | Todo list đã được cache                     | 1. Gọi `GET /todos`<br>2. Delete Todo<br>3. Gọi `GET /todos` lại         | Todo đã delete không còn xuất hiện trong response            | Medium / Major      | Pass               |
| TC-13 | Frontend / React Query | Pagination sử dụng đúng query key       | Frontend đang chạy                          | 1. Mở page 1<br>2. Chuyển sang page khác<br>3. Quay lại page 1           | Đúng Todo list của từng page, không dùng nhầm cache          | Medium / Major      | Pass               |
| TC-14 | Frontend / Logout      | Logout clear React Query cache          | User A đã login và có Todo                  | 1. User A load Todo list<br>2. Logout<br>3. User B login                 | User B không nhận cached data của User A                     | High / Major        | Pass               |
| TC-15 | E2E                    | Full User Journey                       | Application đang chạy                       | Register → Login → Create Todo → Toggle → Verify → Logout                | Toàn bộ User Journey hoàn thành thành công                   | High / Major        | Pass               |
| TC-16 | E2E / Authorization    | Cross-User Data Isolation               | Application đang chạy                       | 1. User A tạo private Todo<br>2. User B login bằng browser context khác  | User B không nhìn thấy Todo của User A                       | High / Critical     | Pass               |

## 4. Defect Tracking & Known Limitations

- Backend automated tests được thực hiện bằng `pytest`.
- E2E tests được thực hiện bằng `Playwright` trên `Chromium`.
- Manual testing phụ thuộc vào Docker environment và local database.
- Một số Frontend scenarios được verify thông qua E2E tests thay vì Frontend unit tests.
- Test Plan tập trung vào Authentication, Authorization, Todo CRUD, JWT, Cache và Data Isolation.
