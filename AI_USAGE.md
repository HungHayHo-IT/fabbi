# Công bố việc sử dụng AI (AI Usage Disclosure)

## AI Assistant đã sử dụng

ChatGPT được sử dụng như một AI assistant hỗ trợ coding và review trong suốt quá trình làm bài assessment này.

## Cách sử dụng AI

AI được dùng để:

- Review codebase hiện có và xác định các vấn đề security tiềm ẩn.
- Giải thích các hướng implementation và trade-offs.
- Đề xuất test case cho authorization, JWT expiration, cache isolation, partial update và các luồng E2E của user.
- Hỗ trợ xây dựng cấu trúc Playwright E2E test.
- Review các cải tiến cho Docker Compose như healthcheck và điều kiện phụ thuộc giữa các service (service dependency conditions).
- Review Technical Specification của tính năng Todo Sharing.
- Hỗ trợ các lệnh Git và troubleshooting các vấn đề trong quá trình phát triển.

## Trách nhiệm của cá nhân

Toàn bộ các thay đổi do AI đề xuất đều được candidate tự review và áp dụng thủ công.

Candidate chịu trách nhiệm về:

- Hiểu rõ implementation hiện có.
- Đưa ra các quyết định implementation cuối cùng.
- Chỉnh sửa source code.
- Chạy và xác nhận các test.
- Xem xét kết quả test và debug các lỗi.
- Review lịch sử Git và pull request cuối cùng.

Các gợi ý do AI tạo ra không được chấp nhận một cách mù quáng, mà được kiểm chứng dựa trên codebase thực tế và hành vi runtime của dự án.

## Nhật ký Prompt / Hội thoại

Sự hỗ trợ của AI được thực hiện thông qua các cuộc hội thoại với ChatGPT trong quá trình làm bài.

Lịch sử hội thoại liên quan có thể được cung cấp cho reviewer khi có yêu cầu.

## Cấu hình AI

- Assistant: ChatGPT
- Mục đích sử dụng: Hỗ trợ coding tương tác, debugging, code review, lên kế hoạch test và giải thích kỹ thuật.
