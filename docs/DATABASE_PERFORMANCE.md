# Database Performance & Indexing Strategy

## 1. Mục tiêu

Tài liệu này trình bày quá trình phân tích và tối ưu hiệu năng cơ sở dữ liệu cho Task 3C.

Mục tiêu:

- Phân tích hiệu năng các truy vấn Todo chính.
- Sử dụng `EXPLAIN (ANALYZE, BUFFERS)` để xác định nguyên nhân gây chậm.
- Kiểm tra hiệu năng trên dataset lớn.
- Thiết kế các composite index phù hợp với các truy vấn thực tế.
- Tạo index thông qua Alembic migration.
- So sánh thời gian thực thi trước và sau khi tối ưu.
- Phân tích các trade-off khi sử dụng index trong production.

---

## 2. Dataset Benchmark

Benchmark được thực hiện trên PostgreSQL với dataset lớn được tạo bằng seed script có sẵn trong project.

| Thành phần | Giá trị |
|---|---:|
| Users | 10,000 |
| Todos | 1,000,000 |
| User benchmark | `338770e3-0705-4089-a5cf-e3bffc97fcd5` |
| Todos của user benchmark | 141 |

Dataset được tạo bằng:

```bash
docker compose exec -e SEED_USERS=10000 -e SEED_TODOS=1000000 backend python -m app.db.seed
```

Cùng một dataset và cùng một user được sử dụng cho benchmark Before và After.

---

## 3. Queries Analyzed

Các truy vấn được phân tích bằng:

```sql
EXPLAIN (ANALYZE, BUFFERS)
```

### Query 1 - Filter todos by user

```sql
SELECT id, title, description, completed, user_id, created_at, updated_at
FROM todos
WHERE user_id = '338770e3-0705-4089-a5cf-e3bffc97fcd5'
LIMIT 20;
```

### Query 2 - Filter by user and order by creation time

```sql
SELECT id, title, description, completed, user_id, created_at, updated_at
FROM todos
WHERE user_id = '338770e3-0705-4089-a5cf-e3bffc97fcd5'
ORDER BY created_at DESC
LIMIT 20;
```

### Query 3 - Filter by user and completion status

```sql
SELECT id, title, description, completed, user_id, created_at, updated_at
FROM todos
WHERE user_id = '338770e3-0705-4089-a5cf-e3bffc97fcd5'
  AND completed = false
ORDER BY created_at DESC
LIMIT 20;
```

### Query 4 - Count todos by user

```sql
SELECT COUNT(*)
FROM todos
WHERE user_id = '338770e3-0705-4089-a5cf-e3bffc97fcd5';
```

---

## 4. Before Optimization

Trước khi thêm index, các truy vấn chính sử dụng:

```text
Parallel Seq Scan
```

PostgreSQL phải quét một phần lớn bảng `todos` để tìm các record phù hợp với điều kiện `user_id`.

Dataset có tổng cộng 1,000,000 Todo, trong khi user benchmark chỉ có 141 Todo.

### Benchmark Before

| Query | Execution Time |
|---|---:|
| User-filtered todo list | 22.103 ms |
| User + ORDER BY created_at | 47.772 ms |
| User + completed + ORDER BY | 69.356 ms |
| COUNT todos by user | 52.053 ms |

Đối với các truy vấn có `ORDER BY`, PostgreSQL còn phải thực hiện bước sort sau khi scan và filter dữ liệu.

Kết quả cho thấy index primary key trên `id` không đủ để tối ưu các query chính của Todo API vì các query thường xuyên sử dụng `user_id`, `completed` và `created_at`.

---

## 5. Indexing Strategy

Dựa trên các query thực tế, hai composite B-tree index được thêm vào bảng `todos`.

### 5.1. Index cho user và created_at

```text
(user_id, created_at, id)
```

Tên index:

```text
ix_todos_user_created_at
```

Index này phục vụ query:

```sql
WHERE user_id = ?
ORDER BY created_at DESC, id DESC
LIMIT 20
```

`user_id` được đặt đầu tiên vì đây là điều kiện filter chính.

`created_at` hỗ trợ việc truy vấn Todo theo thứ tự thời gian tạo.

`id` được thêm vào làm tie-breaker để đảm bảo thứ tự ổn định khi nhiều Todo có cùng giá trị `created_at`.

### 5.2. Index cho user, completed và created_at

```text
(user_id, completed, created_at, id)
```

Tên index:

```text
ix_todos_user_completed_created_at
```

Index này phục vụ query:

```sql
WHERE user_id = ?
  AND completed = ?
ORDER BY created_at DESC, id DESC
LIMIT 20
```

Index được thiết kế dựa trên thứ tự filter và ordering của query.

---

## 6. Alembic Migration

Các index được tạo thông qua Alembic migration thay vì tạo thủ công trực tiếp trong PostgreSQL.

Migration:

```text
backend/alembic/versions/4d509292fb69_add_todo_performance_indexes.py
```

Revision:

```text
4d509292fb69
```

Parent revision:

```text
a0790c76a129
```

Migration tạo hai index:

```python
op.create_index(
    "ix_todos_user_created_at",
    "todos",
    ["user_id", "created_at", "id"],
)

op.create_index(
    "ix_todos_user_completed_created_at",
    "todos",
    ["user_id", "completed", "created_at", "id"],
)
```

Migration được áp dụng bằng:

```bash
cd backend
alembic upgrade head
```

Sau khi migration hoàn thành, các index được kiểm tra bằng:

```sql
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'todos';
```

Kết quả:

```text
todos_pkey
ix_todos_user_created_at
ix_todos_user_completed_created_at
```

---

## 7. After Optimization

Sau khi tạo index, statistics của bảng được cập nhật bằng:

```sql
ANALYZE todos;
```

Sau đó chạy lại cùng bốn query với:

```sql
EXPLAIN (ANALYZE, BUFFERS)
```

### Benchmark Before vs After

| Query | Before | After | Improvement |
|---|---:|---:|---:|
| User-filtered todo list | 22.103 ms | 0.235 ms | 98.94% |
| User + ORDER BY created_at | 47.772 ms | 0.116 ms | 99.76% |
| User + completed + ORDER BY | 69.356 ms | 0.068 ms | 99.90% |
| COUNT todos by user | 52.053 ms | 0.078 ms | 99.85% |

Công thức tính mức cải thiện:

```text
(Before - After) / Before × 100
```

Kết quả cho thấy thời gian thực thi của cả bốn query đều giảm xuống mức sub-millisecond trong dataset benchmark.

---

## 8. Query Plan Changes

### Query 1 - Filter todos by user

**Before:**

```text
Parallel Seq Scan
```

**After:**

```text
Index Scan
using ix_todos_user_completed_created_at
```

Execution Time:

```text
22.103 ms → 0.235 ms
```

PostgreSQL chuyển từ việc quét tuần tự bảng sang sử dụng index để tìm các Todo thuộc user được yêu cầu.

### Query 2 - User + ORDER BY created_at

**Before:**

```text
Parallel Seq Scan
Sort
```

**After:**

```text
Index Scan Backward
using ix_todos_user_created_at
```

Execution Time:

```text
47.772 ms → 0.116 ms
```

Index cho phép PostgreSQL tìm các Todo của user và đọc dữ liệu theo thứ tự `created_at` phù hợp với query.

### Query 3 - User + completed + ORDER BY

**Before:**

```text
Parallel Seq Scan
Sort
```

**After:**

```text
Index Scan Backward
using ix_todos_user_completed_created_at
```

Execution Time:

```text
69.356 ms → 0.068 ms
```

Composite index hỗ trợ đồng thời điều kiện `user_id`, `completed` và thứ tự `created_at`.

### Query 4 - COUNT todos by user

**Before:**

```text
Parallel Seq Scan
```

**After:**

```text
Index Only Scan
using ix_todos_user_completed_created_at
```

Execution Time:

```text
52.053 ms → 0.078 ms
```

Kết quả benchmark cho thấy:

```text
Heap Fetches: 0
```

Trong lần thực thi này, PostgreSQL có thể lấy thông tin cần thiết trực tiếp từ index mà không cần fetch các row tương ứng từ heap.

---

## 9. Application Query Optimization

Query lấy danh sách Todo trong application được cập nhật để sử dụng thứ tự ổn định:

```python
query = (
    select(Todo)
    .where(Todo.user_id == user_id)
    .order_by(Todo.created_at.desc(), Todo.id.desc())
    .offset(skip)
    .limit(limit)
)
```

Thứ tự này phù hợp với index:

```text
(user_id, created_at, id)
```

Việc thêm `id` vào `ORDER BY` giúp đảm bảo thứ tự kết quả ổn định khi nhiều Todo có cùng giá trị `created_at`.

Điều này cũng phù hợp với pagination hiện tại của Todo API.

---

## 10. Index Trade-offs

### 10.1. Write Latency

Index giúp cải thiện hiệu năng đọc nhưng làm tăng chi phí ghi.

Khi thực hiện:

- `INSERT`
- `UPDATE`
- `DELETE`

PostgreSQL phải duy trì thêm các index tương ứng.

Do đó, không nên tạo index một cách tùy tiện. Index nên được thiết kế dựa trên các query thực tế và được sử dụng thường xuyên.

### 10.2. Storage Overhead

Mỗi index chiếm thêm dung lượng lưu trữ trên disk.

Ngoài ra, index cũng sử dụng memory/cache khi PostgreSQL truy cập dữ liệu.

Vì vậy, việc tạo quá nhiều index có thể làm tăng:

- Disk usage
- Memory usage
- Chi phí bảo trì index
- Chi phí ghi dữ liệu

### 10.3. Composite Index Column Order

Thứ tự column trong composite index rất quan trọng.

Ví dụ:

```text
(user_id, completed, created_at, id)
```

phù hợp với query:

```sql
WHERE user_id = ?
  AND completed = ?
ORDER BY created_at DESC, id DESC
```

`user_id` được đặt đầu tiên vì đây là điều kiện filter phổ biến trong Todo API.

`completed` tiếp theo hỗ trợ điều kiện filter trạng thái.

`created_at` hỗ trợ thứ tự dữ liệu.

`id` được sử dụng làm tie-breaker để đảm bảo ordering ổn định.

### 10.4. Migration Safety

Việc tạo index trên bảng lớn trong production cần được thực hiện cẩn thận.

Đối với PostgreSQL có traffic cao, có thể cân nhắc:

```sql
CREATE INDEX CONCURRENTLY
```

để giảm blocking đối với các thao tác ghi đồng thời.

Tuy nhiên, `CREATE INDEX CONCURRENTLY` có các yêu cầu và giới hạn vận hành riêng, vì vậy cần được xem xét trong deployment strategy.

Trong project này, index được quản lý thông qua Alembic migration để database schema có thể được version-control và triển khai nhất quán giữa các environment.

---

## 11. Test Validation

Sau khi hoàn thành thay đổi, toàn bộ backend test suite đã được chạy lại thành công.

Các test liên quan đến Todo và Redis dependency đều pass.

Redis dependency trong test cũng được isolate giữa các test để tránh việc một test thay đổi dependency override và ảnh hưởng đến các test chạy sau.

Việc chạy toàn bộ test suite giúp xác nhận rằng thay đổi query và database index không làm phá vỡ các chức năng hiện có của Todo API.

---

## 12. Summary

Trước khi tối ưu, các query chính trên bảng `todos` sử dụng `Parallel Seq Scan`, dẫn đến việc phải quét một lượng lớn dữ liệu trong bảng 1,000,000 record.

Hai composite index được thêm vào:

```text
(user_id, created_at, id)

(user_id, completed, created_at, id)
```

Các index này được triển khai thông qua Alembic migration và được thiết kế dựa trên các query pattern thực tế của Todo API.

Sau khi tối ưu, PostgreSQL sử dụng:

```text
Index Scan
Index Scan Backward
Index Only Scan
```

thay cho các sequential scan trong các query benchmark.

### Kết quả benchmark

| Query | Before | After | Improvement |
|---|---:|---:|---:|
| User-filtered todo list | 22.103 ms | 0.235 ms | 98.94% |
| User + ORDER BY created_at | 47.772 ms | 0.116 ms | 99.76% |
| User + completed + ORDER BY | 69.356 ms | 0.068 ms | 99.90% |
| COUNT todos by user | 52.053 ms | 0.078 ms | 99.85% |

Kết quả benchmark cho thấy các query được phân tích giảm đáng kể thời gian thực thi trên dataset 1,000,000 Todo.

Việc tối ưu được thực hiện thông qua migration nên các thay đổi database có thể được version-control và tái triển khai nhất quán giữa các environment.

Tuy nhiên, các index bổ sung cũng tạo ra trade-off về write latency và storage overhead, do đó cần cân nhắc workload thực tế trước khi áp dụng chiến lược index tương tự trên production.
