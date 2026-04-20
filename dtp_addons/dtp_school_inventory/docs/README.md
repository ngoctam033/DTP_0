# DTP School Inventory Management

## Mục tiêu
Module mở rộng app Inventory để quản lý trường học, môn học, dụng cụ học tập và cung cấp dashboard tổng quan.

---

## 1. Schema (Models)

### 1.1 res.partner (inherit) — Trường học
File: `models/school_management.py`

| Field | Type | Ghi chú |
|---|---|---|
| is_school | Boolean | Đánh dấu là trường học |
| school_type | Selection | kindergarten / primary / secondary |
| address | Char | Địa chỉ |
| district | Char | Quận/huyện |
| province | Char | Tỉnh/thành |
| region | Selection | hcm / mekong / hue |
| sale_user_ids | Many2many → res.users | Nhân viên kinh doanh phụ trách |
| class_ids | One2many → res.partner.class | Các khối lớp của trường |

### 1.2 res.partner.class — Khối lớp
File: `models/school_management.py`

| Field | Type | Ghi chú |
|---|---|---|
| grade | Selection | A0, A1, A2, 1–9 (rec_name) |
| class_count | Integer | Số lượng lớp trong khối |
| school_id | Many2one → res.partner | Trường sở hữu (cascade) |
| subject_ids | Many2many → res.partner.subject | Môn học áp dụng cho khối (qua bảng res_partner_class_subject_rel) |
| region | Selection (related) | Khu vực, lấy từ school_id.region, store=True |

### 1.3 res.partner.subject — Môn học
File: `models/school_management.py`

| Field | Type | Ghi chú |
|---|---|---|
| name | Char | Tên môn học |
| class_ids | Many2many → res.partner.class | Các khối lớp sử dụng môn này (qua bảng res_partner_class_subject_rel) |
| supply_product_ids | Many2many → product.product | Dụng cụ học tập liên kết |

> Một môn học có thể áp dụng cho nhiều khối lớp ở nhiều trường khác nhau.

### 1.4 stock.picking (inherit) — Phiếu giao hàng
File: `models/stock_picking.py`

| Field | Type | Ghi chú |
|---|---|---|
| partner_id | Many2one → res.partner | Bắt buộc điền (required=True) |
| subject_id | Many2one → res.partner.subject | Môn học đơn giao hàng phục vụ |
| return_deadline_date | Date | Ngày thu hồi (nhập tay) |
| return_days_left | Integer (compute) | Số ngày còn lại đến hạn thu hồi, chỉ tính cho outgoing |

Logic:
- `_onchange_subject_id`: khi chọn môn học, tự động xóa trắng danh sách sản phẩm hiện tại và load danh sách mới từ `supply_product_ids` vào `move_ids` (số lượng mặc định là 1, cho phép user chỉnh tay sau đó).
- `_compute_return_days_left`: tính số ngày còn lại = return_deadline_date - hôm nay. Âm = quá hạn, 0 = đến hạn, dương = còn hạn.

### 1.5 product.template (inherit)
File: `models/product_template.py`

| Field | Type | Ghi chú |
|---|---|---|
| is_storable | Boolean | Mặc định True, cho phép theo dõi tồn kho |

---

## 2. Views & UI

### 2.1 Menu
File: `views/stock_menu_custom_views.xml`

- Menu gốc: **Trường học** (parent: stock.menu_stock_root, seq 80)
  - Trường học → action_dtp_school
  - Lớp học → action_dtp_school_class
  - Môn học → action_dtp_school_subject
- Ẩn các menu gốc không dùng: menu_stock_procurement, menu_action_inventory_tree, menu_procurement_compute

### 2.2 Trường học (res.partner)
File: `views/school_management_views.xml`

- **Search**: lọc theo name, school_type, region; group by loại trường, khu vực
- **List**: hiển thị name, school_type, address, district, province, region
- **Form**: 2 group (thông tin cơ bản + địa chỉ), notebook:
  - Tab "Nhân viên kinh doanh": sale_user_ids (many2many_tags)
  - Tab "Lớp học": class_ids (editable list grade + class_count, sub-form có subject_ids)

### 2.3 Khối lớp (res.partner.class)
File: `views/school_management_views.xml`

- **Search**: lọc theo grade, class_count, school_id, region; group by trường, khối lớp, khu vực
- **List**: chỉ xem (create/edit/delete = false)
- **Form**: chỉ xem, hiển thị grade, class_count, school_id, region + tab môn học (subject_ids many2many_tags)

### 2.4 Môn học (res.partner.subject)
File: `views/school_management_views.xml`

- **Search**: lọc theo name, class_ids; group by khối lớp, môn học
- **List**: cho phép tạo/sửa/xóa, hiển thị name, class_ids (widget many2many_tags), supply_product_ids (many2many_tags)
- **Form**: cho phép tạo/sửa/xóa, các field name, class_ids (widget many2many_tags), supply_product_ids

### 2.5 Phiếu giao hàng (stock.picking) — Inherit views
File: `views/school_management_views.xml`

**Form (inherit stock.view_picking_form):**
- Ẩn các button không dùng: action_detailed_operations, do_print_picking, 207
- partner_id domain: chỉ hiển thị trường học khi picking outgoing
- Thêm field subject_id (sau partner_id), domain lọc theo trường được chọn: `[('class_ids.school_id', '=', partner_id)]`
- Thay field origin bằng: return_deadline_date (nhập tay) + return_days_left (readonly, có màu cảnh báo)

**List (inherit stock.vpicktree):**
- Thay field origin bằng: return_deadline_date + return_days_left (với decoration màu đỏ/vàng/xanh)

**Search (inherit stock.view_picking_internal_search):**
- Thêm field return_deadline_date
- Thêm 2 filter: "Return Overdue" (quá hạn) và "Return Due Today" (đến hạn hôm nay)

### 2.6 Phiếu phế phẩm (stock.scrap) — Inherit views
File: `views/school_management_views.xml`

**Form (inherit stock.stock_scrap_form_view):**
- Ẩn field `should_replenish` (invisible="1") để tinh giản giao diện cho quy trình xử lý của trường học.

---

## 3. Dashboard (OWL)

### 3.1 Backend controller
File: `controllers/dashboard.py`

Endpoint: `/dtp_school_inventory/dashboard/data` (jsonrpc, auth=user)
- Nhận `filters`: { region, school_type, school_id }
- Trả về: kpis, pickings_by_state, top_products, schools_overview, pickings_trend, filter_options

### 3.2 OWL Components
File: `static/src/dashboard/`

| Component | File | Chức năng |
|---|---|---|
| DtpInventoryDashboard | dashboard.js / dashboard.xml / dashboard.scss | Component gốc, load data, điều phối filter và visual |
| FilterPanel | filter_panel/ | Bộ lọc kiểu PowerBI: khu vực, loại trường, trường học |
| KpiCard | kpi_card/ | Thẻ chỉ số: trường học, lớp học, phiếu chờ, phiếu xong, phiếu nhập, phiếu trễ |
| DonutChart | donut_chart/ | Biểu đồ tròn: phiếu kho theo trạng thái |
| HorizontalBarChart | horizontal_bar_chart/ | Biểu đồ ngang: top 8 sản phẩm đã xuất |
| SchoolsTable | schools_table/ | Bảng tổng quan trường học: lớp, môn, phiếu chờ, phiếu xong |
| TrendLineChart | trend_line_chart/ | Biểu đồ đường: xu hướng phiếu hoàn thành 6 tháng |

### 3.3 Dashboard Action
File: `views/dashboard_action.xml`

- Đăng ký ir.actions.client với tag `dtp_school_inventory_dashboard`
- Override menuitem `stock.stock_picking_type_menu` (Overview) để mở dashboard thay vì kanban mặc định
- Click vào KPI card sẽ nhảy đến list stock.picking/res.partner với domain tương ứng

---

## 4. Dữ liệu mẫu
File: `data/school_sample_data.xml`

- 8 sản phẩm dụng cụ học tập (product.product)
- 3 trường học (res.partner): Mầm non Hoa Sen, Tiểu học Sông Tiên, THCS Hương Giang
- 9 khối lớp (res.partner.class): A0, A1, A2, 1, 3, 5, 6, 8, 9
- 5 môn học (res.partner.subject): Làm quen chữ cái, Toán, Mỹ thuật, Tiếng Việt - Ngữ văn, Tự nhiên - Khoa học
  - Mỗi môn liên kết nhiều khối lớp và nhiều trường

---

## 5. Cấu trúc file

```
dtp_addons/dtp_school_inventory/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── dashboard.py
├── data/
│   └── school_sample_data.xml
├── docs/
│   └── README.md
├── models/
│   ├── __init__.py
│   ├── product_template.py
│   ├── school_management.py
│   └── stock_picking.py
├── security/
│   └── ir.model.access.csv
├── static/src/dashboard/
│   ├── dashboard.js / .xml / .scss
│   ├── donut_chart/
│   ├── filter_panel/
│   ├── horizontal_bar_chart/
│   ├── kpi_card/
│   ├── schools_table/
│   └── trend_line_chart/
└── views/
    ├── dashboard_action.xml
    ├── school_management_views.xml
    └── stock_menu_custom_views.xml
```
