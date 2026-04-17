# Thiết kế Schema - Module Quản lý Hàng hóa (dtp_goods_management)

Module này (`dtp_goods_management`) nhằm mục đích theo dõi toàn bộ quá trình cấp phát, thu hồi, và luân chuyển hàng hóa/dụng cụ học tập đến các trường học, thuộc hệ sinh thái `dtp_school_inventory`.

## Mô hình chính (Main Model)

### Model: `dtp.goods.transaction`
Mô hình này đóng vai trò như một sổ nhật ký (log) ghi nhận từng giao dịch đối với các sản phẩm/dụng cụ học tập.

| Tên trường (Field Name) | Kiểu dữ liệu (Type) | Mô tả (Description) | Ràng buộc / Quan hệ (Constraints/Relations) |
| --- | --- | --- | --- |
| `name` | Char | Mã nghiệp vụ/Số tham chiếu | Required, Readonly, Default='New' |
| `operation_type` | Selection | Loại nghiệp vụ | `issue` (Cấp phát), `recover` (Thu hồi), `transfer` (Luân chuyển) |
| `date` | Datetime | Ngày thực hiện | Default: current time |
| `school_id` | Many2one | Trường học đích | `dtp.school` |
| `class_id` | Many2one | Lớp học đích | `dtp.school.class` |
| `subject_id` | Many2one | Môn học đích | `dtp.school.subject` |
| `from_school_id` | Many2one | Từ trường học | `dtp.school` (Luân chuyển) |
| `from_class_id` | Many2one | Từ lớp học | `dtp.school.class` (Luân chuyển) |
| `from_subject_id` | Many2one | Từ môn học | `dtp.school.subject` (Luân chuyển) |
| `product_id` | Many2one | Sản phẩm / Dụng cụ học tập | `product.product`, Required |
| `product_qty` | Float | Số lượng | Required, Default=1.0 |
| `notes` | Text | Ghi chú thêm | |

## Nghiệp vụ cơ bản (Cách lưu dữ liệu)

1. **Cấp phát (Issue)**:
   - `operation_type`: `issue`
   - Nơi nhận: Điền vào `school_id`, `class_id`, `subject_id`
   - Bỏ trống các trường `from_*`

2. **Thu hồi (Recover)**:
   - `operation_type`: `recover`
   - Nơi bị thu hồi: Điền vào `school_id`, `class_id`, `subject_id`
   - Bỏ trống các trường `from_*`

3. **Luân chuyển (Transfer)**:
   - `operation_type`: `transfer`
   - Nơi nhận: Điền vào `school_id`, `class_id`, `subject_id`
   - Nơi xuất: Điền vào `from_school_id`, `from_class_id`, `from_subject_id`

## Tính mở rộng trong tương lai
Hiện tại module chỉ thiết kế schema cơ bản. Khi đưa vào logic nghiệp vụ có thể:
1. Thêm trạng thái (Draft, Done, Cancelled).
2. Viết các hàm (methods) để override nút Confirm, từ đó tự động trừ/cộng số lượng trong kho của trường (nếu có quản lý kho theo trường học thông qua tính năng location của Inventory).
3. Sequence tự động nhảy số theo loại nghiệp vụ, vd: ISS/2026/001, REC/2026/001.

_Tài liệu được tạo theo yêu cầu Task_5._
