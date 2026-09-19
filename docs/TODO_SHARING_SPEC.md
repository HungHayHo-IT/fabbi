# Technical Specification: Todo Sharing

## 1. Overview & Objective

- **Feature Summary**: Cho phép User chia sẻ Todo list cho User khác với một trong hai permission: `viewer` hoặc `editor`. Owner có thể revoke access bất kỳ lúc nào.
- **Problem Statement**: Hiện tại mỗi Todo chỉ thuộc về một User, chưa hỗ trợ collaboration. Feature này cho phép nhiều User cùng truy cập một Todo list theo permission được cấp.
- **Target Audience / Roles**:
  - **Owner**: Người sở hữu Todo list, có toàn quyền quản lý Todo và sharing.
  - **Editor**: Được xem, tạo và cập nhật Todo.
  - **Viewer**: Chỉ được xem Todo.

## 2. User Stories & Acceptance Criteria

### User Story 1: Share Todo List

- **As a** Owner
- **I want to** share Todo list của mình cho một User khác
- **So that** User đó có thể truy cập Todo list theo permission được cấp.
- **Acceptance Criteria**:
  - [ ] Owner có thể share Todo list cho một registered User bằng email.
  - [ ] Permission chỉ được là `viewer` hoặc `editor`.
  - [ ] Owner không thể share Todo list cho chính mình.
  - [ ] Không cho phép tạo duplicate active share.

### User Story 2: Access Shared Todo List

- **As a** Viewer / Editor
- **I want to** truy cập Todo list đã được share cho tôi
- **So that** tôi có thể xem hoặc cộng tác theo đúng permission.
- **Acceptance Criteria**:
  - [ ] Viewer có thể đọc Todo list và Todo details.
  - [ ] Viewer không thể create, update hoặc delete Todo.
  - [ ] Editor có thể create và update Todo.
  - [ ] Editor không thể quản lý sharing permission.

### User Story 3: Revoke Access

- **As a** Owner
- **I want to** revoke quyền truy cập của một User
- **So that** User đó mất quyền truy cập Todo list của tôi ngay lập tức.
- **Acceptance Criteria**:
  - [ ] Owner có thể revoke một active share.
  - [ ] User bị revoke không thể tiếp tục đọc Todo list.
  - [ ] User bị revoke không thể create hoặc update Todo.
  - [ ] Related cache phải được invalidate ngay sau khi revoke.

## 3. Scope

- **In-Scope**:
  - Share Todo list với permission `viewer` / `editor`.
  - Xem shared Todo list.
  - Editor có thể create/update Todo.
  - Owner có thể update permission và revoke access.
  - Authorization cho shared Todo.
  - Chặn duplicate share và self-sharing.
  - Cache invalidation khi permission thay đổi.

- **Out-of-Scope**:
  - Public sharing link.
  - Anonymous / Guest users.
  - Email invitation system.
  - Permission expiration.
  - Real-time collaboration.
  - Share từng Todo item riêng lẻ.

## 4. Database Design

- **New Tables / Altered Tables**: Tạo bảng `todo_shares`.

| Cột | Kiểu dữ liệu | Ghi chú |
|-----|--------------|---------|
| `id` | UUID | Primary Key |
| `owner_id` | UUID | Foreign Key → `users.id` |
| `shared_with_id` | UUID | Foreign Key → `users.id` |
| `permission` | VARCHAR | Chỉ nhận `viewer` hoặc `editor` |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

- **Constraints & Indexes**:
  - Unique constraint trên `(owner_id, shared_with_id)` để ngăn duplicate share.
  - Check constraint: `permission IN ('viewer', 'editor')`.
  - Check constraint: không cho phép `owner_id = shared_with_id`.
  - Các Foreign Key dùng `ON DELETE CASCADE`.
  - Index trên `owner_id` và `shared_with_id` để tối ưu lookup permission.

## 5. API Contracts & Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/todos/shares` | Share Todo list | Yes |
| GET | `/api/v1/todos/shares` | Liệt kê các share (do Owner tạo) | Yes |
| GET | `/api/v1/todos/shared-with-me` | Liệt kê các Todo list được share cho mình | Yes |
| PUT | `/api/v1/todos/shares/{share_id}` | Update permission | Yes |
| DELETE | `/api/v1/todos/shares/{share_id}` | Revoke access | Yes |

- **Request Body & Validation Schema**: Pydantic / JSON format.
- **Responses & Error Codes**: `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`.

## 6. Business Logic & Security Considerations

- **Authorization & Permission Matrix**:

| Action | Owner | Editor | Viewer |
|--------|:-----:|:------:|:------:|
| Read Todo | Yes | Yes | Yes |
| Create Todo | Yes | Yes | No |
| Update Todo | Yes | Yes | No |
| Delete Todo | Yes | No | No |
| Share Todo list | Yes | No | No |
| Update permission | Yes | No | No |
| Revoke access | Yes | No | No |

  - Editor / Viewer không thể share tiếp cho người khác (chỉ Owner được share).

- **Edge Cases & Race Conditions**:

| Tình huống | Cách xử lý |
|------------|------------|
| Duplicate invite | Trả về `409 Conflict` |
| Self-sharing | Trả về `400 Bad Request` |
| Concurrent permission update | Verify permission bên trong transaction |
| Revoke trong lúc Editor đang gửi request | Reject nếu permission không còn hợp lệ |
| JWT hợp lệ | Không đồng nghĩa với có sharing permission hợp lệ, luôn check lại permission |

## 7. Caching & Invalidation Strategy

- **Cache Key**:
  - Todo list của chính User: `todos:list:{user_id}:{page}:{size}`
  - Shared Todo list: `todos:shared:{owner_id}:{user_id}:{page}:{size}`

- **Cache Invalidation** xảy ra khi:
  - Owner create/update/delete Todo.
  - Permission được create/update.
  - Permission bị revoke.
  - Editor create/update Todo.
  - Revoke phải invalidate shared cache **ngay lập tức**.
