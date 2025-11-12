import os, re, json, textwrap
from typing import Tuple
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai



# ---- Config & setup ----
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.stop()  # Dừng app nếu thiếu key
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"
GENCFG = {"temperature": 0.6, "top_p": 0.9}

# === Preset cấu hình test nhanh ===
PRESETS = {
    "Sales outreach": {
        "purpose": "Sales outreach / Chào hàng",
        "tone": "Friendly",
        "lang": "Vietnamese",
        "style": "Chuyên nghiệp",
        "length": "Trung bình",
        "details": "Giới thiệu phần mềm quản lý bán hàng giúp tiết kiệm thời gian; đề nghị demo 15–20 phút trong tuần tới."
    },
    "Customer reply (Apology)": {
        "purpose": "Customer reply / Phản hồi khách hàng",
        "tone": "Apologetic",
        "lang": "Vietnamese",
        "style": "Ngắn gọn",
        "length": "Ngắn",
        "details": "Xin lỗi khách hàng vì giao hàng trễ 2 ngày; tặng voucher 10% cho lần sau."
    },
    "Status update": {
        "purpose": "Status update / Cập nhật tiến độ",
        "tone": "Formal",
        "lang": "English",
        "style": "Chuyên nghiệp",
        "length": "Trung bình",
        "details": "Milestone 1 done, Milestone 2 in QA, Milestone 3 expected by Friday."
    },
    "Leave request": {
        "purpose": "Leave request / Xin nghỉ phép",
        "tone": "Formal",
        "lang": "Vietnamese",
        "style": "Ngắn gọn",
        "length": "Ngắn",
        "details": "Xin nghỉ 1 ngày Thứ Hai tuần tới vì lý do cá nhân; đã bàn giao công việc."
    },
}

# --- State defaults ---
if "purpose" not in st.session_state:
    st.session_state.purpose  = "Customer reply / Phản hồi khách hàng"
if "tone" not in st.session_state:
    st.session_state.tone     = "Formal"
if "lang" not in st.session_state:
    st.session_state.lang     = "Vietnamese"
if "style" not in st.session_state:
    st.session_state.style    = "Chuyên nghiệp"
if "length" not in st.session_state:
    st.session_state.length   = "Trung bình"
if "details" not in st.session_state:
    st.session_state.details  = ""
if "recipient" not in st.session_state:
    st.session_state.recipient = ""
if "signature" not in st.session_state:
    st.session_state.signature = "Best regards,\nPhuoc Doan"
if "cta_template" not in st.session_state:
    st.session_state.cta_template = "Đặt lịch demo"
if "auto_subject" not in st.session_state:
    st.session_state.auto_subject = False



def is_vi(lang: str) -> bool:
    return str(lang).lower().startswith("vi")

def localize_signature(signature: str, lang: str) -> str:
    sig = (signature or "").strip()
    if not sig:
        return sig
    if is_vi(lang) and sig.lower().startswith("best regards"):
        return sig.replace("Best regards", "Trân trọng")
    if not is_vi(lang) and sig.startswith("Trân trọng"):
        return sig.replace("Trân trọng", "Best regards")
    return sig




def call_gemini(prompt: str, temperature: float = 0.6) -> str:
    model = genai.GenerativeModel(MODEL_NAME, generation_config={"temperature": temperature})
    resp = model.generate_content(prompt)
    return resp.text.strip()

def build_json_prompt(purpose, tone, recipient, details, lang, signature,
                      words=120, require_cta=True, salutation_line="", variables=None):

    cta_rule = "Include a clear call-to-action at the end." if require_cta else "Do not include a call-to-action."
    
    # Xây dựng phần variables info
    var_info = ""
    if variables:
        var_items = []
        if variables.get("order_id"):
            var_items.append(f"- Order ID: {variables['order_id']}")
        if variables.get("delivery_date"):
            var_items.append(f"- Delivery date: {variables['delivery_date']}")
        if variables.get("hotline"):
            var_items.append(f"- Hotline: {variables['hotline']}")
        if variables.get("meeting_link"):
            var_items.append(f"- Meeting/Form link: {variables['meeting_link']}")
        if var_items:
            var_info = "\nAvailable variables:\n" + "\n".join(var_items)
    
    return f"""
You are an assistant that writes concise, professional business emails.
Return STRICT JSON only. No markdown, no explanations, no code fences.

Constraints (non-negotiable):
- Language: {lang}
- Tone: {tone}
- Subject line ≤ 60 characters
- Body around {words} words
- Use the provided recipient if available; otherwise keep it natural
- {cta_rule}
- The body MUST end with the signature below.
- Start the body with this exact salutation line (if non-empty): "{salutation_line}"
- Do NOT use placeholders like [Link...] or [form...]. Use actual values from variables if available.


Context:
- Purpose: {purpose}
- Recipient: {recipient or "N/A"}
- Details: {details or "N/A"}
- Signature: {signature}{var_info}

Return EXACTLY this JSON shape:
{{"subject": "<one line>", "body": "<multi-line email body ending with the signature>"}}
""".strip()



def build_prompt(purpose, tone, recipient, details, lang, signature, words=120, require_cta=True):
    cta_rule = "Include a clear call-to-action at the end." if require_cta else "Do not include a call-to-action."
    return f"""
System instructions (non-negotiable):
- Output in {lang}.
- Professional, polite, concise tone: {tone}.
- Subject line ≤ 60 characters.
- Body around {words} words.
- Use the provided recipient if available; otherwise keep it generic but natural.
- {cta_rule}
- Strictly follow the output schema below.

Context:
- Purpose: {purpose}
- Recipient: {recipient or "N/A"}
- Details: {details or "N/A"}
- Signature (must end the body): {signature}

Output schema (do not add extra text):
Subject: <one line>
Body:
<multiple lines, ready to paste into an email client>
""".strip()


def parse_email(text: str):
    # Cố gắng tách Subject và Body nếu model trả đúng format
    subj_match = re.search(r"^Subject:\s*(.+)", text, flags=re.IGNORECASE|re.MULTILINE)
    body_match = re.search(r"^Body:\s*(.*)$", text, flags=re.IGNORECASE|re.DOTALL|re.MULTILINE)
    subject = subj_match.group(1).strip() if subj_match else "Generated Email"
    body = body_match.group(1).strip() if body_match else text
    return subject, body

def call_gemini_json(prompt: str, temperature: float = 0.6) -> dict:
    cfg = dict(GENCFG)
    cfg["temperature"] = temperature
    model = genai.GenerativeModel(MODEL_NAME, generation_config=cfg)
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    # Thử parse JSON thẳng
    try:
        return json.loads(text)
    except Exception:
        # Fallback: cố gắng trích khối {...} lớn nhất
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = text[start:end+1]
            try:
                return json.loads(snippet)
            except Exception:
                pass
        # Fallback cuối cùng: trả cấu trúc tối thiểu
        return {"subject": "Generated Email", "body": text or "No content"}

def has_cta_in_body(body: str, lang: str) -> bool:
    """Kiểm tra xem body đã có CTA (bất kỳ loại) chưa"""
    t = (body or "").lower()
    if is_vi(lang):
        patterns = [
            # Form CTA
            r"(điền form|điền biểu mẫu|điền vào|biểu mẫu ngắn gọn)",
            # Đặt lịch/Hẹn lịch
            r"(đặt lịch|hẹn lịch|đặt hẹn|trao đổi.*?phút|thời gian phù hợp|cho tôi biết thời gian|lịch trình)",
            # Phản hồi/Xác nhận
            r"(phản hồi email|xác nhận)",
            # Tải tài liệu
            r"(tải tài liệu|tải file|download|xem thêm)",
            # CTA do model sinh ra
            r"(hãy đăng ký|đăng ký tại|đăng ký ngay|liên hệ hotline|liên hệ.*?hotline|vui lòng liên hệ)",
            # Link CTA
            r"(https?://|www\.)",
        ]
    else:
        patterns = [
            r"(fill out|fill in the form|form)",
            r"(schedule|book a call|demo|time that works)",
            r"(reply to|confirm)",
            r"(download|view the|brief deck)",
            # CTA do model sinh ra
            r"(please.*?register|register.*?here|sign up|click.*?link|visit.*?link)",
            # Link CTA
            r"(https?://|www\.)",
        ]
    return any(re.search(p, t, re.IGNORECASE) for p in patterns)

def enforce_rules(subject: str,
                  body: str,
                  signature: str,
                  require_cta: bool = True,
                  purpose: str = None,
                  lang: str = "Vietnamese",
                  audience: str = "B2B",
                  variables: dict | None = None):
    subject = (subject or "Generated Email").strip()
    if len(subject) > 70:
        subject = subject[:67].rstrip() + "..."

    body = (body or "").strip()

    # Gỡ CTA tiếng Anh khi đang viết tiếng Việt
    if is_vi(lang):
        body = re.sub(
            r"\n*Please let me know a suitable time to proceed\.\s*$",
            "",
            body,
            flags=re.IGNORECASE
        )

    # Quy tắc CTA theo loại email
    purpose = (purpose or "").strip()
    purpose_vi = purpose.lower()

    is_apology = "customer reply" in purpose_vi or "phản hồi khách hàng" in purpose_vi
    is_status  = "status update" in purpose_vi or "cập nhật tiến độ" in purpose_vi
    is_leave   = "leave request" in purpose_vi or "xin nghỉ" in purpose_vi
    is_sales = ("sales outreach" in purpose_vi) or ("chào hàng" in purpose_vi)
    is_event = "event invitation" in purpose_vi or "mời sự kiện" in purpose_vi
    is_feedback = "feedback request" in purpose_vi or "yêu cầu phản hồi" in purpose_vi
    is_partnership = "partnership inquiry" in purpose_vi or "hợp tác" in purpose_vi


    # Xử lý CTA dựa trên require_cta và purpose
    if require_cta and not is_leave:  # Leave request không bao giờ có CTA
        if not has_cta_in_body(body, lang):  # tránh chèn nếu body đã có CTA
            tpl = (variables or {}).get("_cta_template")  # nhận template đã chọn
            if is_vi(lang):
                # Xác định xưng hô dựa trên audience
                pronoun = "Quý vị" if audience == "B2B" else "Anh/chị"
                
                if tpl == "Phản hồi xác nhận":
                    body += f"\n\n{pronoun} vui lòng phản hồi email này để xác nhận giúp tôi nhé."
                elif tpl == "Điền form":
                    link = (variables or {}).get("meeting_link") or ""
                    if link:
                        body += f"\n\n{pronoun} có thể điền form tại đây để chúng tôi chuẩn bị nội dung phù hợp: {link}"
                    else:
                        body += f"\n\n{pronoun} có thể điền form để chúng tôi chuẩn bị nội dung phù hợp."
                elif tpl == "Tải tài liệu":
                    link = (variables or {}).get("meeting_link") or ""
                    if link:
                        body += f"\n\n{pronoun} có thể tải tài liệu giới thiệu tại đây: {link}"
                    else:
                        body += f"\n\n{pronoun} có thể tải tài liệu giới thiệu của chúng tôi."
                else:  # "Đặt lịch demo" (mặc định)
                    cta_text = f"{pronoun} có thể cho tôi biết thời gian phù hợp để trao đổi ngắn 15–20 phút không?"
                    # Viết hoa chữ cái đầu nếu cần
                    if cta_text and cta_text[0].islower():
                        cta_text = cta_text[0].upper() + cta_text[1:]
                    body += f"\n\n{cta_text}"
            else:
                if tpl == "Phản hồi xác nhận":
                    body += "\n\nPlease reply to confirm at your convenience."
                elif tpl == "Điền form":
                    link = (variables or {}).get("meeting_link") or ""
                    if link:
                        body += f"\n\nCould you fill out this short form so we can tailor the demo: {link}"
                    else:
                        body += "\n\nCould you fill out this short form so we can tailor the demo?"
                elif tpl == "Tải tài liệu":
                    link = (variables or {}).get("meeting_link") or ""
                    if link:
                        body += f"\n\nYou can download our brief deck here: {link}"
                    else:
                        body += "\n\nYou can download our brief deck."
                else:
                    body += "\n\nWould you be open to a quick 15–20 min demo next week?"
    
    # Thêm hỗ trợ cho Apology/Status (nếu không có CTA)
    if not require_cta or is_leave:
        hotline_val = (variables or {}).get("hotline")
        if (is_apology or is_status) and is_vi(lang):
            if not re.search(r"(liên hệ|hỗ trợ|phản hồi email)", body, re.IGNORECASE):
                contact = f"hotline {hotline_val}" if hotline_val else "hotline"
                body += f"\n\nNếu anh/chị cần hỗ trợ thêm, vui lòng phản hồi email này hoặc liên hệ {contact}."
        elif (is_apology or is_status) and not is_vi(lang):
            if not re.search(r"(support|reach us|reply to this email)", body, re.IGNORECASE):
                body += "\n\nIf you need further support, please reply to this email or contact our hotline."




    # Xóa placeholder [Link biểu mẫu] hoặc [địa chỉ form] nếu link thực tế đã được chèn
    body = re.sub(r"\[.*?link.*?biểu mẫu.*?\]", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\[.*?địa chỉ.*?form.*?\]", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\[Link.*?\]", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\[.*?form.*?\]", "", body, flags=re.IGNORECASE)
    body = re.sub(r"\[.*?\]", "", body)  # Xóa tất cả placeholder còn lại
    
    # Xóa dòng "tại đây: ." (placeholder link trống)
    body = re.sub(r"tại đây:\s*\.\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"tại đây\s*:\s*$", "", body, flags=re.IGNORECASE | re.MULTILINE)
    body = re.sub(r"here:\s*\.\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"here\s*:\s*$", "", body, flags=re.IGNORECASE | re.MULTILINE)
    
    # Xóa dòng trống thừa sau khi xóa placeholder
    body = re.sub(r"\n\n+", "\n\n", body)

    # Bảo toàn chữ ký (tránh lặp)
    # Kiểm tra xem signature đã tồn tại trong body chưa (bất kỳ dạng nào)
    if signature:
        sig_lines = signature.strip().split('\n')
        name = sig_lines[-1].strip() if sig_lines else ""
        # Nếu tên chưa có trong body → thêm signature
        if name and name not in body:
            body += f"\n\n{signature}"
        elif not name and signature not in body:
            body += f"\n\n{signature}"

    return subject, body


def normalize_signature_text(sig: str, lang: str) -> str:
    s = (sig or "").strip()
    if not s:
        return s
    
    if is_vi(lang):
        # Chuyển "Best regards" → "Trân trọng" (giữ tên)
        s = re.sub(r"(?i)^best\s*regards?\s*,?\s*", "Trân trọng, ", s)
        # Nếu không có salutation, thêm "Trân trọng,"
        if not re.match(r"(?i)^(trân\s*trọng|best\s*regards)", s):
            s = "Trân trọng, " + s
    else:
        # Chuyển "Trân trọng" → "Best regards" (giữ tên)
        s = re.sub(r"(?i)^trân\s*trọng\s*,?\s*", "Best regards, ", s)
        # Nếu không có salutation, thêm "Best regards,"
        if not re.match(r"(?i)^(trân\s*trọng|best\s*regards)", s):
            s = "Best regards, " + s
    
    return s

def dedupe_signature(body: str, normalized_sig: str) -> str:
    # xoá chữ ký trùng cuối thư (không phân biệt khoảng trắng/hoa thường)
    if not body or not normalized_sig:
        return body
    
    # Trích tên từ normalized_sig (dòng cuối)
    sig_lines = normalized_sig.strip().split('\n')
    name = sig_lines[-1].strip() if sig_lines else ""
    
    if not name:
        return body
    
    # Pattern 1: Xóa TẤT CẢ signature với salutation + tên (bất kỳ format nào)
    # Bắt: (optional newline) + salutation + (optional newline/space) + name
    # Ví dụ: "Trân trọng,\nTuyen Nguyen" hoặc "Trân trọng, Tuyen Nguyen"
    # Xóa tất cả lần (không chỉ lần cuối)
    pattern1 = rf"(?:\n|\r|\r\n)?\s*(?:Trân\s*trọng|Best\s*regards|Warm\s*regards)\s*,?\s*(?:\n|\r|\r\n)?\s*{re.escape(name)}\s*(?:\n|$)"
    cleaned = re.sub(pattern1, "\n", body, flags=re.IGNORECASE)
    
    # Pattern 2: Xóa signature chỉ có tên (nếu vẫn còn)
    # Xóa tất cả lần tên nếu có nhiều hơn 1 lần
    if name in cleaned:
        count = len(re.findall(re.escape(name), cleaned, re.IGNORECASE))
        if count > 1:
            # Xóa tất cả lần tên (không chỉ lần cuối)
            pattern2 = rf"(?:\n|\r|\r\n)+\s*{re.escape(name)}\s*(?:\n|$)"
            cleaned = re.sub(pattern2, "\n", cleaned, flags=re.IGNORECASE)
    
    # Xóa dòng trống thừa
    cleaned = re.sub(r"\n\n+", "\n", cleaned)
    
    return cleaned


def has_cta_invite(body: str, lang: str) -> bool:
    t = (body or "").lower()
    if is_vi(lang):
        patterns = [
            r"anh/chị.*(có thể|vui lòng).*(hẹn|đặt lịch|trao đổi|demo)",
            r"(hẹn|lịch|trao đổi|demo).*(tuần này|ngày|thời gian|phút)",
            r"(thời gian).*?(phù hợp|thuận tiện)",
        ]
    else:
        patterns = [
            r"would you be (available|open)",
            r"could (we|you) (schedule|set up)",
            r"(does|would) .* (work|suit) for you",
            r"quick (15|20)[–-]?(min| minute) (call|demo)",
        ]
    return any(re.search(p, t, re.IGNORECASE) for p in patterns)



def soften_claims(text: str, lang: str) -> str:
    s = text

    if is_vi(lang):
        # "lên đến 20%" -> "khoảng/đã ghi nhận tới ~20% ở một số trường hợp"
        s = re.sub(r"lên đến\s*(\d+%)", r"đã ghi nhận tới khoảng \1 ở một số trường hợp", s, flags=re.IGNORECASE)
        # "cam kết" -> "nỗ lực/định hướng mang lại"
        s = re.sub(r"\bcam kết\b", "nỗ lực", s, flags=re.IGNORECASE)
        # "giải pháp tiên tiến" -> giữ 1 lần, tránh lặp
        s = re.sub(r"giải pháp tiên tiến(,?\s*)", "giải pháp phù hợp, ", s, flags=re.IGNORECASE)
    else:
        s = re.sub(r"up to\s*(\d+%)", r"we’ve seen up to around \1 in some cases", s, flags=re.IGNORECASE)
        s = re.sub(r"\bguarantee\b", "aim to", s, flags=re.IGNORECASE)
        s = re.sub(r"\bcutting-edge solution\b", "a suitable solution", s, flags=re.IGNORECASE)

    return s



def suggest_subject(purpose: str, lang: str) -> str:
    pv = (purpose or "").lower()
    if is_vi(lang):
        if "sales outreach" in pv or "chào hàng" in pv:
            return "Mời demo giải pháp giúp tối ưu hiệu suất (15–20’)"
        if "customer reply" in pv or "phản hồi khách hàng" in pv:
            return "Thư xin lỗi về đơn hàng và ưu đãi đính kèm"
        if "status update" in pv or "cập nhật tiến độ" in pv:
            return "Cập nhật tiến độ công việc"
        if "leave request" in pv or "xin nghỉ" in pv:
            return "Đề nghị xin nghỉ phép"
        return "Thông tin trao đổi"
    else:
        if "sales outreach" in pv:
            return "Quick 15–20’ demo to improve efficiency"
        if "customer reply" in pv:
            return "Apology for your order – with a voucher"
        if "status update" in pv:
            return "Project status update"
        if "leave request" in pv:
            return "Leave request"
        return "Regarding our discussion"


def trim_pleasantries(body: str, lang: str, purpose: str) -> str:
    if not body or not purpose:
        return body
    s = body

    if is_vi(lang):
        patterns = [
            # Câu mở đầu
            r"^(Kính gửi.*?,\s*)?Hy vọng (anh|chị|bạn|quý.*) có một ngày (tốt lành|hiệu quả)\.?\s*\n",
            r"^(Kính gửi.*?,\s*)?Chúc (anh|chị|bạn|quý.*) một ngày (tốt lành|hiệu quả)\.?\s*\n",
            r"^(Kính gửi.*?,\s*)\s*(Chúng tôi|Tôi|Bên tôi)\s+hy vọng\s+.*?\.\s*\n",
            # Câu ở giữa body - "Hy vọng ... sẽ ..."
            r"\n\s*Hy vọng (anh|chị|bạn|quý.*) sẽ (tiếp tục|ủng hộ|hợp tác|phát triển).*?\.\s*\n",
            # Câu "Chúc ... có ..."
            r"\n\s*Chúc (anh|chị|bạn|quý.*) (có một|một|thật)\s+(ngày|tuần|tháng)\s+(tốt lành|hiệu quả|thành công).*?\.\s*\n",
            # Câu "Hy vọng được ..."
            r"\n\s*Hy vọng được (nghe|nhận|trao đổi).*?\.\s*(?=\n\n|$)",
            # Câu "Hy vọng ..." (generic)
            r"\n\s*Hy vọng.*?\.\s*\n",
        ]
    else:
        patterns = [
            r"^(Dear .*?,\s*)?I hope (this email )?finds you well\.?\s*\n",
            r"^(Dear .*?,\s*)?Hope you are doing well\.?\s*\n",
            r"\n\s*I hope you will (continue|support|work).*?\.\s*\n",
            r"\n\s*Wishing you (a great|a wonderful).*?\.\s*\n",
            r"\n\s*I hope.*?\.\s*\n",
        ]

    for p in patterns:
        s = re.sub(p, "\n", s, flags=re.IGNORECASE)
    
    # Xóa dòng trống thừa
    s = re.sub(r"\n\n+", "\n\n", s)
    return s.strip()



def build_salutation(recipient: str, lang: str) -> str:
    if not recipient or not recipient.strip():
        return ""
    name = recipient.strip()
    if is_vi(lang):
        # VI: không ép “quý công ty” ở đây để tránh cứng nhắc; salutation trung tính
        return f"Kính gửi {name},"
    else:
        return f"Dear {name},"


def tune_audience(body: str, audience: str, lang: str) -> str:
    if not body:
        return body
    s = body
    if is_vi(lang):
        if audience == "B2B":
            # Nâng mức trang trọng, thêm "quý công ty" nếu phù hợp
            s = re.sub(r"\banh/chị\b", "anh/chị", s, flags=re.IGNORECASE)  # giữ nguyên
            # Khi có “doanh nghiệp bạn/anh”, đổi thành “quý công ty”
            s = re.sub(r"\b(doanh nghiệp|công ty)\s+(anh|bạn)\b", "quý công ty", s, flags=re.IGNORECASE)
        else:  # B2C
            # Hạ bớt những cụm quá trang trọng
            s = re.sub(r"\bquý\s*công\s*ty\b", "anh/chị", s, flags=re.IGNORECASE)
            s = re.sub(r"\bquý\s*đơn vị\b", "anh/chị", s, flags=re.IGNORECASE)
    else:
        # English: B2B nhẹ tính formal; B2C nhẹ friendly
        if audience == "B2B":
            s = re.sub(r"\byou\b", "your team", s, flags=re.IGNORECASE)
        else:
            s = re.sub(r"\byour team\b", "you", s, flags=re.IGNORECASE)
    return s


def interpolate_variables(text: str, variables: dict) -> str:
    if not text:
        return text
    s = text
    for k, v in variables.items():
        s = s.replace("{{" + k + "}}", v or "")
    return s

def subject_variants(base: str, purpose: str, lang: str) -> list:
    base = (base or "").strip()
    cand = []
    if is_vi(lang):
        if "sales outreach" in purpose.lower() or "chào hàng" in purpose.lower():
            cand += ["Mời demo giải pháp (15–20’)", "Giới thiệu giải pháp tối ưu hiệu suất", "Hẹn trao đổi nhanh về nhu cầu"]
        elif "customer reply" in purpose.lower() or "phản hồi khách hàng" in purpose.lower():
            cand += ["Thành thật xin lỗi về sự chậm trễ đơn hàng", "Cập nhật đơn hàng & ưu đãi"]
        elif "status update" in purpose.lower() or "cập nhật tiến độ" in purpose.lower():
            cand += ["Cập nhật tiến độ dự án", "Tình trạng các mốc công việc"]
        elif "leave request" in purpose.lower() or "xin nghỉ" in purpose.lower():
            cand += ["Đề nghị xin nghỉ phép", "Xin phép nghỉ 1 ngày"]
        else:
            cand += ["Thông tin trao đổi", "Trao đổi nhanh"]
    else:
        if "sales outreach" in purpose.lower():
            cand += ["Quick 15–20’ demo request", "Intro to our solution", "Brief chat about your needs"]
        elif "customer reply" in purpose.lower():
            cand += ["Sincere apology for the delay", "Order update with a voucher"]
        elif "status update" in purpose.lower():
            cand += ["Project status update", "Milestone progress update"]
        elif "leave request" in purpose.lower():
            cand += ["Leave request", "Requesting one day off"]
        else:
            cand += ["Regarding our discussion", "Quick follow-up"]

    if base and base.lower() not in {"subject", "generated email"}:
        cand = [base] + cand

    uniq = []
    for x in cand:
        x = x.strip()
        if not x:
            continue
        if len(x) > 60:
            x = x[:57].rstrip() + "..."
        if x not in uniq:
            uniq.append(x)
    return uniq[:5]





# ---- Streamlit UI ----
st.set_page_config(page_title="AI Email Generator", page_icon="📧", layout="centered")
st.title("📧 AI Email Generator (Gemini)")

with st.sidebar:

    preset_name = st.selectbox("🎯 Chọn kịch bản mẫu (optional)", ["None"] + list(PRESETS.keys()), key="preset_name")
    audience = st.selectbox("Đối tượng (Audience)", ["B2B", "B2C"], key="audience")
    st.markdown("**Biến (optional) để chèn vào Details/body:**")
    v_order_id      = st.text_input("{{order_id}}", key="var_order_id")
    v_delivery_date = st.text_input("{{delivery_date}}", key="var_delivery_date")
    v_hotline       = st.text_input("{{hotline}}", value="1900 xxxx", key="var_hotline")
    v_meeting_link  = st.text_input("{{meeting_link}}", key="var_meeting_link")
    


    if preset_name != "None":
        p = PRESETS[preset_name]
        # chỉ apply khi chọn preset mới (tránh vòng lặp rerun)
        if st.session_state.get("last_preset") != preset_name:
            st.session_state.purpose   = p["purpose"]
            st.session_state.tone      = p["tone"]
            st.session_state.lang      = p["lang"]
            st.session_state.style     = p["style"]
            st.session_state.length    = p["length"]
            st.session_state.details   = p["details"]
            st.session_state.last_preset = preset_name
            st.rerun()

    if st.session_state.get("last_preset") and st.session_state.last_preset != "None":
        st.info(f"Preset đã load: {st.session_state.last_preset}")


    st.subheader("Settings")
    tone = st.selectbox("Tone (tông giọng)", ["Formal", "Friendly", "Apologetic", "Neutral"], key="tone")
    lang = st.selectbox("Language / Ngôn ngữ", ["English", "Vietnamese"], key="lang")
    signature = st.text_input("Signature / Chữ ký", key="signature")
    # chuẩn hoá chữ ký theo ngôn ngữ (ghi lại vào state)
    style = st.selectbox("Phong cách viết", ["Ngắn gọn", "Chuyên nghiệp", "Thân thiện"], key="style")
    length = st.radio("Độ dài email", ["Ngắn", "Trung bình", "Chi tiết"], key="length")

    words = {"Ngắn": 80, "Trung bình": 120, "Chi tiết": 160}[st.session_state.length]

        # Điều chỉnh temperature theo tone
    tone_temp_map = {"Formal": 0.4, "Friendly": 0.7, "Apologetic": 0.5, "Neutral": 0.6}
    temperature = tone_temp_map.get(st.session_state.tone, 0.6)





st.markdown("Nhập thông tin bên dưới để tạo email.")

col1, col2 = st.columns(2)
with col1:
    purpose = st.selectbox("Loại email (Purpose)", [
        "Sales outreach / Chào hàng",
        "Customer reply / Phản hồi khách hàng",
        "Leave request / Xin nghỉ phép",
        "Status update / Cập nhật tiến độ",
        "Event invitation / Mời sự kiện",
        "Feedback request / Yêu cầu phản hồi",
        "Partnership inquiry / Hợp tác",
        "Generic business email / Chung"
    ], key="purpose")

    recipient = st.text_input("Người nhận (Recipient) - optional", key="recipient")

is_sales = ("sales" in st.session_state.purpose.lower()) or ("chào hàng" in st.session_state.purpose.lower())

# Luôn hiển thị CTA toggle (cho phép user bật/tắt CTA ở bất kỳ loại email nào)
default_cta = True if is_sales else False
require_cta = st.checkbox("Include call-to-action (CTA)", value=default_cta, key="require_cta")

# CTA templates (chỉ khi CTA đang bật)
if st.session_state.get("require_cta", False):
    st.selectbox(
        "CTA template",
        ["Đặt lịch demo", "Phản hồi xác nhận", "Điền form", "Tải tài liệu"],
        key="cta_template"
    )




auto_subject = st.checkbox("🔄 Tự chọn tiêu đề (ẩn hộp chọn)", value=st.session_state.auto_subject, key="auto_subject")

details = st.text_area("Nội dung/Chi tiết thêm (Details) – càng cụ thể kết quả càng tốt",
                       value=st.session_state.details, key="details")


gen_btn = st.button("Generate Email")

if gen_btn:
    # Validation: kiểm tra Details không trống
    if not st.session_state.details or not st.session_state.details.strip():
        st.error("⚠️ Vui lòng nhập nội dung chi tiết (Details) trước khi generate!")
    else:
        with st.spinner("Generating..."):
            salutation_line = build_salutation(st.session_state.recipient, st.session_state.lang)

            # Cho phép user bật/tắt CTA ở bất kỳ loại email nào
            # Nếu user bật CTA, enforce_rules sẽ quyết định có thêm CTA hay không dựa trên purpose
            effective_require_cta = st.session_state.get("require_cta", False)

            # --- interpolate variables for details ---
            # Chỉ thêm variables có giá trị (không trống)
            vars_map = {}
            if st.session_state.var_order_id and st.session_state.var_order_id.strip():
                vars_map["order_id"] = st.session_state.var_order_id.strip()
            if st.session_state.var_delivery_date and st.session_state.var_delivery_date.strip():
                vars_map["delivery_date"] = st.session_state.var_delivery_date.strip()
            if st.session_state.var_hotline and st.session_state.var_hotline.strip():
                vars_map["hotline"] = st.session_state.var_hotline.strip()
            if st.session_state.var_meeting_link and st.session_state.var_meeting_link.strip():
                vars_map["meeting_link"] = st.session_state.var_meeting_link.strip()
            vars_map["_cta_template"] = st.session_state.get("cta_template")
            details_filled = interpolate_variables(st.session_state.details, vars_map)
            
            # Normalize signature TRƯỚC khi truyền vào prompt (tránh lặp)
            normalized_sig = normalize_signature_text(st.session_state.signature, st.session_state.lang)
            
            prompt = build_json_prompt(
                st.session_state.purpose, st.session_state.tone,
                st.session_state.recipient, details_filled,
                st.session_state.lang, normalized_sig,
                words=words, require_cta=effective_require_cta,
                salutation_line=salutation_line,
                variables=vars_map  # Truyền variables để model biết link thực tế
            )

            # GỌI MODEL NGAY TRONG SPINNER
            data = call_gemini_json(prompt, temperature=temperature)

            subject_raw = data.get("subject", "Generated Email")
            if (not subject_raw) or (subject_raw.strip().lower() in {"generated email", "subject"}) or (len(subject_raw.strip()) < 5):
                subject_raw = suggest_subject(purpose, lang)

            body_raw = data.get("body", "")

            # Làm sạch body trước khi enforce
            body_raw = trim_pleasantries(body_raw, lang, purpose)
            # signature đã normalize ở trên, chỉ cần dedupe
            body_raw = dedupe_signature(body_raw, normalized_sig)
            body_raw = tune_audience(body_raw, st.session_state.audience, st.session_state.lang)


            subject, body = enforce_rules(
                subject_raw, body_raw, normalized_sig,
                require_cta=effective_require_cta,
                purpose=purpose,
                lang=lang,
                audience=st.session_state.audience,
                variables=vars_map  
            )
            body = soften_claims(body, lang)

        # Render UI (ngoài spinner)
        st.success("Generated successfully!")
        
        # Subject picker - chỉ hiển thị nếu auto_subject = False
        if not st.session_state.auto_subject:
            choices = subject_variants(subject, st.session_state.purpose, st.session_state.lang)
            picked = st.radio("Chọn tiêu đề", choices, index=0, key="subject_pick")
            if picked and picked != subject:
                subject = picked
        
        st.markdown(f"**Subject:** {subject}")
        if "Generated Email" in subject_raw or subject_raw.lower().strip() in {"generated email", "subject"}:
            st.caption("⚠️ Subject được sinh tự động từ gợi ý fallback vì model không trả về.")
        st.text_area("Body", value=body, height=260)
        st.caption(f"Subject length: {len(subject)} chars | Body words: {len(body.split())}")
        st.download_button(
            "Download .txt",
            data=(f"Subject: {subject}\n\n{body}").encode("utf-8"),
            file_name="generated_email.txt",
            mime="text/plain"
        )
        with st.expander("Debug (prompt & raw response)"):
            st.code(prompt, language="markdown")
            st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")



st.caption("Built with Streamlit + Gemini · Demo for internal email/proposal generation.")
