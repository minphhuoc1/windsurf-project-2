# 📧 AI Email Generator

**Ứng dụng tạo email tự động bằng AI - Hỗ trợ tiếng Việt & Tiếng Anh**

Sử dụng Google Gemini API để tạo email chuyên nghiệp, phù hợp với từng loại email và đối tượng khác nhau.

---

## ✨ **Tính năng chính**

### 🎯 **Loại email hỗ trợ**
- ✅ **Sales outreach** - Chào hàng, giới thiệu sản phẩm
- ✅ **Customer reply** - Phản hồi khách hàng, xin lỗi
- ✅ **Leave request** - Xin nghỉ phép
- ✅ **Status update** - Cập nhật tiến độ dự án
- ✅ **Event invitation** - Mời sự kiện, webinar
- ✅ **Feedback request** - Yêu cầu phản hồi
- ✅ **Partnership inquiry** - Hợp tác kinh doanh
- ✅ **Generic business email** - Email chung

### 🌍 **Hỗ trợ ngôn ngữ**
- 🇻🇳 Tiếng Việt
- 🇬🇧 Tiếng Anh

### 👥 **Tùy chỉnh đối tượng**
- **B2B** - Tone formal, xưng hô "Quý vị"
- **B2C** - Tone thân thiện, xưng hô "Anh/chị"

### 🎨 **Tùy chỉnh nâng cao**
- **Tone**: Formal, Friendly, Apologetic, Neutral
- **Độ dài**: Ngắn, Trung bình, Dài
- **Phong cách**: Chuyên nghiệp, Ngắn gọn, Thân thiện
- **CTA Template**: Đặt lịch demo, Phản hồi xác nhận, Điền form, Tải tài liệu
- **Variable interpolation**: Order ID, Delivery date, Hotline, Meeting link

### 📥 **Tính năng khác**
- ✅ Chọn tiêu đề từ gợi ý hoặc tự nhập
- ✅ Download email dưới dạng `.txt`
- ✅ Hiển thị debug info (prompt, response)
- ✅ Xóa placeholder tự động
- ✅ Xóa pleasantries không cần thiết
- ✅ Điều chỉnh tone theo đối tượng

---

## 🚀 **Cách sử dụng**

### **Cách 1: Chạy local**

**Yêu cầu:**
- Python 3.10+
- Google Gemini API key

**Cài đặt:**
```bash
# Clone repo
git clone https://github.com/minphhuoc1/windsurf-project-2.git
cd windsurf-project-2

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Chạy app
streamlit run app.py
```

**Truy cập:** http://localhost:8501

---

### **Cách 2: Dùng online (Streamlit Cloud)**

Truy cập: **https://email-ai-generate.streamlit.app/** 

---

## 📋 **Cấu trúc file**

```
windsurf-project-2/
├── app.py                      # Main Streamlit app
├── test_gemini.py              # Test script
├── requirements.txt            # Dependencies
├── .env                        # API key (local only)
├── .gitignore                  # Git ignore rules
├── TEST_SCENARIOS_NO_PRESET.md # Test scenarios
└── README.md                   # This file
```

---

## 🔧 **Cài đặt & Cấu hình**

### **1. Tạo Google Gemini API key**

1. Truy cập: https://aistudio.google.com/app/apikeys
2. Click **"Create API Key"**
3. Copy key → lưu vào `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### **2. Cài đặt dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `streamlit==1.28.1` - Web framework
- `google-generativeai==0.3.0` - Gemini API client
- `python-dotenv==1.0.0` - Load environment variables

### **3. Chạy app**

```bash
streamlit run app.py
```

---

## 📊 **Ví dụ sử dụng**

### **Kịch bản 1: Sales outreach**
```
Purpose: Sales outreach
Tone: Friendly
Language: Vietnamese
Recipient: Nguyễn Văn A
Audience: B2B
Details: Giới thiệu phần mềm quản lý bán hàng
CTA: Đặt lịch demo
Meeting Link: https://calendly.com/demo
```

**Kết quả:**
- Subject: "Giải pháp quản lý bán hàng hiệu quả cho doanh nghiệp của bạn"
- Body: Email chuyên nghiệp với CTA rõ ràng + link Calendly

### **Kịch bản 2: Feedback request**
```
Purpose: Feedback request
Tone: Friendly
Language: Vietnamese
Recipient: Anh Minh
Audience: B2C
Details: Yêu cầu phản hồi về dịch vụ
Hotline: 1900-5555
```

**Kết quả:**
- Email thân thiện, yêu cầu phản hồi
- Hotline được thay thế tự động

---

## 🎯 **Các tính năng nâng cao**

### **1. CTA Template**
Chọn loại call-to-action:
- **Đặt lịch demo** - Hẹn lịch trao đổi
- **Phản hồi xác nhận** - Yêu cầu xác nhận
- **Điền form** - Yêu cầu điền biểu mẫu
- **Tải tài liệu** - Chia sẻ tài liệu

### **2. Variable Interpolation**
Thay thế biến tự động:
- `{order_id}` → Order ID
- `{delivery_date}` → Ngày giao hàng
- `{hotline}` → Số hotline
- `{meeting_link}` → Link hẹn lịch/form

### **3. Tone Detection**
- **Formal** - Xin lỗi, cập nhật tiến độ
- **Friendly** - Chào hàng, phản hồi
- **Apologetic** - Xin lỗi khách hàng
- **Neutral** - Email chung

### **4. Audience-specific**
- **B2B** - Xưng hô "Quý vị", tone formal
- **B2C** - Xưng hô "Anh/chị", tone thân thiện

---

## 🧪 **Testing**

### **Chạy test script**
```bash
python test_gemini.py
```

### **Test scenarios**
Xem file `TEST_SCENARIOS_NO_PRESET.md` để test 8 kịch bản khác nhau.

---

## 📈 **Hiệu suất & Giới hạn**

| Tiêu chí | Giá trị |
|---------|--------|
| **Model** | Gemini 2.5 Flash |
| **Thời gian generate** | 2-5 giây |
| **Subject length** | ≤ 70 ký tự |
| **Body length** | ~120 từ (tùy chỉnh) |
| **API quota (free)** | 250 requests/day |

---

## 🔒 **Bảo mật**

- ✅ API key lưu trong `.env` (local only)
- ✅ `.env` không được commit lên Git
- ✅ Streamlit Cloud dùng Secrets (encrypted)
- ✅ Không lưu dữ liệu email trên server

---

## 📝 **Changelog**

### **v1.0 (Current)**
- ✅ 8 loại email
- ✅ 2 ngôn ngữ (Việt, Anh)
- ✅ 2 audience (B2B, B2C)
- ✅ CTA template selector
- ✅ Variable interpolation
- ✅ Tone customization
- ✅ Download email
- ✅ Debug mode

---


## 📞 **Hỗ trợ & Liên hệ**

- **GitHub Issues**: https://github.com/minphhuoc1/windsurf-project-2/issues
- **Email**: [phuocdoan333@gmail.com]

---

## 📄 **License**

MIT License - Tự do sử dụng, sửa đổi, phân phối

---

## 🙏 **Cảm ơn**

- **Google Gemini API** - AI model
- **Streamlit** - Web framework
- **Python** - Programming language

---

## 🎯 **Roadmap (Tương lai)**

- [ ] Hỗ trợ thêm ngôn ngữ (Trung, Nhật, Hàn)
- [ ] Template email tùy chỉnh
- [ ] A/B testing CTA
- [ ] Analytics dashboard
- [ ] Email scheduling
- [ ] Integration với Gmail, Outlook

---

**Phiên bản:** 1.0  
**Cập nhật lần cuối:** November 2025  
**Tác giả:** Phuoc Doan
