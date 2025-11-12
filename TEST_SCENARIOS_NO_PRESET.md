# 🎯 Test Scenarios - Không dùng Preset

Hướng dẫn: Chọn **"Custom"** hoặc **"Other"** ở Preset Selector, sau đó nhập các thông tin dưới đây.

---

## 📧 **Kịch bản 6: Partnership Inquiry (Tiếng Anh, B2B)**

### Cấu hình:
- **Preset**: Custom / Other
- **Purpose**: Partnership inquiry
- **Tone**: Professional
- **Recipient**: Sarah Johnson
- **Audience**: B2B
- **Language**: English
- **Signature**: Best regards, Phuoc Doan
- **Writing Style**: Professional
- **Email Length**: Medium
- **Include CTA**: ✅ Yes
- **CTA Template**: Đặt lịch demo (hoặc tương đương)

### Details (nhập vào):
```
We are a leading software development company specializing in AI solutions. 
We noticed your company's recent expansion into the Southeast Asian market 
and believe our expertise could be valuable for your digital transformation initiatives. 
We'd like to explore potential collaboration opportunities.
```

### Variables:
- Order ID: (để trống)
- Delivery Date: (để trống)
- Hotline: (để trống)
- Meeting Link: https://calendly.com/partnership

### Kỳ vọng:
- ✅ Tone chuyên nghiệp, formal
- ✅ CTA hẹn lịch với link thực tế
- ✅ Không có placeholder
- ✅ Subject ngắn gọn, hấp dẫn

---

## 📧 **Kịch bản 7: Product Feedback Request (Tiếng Việt, B2C)**

### Cấu hình:
- **Preset**: Custom / Other
- **Purpose**: Feedback request
- **Tone**: Friendly
- **Recipient**: Anh Minh
- **Audience**: B2C
- **Language**: Vietnamese
- **Signature**: Trân trọng, Phuoc Doan
- **Writing Style**: Friendly
- **Email Length**: Short
- **Include CTA**: ✅ Yes
- **CTA Template**: Phản hồi xác nhận

### Details (nhập vào):
```
Cảm ơn anh đã sử dụng dịch vụ của chúng tôi trong tháng vừa rồi. 
Chúng tôi rất muốn biết ý kiến của anh về trải nghiệm, 
để chúng tôi có thể cải thiện dịch vụ tốt hơn.
```

### Variables:
- Order ID: (để trống)
- Delivery Date: (để trống)
- Hotline: 1900-5555
- Meeting Link: (để trống)

### Kỳ vọng:
- ✅ Tone thân thiện, không quá trang trọng
- ✅ CTA yêu cầu phản hồi
- ✅ Hotline được nhắc đến
- ✅ Ngắn gọn, dễ đọc

---

## 📧 **Kịch bản 8: Event Invitation (Tiếng Anh, B2B)**

### Cấu hình:
- **Preset**: Custom / Other
- **Purpose**: Event invitation
- **Tone**: Friendly
- **Recipient**: Michael Chen
- **Audience**: B2B
- **Language**: English
- **Signature**: Warm regards, Phuoc Doan
- **Writing Style**: Friendly
- **Email Length**: Medium
- **Include CTA**: ✅ Yes
- **CTA Template**: Đặt lịch demo (hoặc tương đương)

### Details (nhập vào):
```
We're hosting an exclusive webinar on "AI-Driven Business Transformation" 
on November 20th at 2 PM UTC. Industry leaders will share insights on 
how to leverage AI for competitive advantage. We'd love to have you join us.
```

### Variables:
- Order ID: (để trống)
- Delivery Date: (để trống)
- Hotline: (để trống)
- Meeting Link: https://zoom.us/webinar/ai-transformation

### Kỳ vọng:
- ✅ Tone thân thiện nhưng chuyên nghiệp
- ✅ Event details rõ ràng
- ✅ CTA đăng ký với link Zoom
- ✅ Không có placeholder

---

## 📋 **Checklist kiểm tra:**

Sau khi test 3 kịch bản trên, kiểm tra:

- ✅ Subject không bị cắt (giới hạn 70 ký tự)
- ✅ CTA không lặp
- ✅ Link thực tế được sử dụng
- ✅ Không có placeholder `[Link...]`
- ✅ Tone phù hợp với cấu hình
- ✅ Xưng hô đúng (B2B: formal, B2C: friendly)
- ✅ Hotline được thay thế khi có
- ✅ Chữ hoa đúng ở đầu câu CTA
- ✅ Download .txt hoạt động

---

## 💡 Ghi chú:
- Nếu "Custom" không có, thử nhập "Other" hoặc tên tùy ý
- Nếu model không nhận ra purpose, hãy báo để điều chỉnh
- Kiểm tra xem có thêm pleasantries không (nên xóa hết)
