# DTP School Inventory Management

## Muc tieu
Module them schema quan ly truong hoc trong app Inventory.

## Pham vi schema
- Truong hoc gom 3 loai: Mam non, Cap 1, Cap 2.
- Khoi lop: A0, A1, A2, 1-9.
- Moi truong co dia chi, quan/huyen, tinh/thanh, khu vuc (HCM, Mekong, Hue).
- Moi truong (res.partner) co 1 hoac nhieu sale phu trach qua lien ket den model co san `res.users`.
- Moi khoi lop trong truong luu so luong lop (khong luu ten lop rieng).
- Moi khoi lop co 1 hoac nhieu mon hoc.
- Moi mon hoc lien ket dung cu hoc tap qua `product.product` (module stock).

## UI
- Menu duoc gan vao Inventory menu (`stock.menu_stock_root`).
- Tao day du list/form/menu/action cho:
  - Truong hoc
  - Lop hoc
  - Mon hoc
- Nhap lieu tap trung trong form truong hoc (notebook Sales, Classes, Subjects).
- Cac view ngoai form truong hoc de che do chi xem (khong tao/sua/xoa).

## Group By
- Ho tro group theo truong, mon hoc va khu vuc o cac search view lien quan.

## Ghi chu
- Module hien tai chi tap trung thiet ke schema va giao dien.
- Chua bao gom logic nghiep vu, constraint nang cao, hoac automation.
