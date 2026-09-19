# Kế hoạch kiểm thử thủ công: Authentication, Todo & Regression

## 1. Phạm vi và Mục tiêu

- Kiểm tra mục tiêu: Xác thực các tính năng chính và kiểm tra sửa lỗi (hồi quy) các lỗi đã được sửa.
- Phạm vi kiểm tra: Authentication, Todo CRUD, Authorization, Caching.

## 2. Môi trường thử nghiệm và các điều kiện tiên quyết

- URL cơ sở phía máy chủ: `http://localhost:8000`
- URL cơ bản của giao diện người dùng: `http://localhost:3000`
- Tài khoản thử nghiệm được thiết lập sẵn:
  - Tài khoản 1 (Người dùng A): `user_a@test.com` / `Password@123`
  - Tài khoản 2 (Người dùng B): `user_b@test.com` / `Password@123`

## 3. Ma trận các trường hợp kiểm thử

| Mã TC | Mô-đun / Tính năng | Kịch bản kiểm thử                                      | Điều kiện tiên quyết                         | Các bước kiểm tra                                                                   | Kết quả dự kiến                                             | Mức độ ưu tiên / Mức độ nghiêm trọng | Trạng thái (Đạt/Không đạt) |
| ----- | ------------------ | ------------------------------------------------------ | -------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------ | -------------------------- |
| TC-01 | Xác thực           | Đăng nhập thành công với mật khẩu đúng                 | Người dùng đã đăng ký                        | 1. Nhập đúng email/password<br>2. Bấm Đăng nhập                                     | Đăng nhập thành công và chuyển đến trang Todo               | Cao / Chặn                           | Đạt                        |
| TC-02 | Xác thực           | Đăng nhập thất bại với mật khẩu sai                    | Người dùng đã đăng ký                        | 1. Nhập email đúng, password sai<br>2. Bấm Đăng nhập                                | Đăng nhập bị từ chối và hiển thị lỗi xác thực               | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-03 | Bảo mật Todo       | Người dùng A không thể đọc Todo của người dùng B       | Người dùng A & B đã đăng nhập, B sở hữu Todo | 1. B tạo Todo X<br>2. A gọi GET `/todos/X`                                          | A không thể đọc Todo X, API trả về 404                      | Cao / Nghiêm trọng                   | Đạt                        |
| TC-04 | Bảo mật Todo       | Người dùng A không thể cập nhật Todo của người dùng B  | Người dùng A & B đã đăng nhập, B sở hữu Todo | 1. B tạo Todo X<br>2. A gọi PUT `/todos/X`                                          | Todo của B không bị thay đổi                                | Cao / Nghiêm trọng                   | Đạt                        |
| TC-05 | Bảo mật Todo       | Người dùng A không thể xóa Todo của người dùng B       | Người dùng A & B đã đăng nhập, B sở hữu Todo | 1. B tạo Todo X<br>2. A gọi DELETE `/todos/X`                                       | Todo của B vẫn tồn tại                                      | Cao / Nghiêm trọng                   | Đạt                        |
| TC-06 | Logic Todo         | Đổi trạng thái Todo từ hoàn thành sang chưa hoàn thành | Todo đang ở trạng thái hoàn thành            | 1. Bỏ chọn checkbox<br>2. Refresh trang                                             | Todo vẫn ở trạng thái chưa hoàn thành (`completed = false`) | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-07 | Logic Todo         | Cập nhật title không làm mất description               | Todo có title và description                 | 1. Tạo Todo có title + description<br>2. Chỉ cập nhật title<br>3. Kiểm tra lại Todo | Title được cập nhật, description vẫn giữ nguyên             | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-08 | Cache              | Cache Todo được phân tách theo người dùng              | Người dùng A & B đều có Todo                 | 1. A gọi GET `/todos`<br>2. B gọi GET `/todos`                                      | B chỉ nhận Todo của B, không nhận dữ liệu của A             | Cao / Nghiêm trọng                   | Đạt                        |
| TC-09 | Cache              | Tạo Todo làm mất cache cũ                              | Danh sách Todo đã được cache                 | 1. Gọi GET `/todos`<br>2. Tạo Todo mới<br>3. Gọi GET `/todos` lại                   | Todo mới xuất hiện, không trả dữ liệu cache cũ              | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-10 | Cache              | Cập nhật Todo làm mất cache cũ                         | Danh sách Todo đã được cache                 | 1. Gọi GET `/todos`<br>2. Cập nhật Todo<br>3. Gọi GET `/todos` lại                  | Dữ liệu Todo mới được trả về                                | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-11 | Cache              | Xóa Todo làm mất cache cũ                              | Danh sách Todo đã được cache                 | 1. Gọi GET `/todos`<br>2. Xóa Todo<br>3. Gọi GET `/todos` lại                       | Todo đã xóa không còn xuất hiện                             | Trung bình / Nghiêm trọng            | Đạt                        |
| TC-12 | Frontend           | Đăng xuất xóa dữ liệu cache của người dùng trước       | User A đã đăng nhập và có Todo               | 1. User A đăng xuất<br>2. User B đăng nhập trên cùng trình duyệt                    | User B không nhìn thấy dữ liệu cache của User A             | Cao / Nghiêm trọng                   | Đạt                        |
| TC-13 | E2E                | Luồng người dùng hoàn chỉnh                            | Ứng dụng đang chạy                           | Register → Create Todo → Toggle → Verify → Logout                                   | Toàn bộ luồng thực hiện thành công                          | Cao / Nghiêm trọng                   | Đạt                        |
| TC-14 | E2E                | Phân tách dữ liệu giữa hai người dùng                  | Ứng dụng đang chạy                           | 1. A tạo Todo riêng tư<br>2. B đăng nhập bằng session khác                          | B không nhìn thấy Todo của A                                | Cao / Nghiêm trọng                   | Đạt                        |

## 4. Theo dõi và những hạn chế đã biết

- Các test tự động backend được thực hiện bằng `pytest`.
- Các test E2E được thực hiện bằng Playwright trên Chromium.
- Kiểm thử thủ công phụ thuộc vào môi trường Docker local.
- Một số trường hợp frontend được kiểm tra thông qua E2E thay vì frontend unit test.
- Chưa bao phủ toàn bộ các trường hợp biên của ứng dụng.
