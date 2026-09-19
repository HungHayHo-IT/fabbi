# Technical Specification: Todo Sharing

## 1. Overview & Objective

- **Feature Summary**: Cho phép User chia sẻ Todo list với User khác bằng hai permission: `viewer` hoặc `editor`. Owner có thể revoke access bất kỳ lúc nào.
- **Problem Statement**: Hiện tại Todo chỉ thuộc về một User và chưa hỗ trợ collaboration. Feature này cho phép nhiều User cùng truy cập Todo list theo permission được cấp.
- **Target Audience / Roles**:
  - **Owner**: Người sở hữu Todo list, có toàn quyền quản lý Todo và sharing.
  - **Editor**: Có thể xem, tạo và cập nhật Todo.
  - **Viewer**: Chỉ có quyền xem Todo.

## 2. User Stories & Acceptance Criteria

### User Story 1: Share Todo List

- **As a** Owner
- **I want to** share my Todo list with another User
- **So that** the User can access my Todo list with the assigned permission.
- **Acceptance Criteria**:
  - [ ] Owner có thể share Todo list cho một registered User bằng email.
  - [ ] Permission chỉ được phép là `viewer` hoặc `editor`.
  - [ ] Owner không thể share Todo list cho chính mình.
  - [ ] Không cho phép tạo duplicate active share.

### User Story 2: Access Shared Todo List

- **As a** Viewer / Editor
- **I want to** access a Todo list shared with me
- **So that** I can view or collaborate according to my permission.
- **Acceptance Criteria**:
  - [ ] Viewer có thể đọc Todo list và Todo details.
  - [ ] Viewer không thể create, update hoặc delete Todo.
  - [ ] Editor có thể create và update Todo.
  - [ ] Editor không thể quản lý sharing permission.

### User Story 3: Revoke Access

- **As a** Owner
- **I want to** revoke a User's access
- **So that** the User immediately loses access to my Todo list.
- **Acceptance Criteria**:
  - [ ] Owner có thể revoke một active share.
  - [ ] User bị revoke không thể tiếp tục đọc Todo list.
  - [ ] User bị revoke không thể create hoặc update Todo.
  - [ ] Related cache phải được invalidated ngay sau khi revoke.

## 3. Scope

- **In-Scope**:

  - Share Todo list bằng `viewer` / `editor` permission.
  - View shared Todo list.
  - Editor có thể create/update Todo.
  - Owner có thể update permission và revoke access.
  - Authorization cho shared Todo.
  - Duplicate share và self-sharing prevention.
  - Cache invalidation khi permission thay đổi.

- **Out-of-Scope**:
  - Public sharing link.
  - Anonymous / Guest users.
  - Email invitation system.
  - Permission expiration.
  - Real-time collaboration.
  - Sharing individual Todo item.

## 4. Database Design

- **New Tables / Altered Tables**:

  - Tạo bảng `todo_shares`:
    - `id`: UUID, Primary Key.
    - `owner_id`: UUID, Foreign Key → `users.id`.
    - `shared_with_id`: UUID, Foreign Key → `users.id`.
    - `permission`: VARCHAR, chỉ nhận `viewer` hoặc `editor`.
    - `created_at`: TIMESTAMP.
    - `updated_at`: TIMESTAMP.

- **Constraints & Indexes**:
  - Unique constraint trên `(owner_id, shared_with_id)` để ngăn duplicate share.
  - Check constraint đảm bảo `permission IN ('viewer', 'editor')`.
  - Không cho phép `owner_id = shared_with_id`.
  - Foreign keys sử dụng `ON DELETE CASCADE`.
  - Index trên `owner_id` và `shared_with_id` để tối ưu lookup sharing permissions.

## 5. API Contracts & Endpoints

| Method | Endpoint                          | Description            | Auth Required |
| ------ | --------------------------------- | ---------------------- | ------------- |
| POST   | `/api/v1/todos/shares`            | Share Todo list        | Yes           |
| GET    | `/api/v1/todos/shares`            | List shares            | Yes           |
| GET    | `/api/v1/todos/shared-with-me`    | List shared Todo lists | Yes           |
| PUT    | `/api/v1/todos/shares/{share_id}` | Update permission      | Yes           |
| DELETE | `/api/v1/todos/shares/{share_id}` | Revoke access          | Yes           |

- **Request Body & Validation Schema**: Pydantic / JSON format.
- **Responses & Error Codes**: `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`.

## 6. Business Logic & Security Considerations

- **Authorization & Permission Matrix**:

| Action            | Owner | Editor | Viewer |
| ----------------- | ----- | ------ | ------ |
| Read Todo         | Yes   | Yes    | Yes    |
| Create Todo       | Yes   | Yes    | No     |
| Update Todo       | Yes   | Yes    | No     |
| Delete Todo       | Yes   | No     | No     |
| Share Todo list   | Yes   | No     | No     |
| Update permission | Yes   | No     | No     |
| Revoke access     | Yes   | No     | No     |

- **Edge Cases & Race Conditions**:
  - Duplicate invite → `409 Conflict`.
  - Self-sharing → `400 Bad Request`.
  - Concurrent permission update → verify permission inside transaction.
  - Revoke while Editor is making a request → reject if permission is no longer valid.
  - Valid JWT does not imply valid sharing permission.

## 7. Caching & Invalidation Strategy

- **Cache Key**:

`todos:list:{user_id}:{page}:{size}`

- Shared Todo cache:

`todos:shared:{owner_id}:{user_id}:{page}:{size}`

- **Cache Invalidation**:
  - Owner create/update/delete Todo.
  - Permission create/update.
  - Permission revoke.
  - Editor create/update Todo.
  - Revoke phải invalidate shared cache ngay lập tức.
